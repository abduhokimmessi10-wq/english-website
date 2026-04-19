from django.core.management.base import BaseCommand
from speaking.models import Question
from speaking.questions_data import QUESTIONS


class Command(BaseCommand):
    help = 'Load all IELTS speaking questions into the database'

    def handle(self, *args, **kwargs):
        Question.objects.all().delete()
        created = 0
        for q in QUESTIONS:
            Question.objects.create(**q)
            created += 1
        self.stdout.write(self.style.SUCCESS(f'Successfully loaded {created} questions'))
