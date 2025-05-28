from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User
from app.models import *


class Command(BaseCommand):
    help = 'Очищает все тестовые данные, сохраняя пользователей-администраторов'

    @transaction.atomic
    def handle(self, *args, **options):
<<<<<<< HEAD
        admins = list(User.objects.filter(is_superuser=True).values_list('id', flat=True))

=======
        # Сохраняем администраторов
        admins = list(User.objects.filter(is_superuser=True).values_list('id', flat=True))

        # Удаление данных в правильном порядке (чтобы избежать ошибок ForeignKey)
>>>>>>> 6182a2fc9cdbccc42e7d88b34e4061195c23250c
        models = [
            AnswerDislike, AnswerLike,
            QuestionDislike, QuestionLike,
            Answer, Question,
            Tag, Profile
        ]

        for model in models:
            self.stdout.write(f"Удаление {model.__name__}...")
            model.objects.all().delete()
<<<<<<< HEAD
=======

        # Удаляем всех пользователей, кроме админов
>>>>>>> 6182a2fc9cdbccc42e7d88b34e4061195c23250c
        User.objects.exclude(id__in=admins).delete()

        self.stdout.write(self.style.SUCCESS("База данных успешно очищена!"))