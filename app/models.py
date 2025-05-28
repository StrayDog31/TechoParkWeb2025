from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(
        upload_to='uploads/avatars',
        blank=True,
        null=True,
        default='avatars/default.png'
    )

    def __str__(self):
        return f"{self.user.username}'s profile"

class Image(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='uploads/')
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT)

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class QuestionManager(models.Manager):
    def new(self):
        return self.order_by('-created_at')

    def best(self):
        return self.order_by('-rating', '-created_at')

    def by_tag(self, tag_name):
        return self.filter(tags__name=tag_name)


class Question(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    tags = models.ManyToManyField(Tag, related_name='questions')
    created_at = models.DateTimeField(default=timezone.now)
    is_solved = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)

    objects = QuestionManager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def rating(self):
        """Вычисляет текущий рейтинг на основе лайков/дизлайков"""
        return self.question_likes.count() - self.question_dislikes.count()

    def get_answers_count(self):
        return self.answers.count()

    def get_user_vote(self, user):
        """
        Возвращает тип голоса пользователя ('like', 'dislike' или None)
        """
        if not user.is_authenticated:
            return None

        if self.question_likes.filter(user=user).exists():
            return 'like'
        if self.question_dislikes.filter(user=user).exists():
            return 'dislike'
        return None

    def update_rating(self):
        """Обновляет рейтинг (альтернатива property)"""
        self.rating = self.question_likes.count() - self.question_dislikes.count()
        self.save(update_fields=['rating'])


class Answer(models.Model):
    text = models.TextField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    is_solution = models.BooleanField(default=False)
    rating = models.IntegerField(default=0)  # Поле в БД

    class Meta:
        ordering = ['-is_solution', '-rating', 'created_at']

    def update_rating(self):
        self.rating = self.answer_likes.count() - self.answer_dislikes.count()
        self.save()

    def __str__(self):
        return f'Answer to "{self.question.title}"'

    def mark_as_solution(self):
        self.question.answers.update(is_solution=False)
        self.is_solution = True
        self.save()
        self.question.is_solved = True
        self.question.save()

    def update_rating(self):
        """Вычисляет рейтинг как разницу между лайками и дизлайками"""
        return self.answer_likes.count() - self.answer_dislikes.count()

    def get_user_vote(self, user):
        """
        Возвращает 'like', 'dislike' или None для указанного пользователя
        """
        if not user.is_authenticated:
            return None

        if self.answer_likes.filter(user=user).exists():
            return 'like'
        if self.answer_dislikes.filter(user=user).exists():
            return 'dislike'
        return None

class BaseVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class QuestionLike(BaseVote):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='question_likes')

    class Meta:
        unique_together = ('user', 'question')

class QuestionDislike(BaseVote):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='question_dislikes')

    class Meta:
        unique_together = ('user', 'question')


class AnswerLike(BaseVote):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='answer_likes')

    class Meta:
        unique_together = ('user', 'answer')
class AnswerDislike(BaseVote):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='answer_dislikes')

    class Meta:
        unique_together = ('user', 'answer')