import json
import random
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import Question, PracticeSession, Answer
from .ai_feedback import get_feedback, get_band_label, get_band_color


def _session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def _err(msg, status=400):
    return JsonResponse({'error': msg}, status=status)


def _ok(data=None, status=200):
    payload = {'ok': True}
    if data:
        payload.update(data)
    return JsonResponse(payload, status=status)


# ─── pages ───────────────────────────────────────────────────────────────────

def index(request):
    sk = _session_key(request)
    total_sessions = PracticeSession.objects.filter(session_key=sk, completed=True).count()
    recent = PracticeSession.objects.filter(session_key=sk, completed=True).first()
    best_score = None
    if recent and recent.total_score:
        best_score = recent.total_score
    return render(request, 'index.html', {
        'total_sessions': total_sessions,
        'best_score': best_score,
    })


def practice_page(request, part):
    if part not in [1, 2, 3]:
        from django.http import Http404
        raise Http404
    sk = _session_key(request)
    questions = list(Question.objects.filter(part=part, is_active=True).values(
        'id', 'part', 'text', 'topic', 'order'
    ))
    return render(request, 'practice.html', {
        'part': part,
        'questions_json': json.dumps(questions),
        'questions_count': len(questions),
    })


def results_page(request, session_id):
    sk = _session_key(request)
    try:
        session = PracticeSession.objects.get(id=session_id, session_key=sk)
    except PracticeSession.DoesNotExist:
        from django.http import Http404
        raise Http404
    answers = session.answers.select_related('question').all()
    return render(request, 'results.html', {
        'session': session,
        'answers': answers,
        'get_band_label': get_band_label,
        'get_band_color': get_band_color,
    })


# ─── api: questions ───────────────────────────────────────────────────────────

@require_http_methods(['GET'])
def api_questions(request, part):
    questions = Question.objects.filter(part=part, is_active=True)
    return JsonResponse({'questions': [q.to_dict() for q in questions]})


# ─── api: sessions ────────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(['POST'])
def api_session_start(request):
    sk = _session_key(request)
    try:
        body = json.loads(request.body)
    except Exception:
        return _err('invalid json')
    part = body.get('part', 1)
    session = PracticeSession.objects.create(session_key=sk)
    return JsonResponse({'session_id': session.id}, status=201)


@csrf_exempt
@require_http_methods(['POST'])
def api_session_complete(request, session_id):
    sk = _session_key(request)
    try:
        session = PracticeSession.objects.get(id=session_id, session_key=sk)
    except PracticeSession.DoesNotExist:
        return _err('session not found', 404)

    answers = session.answers.filter(feedback_overall__isnull=False)
    if answers.exists():
        avg = sum(a.feedback_overall for a in answers) / answers.count()
        session.total_score = round(avg * 2) / 2
    session.completed = True
    session.save()
    return _ok({'session_id': session.id, 'total_score': session.total_score})


# ─── api: submit answer + get feedback ────────────────────────────────────────

@csrf_exempt
@require_http_methods(['POST'])
def api_submit_answer(request):
    sk = _session_key(request)
    try:
        body = json.loads(request.body)
    except Exception:
        return _err('invalid json')

    session_id = body.get('session_id')
    question_id = body.get('question_id')
    answer_text = body.get('answer_text', '').strip()

    if not answer_text:
        return _err('answer cannot be empty')
    if len(answer_text) < 10:
        return _err('answer is too short — please give a full response')

    try:
        session = PracticeSession.objects.get(id=session_id, session_key=sk)
        question = Question.objects.get(id=question_id)
    except (PracticeSession.DoesNotExist, Question.DoesNotExist):
        return _err('session or question not found', 404)

    answer, created = Answer.objects.get_or_create(
        session=session,
        question=question,
        defaults={'answer_text': answer_text}
    )
    if not created:
        answer.answer_text = answer_text
        answer.save()

    fb = get_feedback(question.text, question.part, answer_text)

    answer.feedback_fluency = fb['fluency']
    answer.feedback_vocabulary = fb['vocabulary']
    answer.feedback_grammar = fb['grammar']
    answer.feedback_pronunciation = fb['pronunciation']
    answer.feedback_overall = fb['overall']
    answer.feedback_text = fb['feedback_text']
    answer.feedback_strengths = fb['strengths']
    answer.feedback_improvements = fb['improvements']
    answer.model_answer = fb['model_answer']
    answer.save()

    return JsonResponse({
        'answer_id': answer.id,
        'feedback': {
            'fluency': fb['fluency'],
            'vocabulary': fb['vocabulary'],
            'grammar': fb['grammar'],
            'pronunciation': fb['pronunciation'],
            'overall': fb['overall'],
            'band_label': get_band_label(fb['overall']),
            'band_color': get_band_color(fb['overall']),
            'feedback_text': fb['feedback_text'],
            'strengths': fb['strengths'],
            'improvements': fb['improvements'],
            'model_answer': fb['model_answer'],
        }
    }, status=201)


# ─── api: history ─────────────────────────────────────────────────────────────

@require_http_methods(['GET'])
def api_history(request):
    sk = _session_key(request)
    sessions = PracticeSession.objects.filter(session_key=sk, completed=True)[:10]
    data = []
    for s in sessions:
        data.append({
            'id': s.id,
            'started_at': s.started_at.isoformat(),
            'total_score': s.total_score,
            'answers_count': s.answers.count(),
        })
    return JsonResponse({'sessions': data})
