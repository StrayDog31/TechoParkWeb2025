from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User
from app.models import *


class Command(BaseCommand):
    help = 'Очищает все тестовые данные, сохраняя пользователей-администраторов'

    @transaction.atomic
    def handle(self, *args, **options):
        admins = list(User.objects.filter(is_superuser=True).values_list('id', flat=True))

        models = [
            AnswerDislike, AnswerLike,
            QuestionDislike, QuestionLike,
            Answer, Question,
            Tag, Profile
        ]

        for model in models:
            self.stdout.write(f"Удаление {model.__name__}...")
            model.objects.all().delete()
        User.objects.exclude(id__in=admins).delete()

        self.stdout.write(self.style.SUCCESS("База данных успешно очищена!"))