from django.db import models
from django.utils import timezone


class Question(models.Model):
    PART_CHOICES = [(1, 'Part 1'), (2, 'Part 2'), (3, 'Part 3')]

    part = models.IntegerField(choices=PART_CHOICES)
    text = models.TextField()
    topic = models.CharField(max_length=100, blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['part', 'order']

    def __str__(self):
        return f"Part {self.part} Q{self.order}: {self.text[:60]}"

    def to_dict(self):
        return {
            'id': self.id,
            'part': self.part,
            'text': self.text,
            'topic': self.topic,
            'order': self.order,
        }


class PracticeSession(models.Model):
    session_key = models.CharField(max_length=64, db_index=True)
    started_at = models.DateTimeField(default=timezone.now)
    completed = models.BooleanField(default=False)
    total_score = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"Session {self.id} — {self.session_key[:8]}"


class Answer(models.Model):
    session = models.ForeignKey(PracticeSession, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    # AI feedback fields
    feedback_fluency = models.FloatField(null=True, blank=True)
    feedback_vocabulary = models.FloatField(null=True, blank=True)
    feedback_grammar = models.FloatField(null=True, blank=True)
    feedback_pronunciation = models.FloatField(null=True, blank=True)
    feedback_overall = models.FloatField(null=True, blank=True)
    feedback_text = models.TextField(blank=True)
    feedback_strengths = models.TextField(blank=True)
    feedback_improvements = models.TextField(blank=True)
    model_answer = models.TextField(blank=True)

    class Meta:
        ordering = ['submitted_at']

    def __str__(self):
        return f"Answer for Q{self.question_id} in Session {self.session_id}"

    def to_dict(self):
        return {
            'id': self.id,
            'question_id': self.question_id,
            'question_text': self.question.text,
            'question_part': self.question.part,
            'answer_text': self.answer_text,
            'submitted_at': self.submitted_at.isoformat(),
            'feedback': {
                'fluency': self.feedback_fluency,
                'vocabulary': self.feedback_vocabulary,
                'grammar': self.feedback_grammar,
                'pronunciation': self.feedback_pronunciation,
                'overall': self.feedback_overall,
                'text': self.feedback_text,
                'strengths': self.feedback_strengths,
                'improvements': self.feedback_improvements,
                'model_answer': self.model_answer,
            } if self.feedback_overall else None,
        }
