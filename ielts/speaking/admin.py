from django.contrib import admin
from .models import Question, PracticeSession, Answer


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'part', 'order', 'topic', 'text']
    list_filter = ['part', 'is_active']
    ordering = ['part', 'order']


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ['question', 'answer_text', 'feedback_overall', 'submitted_at']


@admin.register(PracticeSession)
class PracticeSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'session_key', 'started_at', 'completed', 'total_score']
    list_filter = ['completed']
    inlines = [AnswerInline]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['id', 'question', 'feedback_overall', 'submitted_at']
    list_filter = ['question__part']
    readonly_fields = ['feedback_text', 'feedback_strengths', 'feedback_improvements', 'model_answer']
