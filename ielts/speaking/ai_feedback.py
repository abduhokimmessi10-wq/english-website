import json
import re
from django.conf import settings
from groq import Groq

client = Groq(api_key=settings.GROQ_API_KEY)


def get_feedback(question_text: str, part: int, answer_text: str) -> dict:
    part_context = {
        1: "This is IELTS Speaking Part 1 — short conversational answers about familiar topics.",
        2: "This is IELTS Speaking Part 2 — a 1-2 minute monologue based on a cue card.",
        3: "This is IELTS Speaking Part 3 — extended discussion with abstract/analytical answers.",
    }

    prompt = f"""You are an expert IELTS Speaking examiner. Evaluate this candidate's answer strictly and professionally.

{part_context.get(part, '')}

QUESTION: {question_text}

CANDIDATE'S ANSWER: {answer_text}

Evaluate the answer on four IELTS criteria (score each 1.0–9.0 in 0.5 increments):
1. Fluency & Coherence — how smoothly and logically they speak
2. Lexical Resource — range and accuracy of vocabulary
3. Grammatical Range & Accuracy — sentence structures and grammar
4. Pronunciation — clarity and natural speech patterns (infer from written answer style)

Respond ONLY with valid JSON, no extra text, no markdown:
{{
  "fluency": <score>,
  "vocabulary": <score>,
  "grammar": <score>,
  "pronunciation": <score>,
  "overall": <average of four scores rounded to nearest 0.5>,
  "feedback_text": "<2-3 sentence overall assessment>",
  "strengths": "<2-3 specific strengths with examples from their answer>",
  "improvements": "<2-3 specific areas to improve with concrete suggestions>",
  "model_answer": "<A high-scoring Band 8-9 model answer for this same question, 3-5 sentences>"
}}"""

    try:
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000,
        )
        raw = response.choices[0].message.content.strip()
        raw = re.sub(r'^```json\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)
        data = json.loads(raw)

        scores = [data.get('fluency', 5), data.get('vocabulary', 5),
                  data.get('grammar', 5), data.get('pronunciation', 5)]
        avg = sum(scores) / 4
        overall = round(avg * 2) / 2

        return {
            'fluency': float(data.get('fluency', 5.0)),
            'vocabulary': float(data.get('vocabulary', 5.0)),
            'grammar': float(data.get('grammar', 5.0)),
            'pronunciation': float(data.get('pronunciation', 5.0)),
            'overall': overall,
            'feedback_text': str(data.get('feedback_text', '')),
            'strengths': str(data.get('strengths', '')),
            'improvements': str(data.get('improvements', '')),
            'model_answer': str(data.get('model_answer', '')),
        }
    except (json.JSONDecodeError, KeyError, Exception) as e:
        print(f"GROQ ERROR: {str(e)}")
        return {
            'fluency': 5.0,
            'vocabulary': 5.0,
            'grammar': 5.0,
            'pronunciation': 5.0,
            'overall': 5.0,
            'feedback_text': 'AI feedback could not be generated. Please try again.',
            'strengths': '',
            'improvements': '',
            'model_answer': '',
            'error': str(e),
        }


def get_band_label(score: float) -> str:
    if score >= 8.5: return 'Expert'
    if score >= 7.5: return 'Very Good'
    if score >= 6.5: return 'Good'
    if score >= 5.5: return 'Competent'
    if score >= 4.5: return 'Modest'
    return 'Limited'


def get_band_color(score: float) -> str:
    if score >= 8.0: return '#34d399'
    if score >= 7.0: return '#60a5fa'
    if score >= 6.0: return '#a78bfa'
    if score >= 5.0: return '#fbbf24'
    return '#f87171'
