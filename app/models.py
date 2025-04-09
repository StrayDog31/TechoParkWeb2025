from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f'Profile of {self.user.username}'


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
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)
    rating = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    is_solved = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)

    objects = QuestionManager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def update_rating(self):
        likes = self.question_likes.count()
        dislikes = self.question_dislikes.count()
        self.rating = likes - dislikes
        self.save()

    def get_answers_count(self):
        return self.answers.count()


class Answer(models.Model):
    text = models.TextField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    is_solution = models.BooleanField(default=False)
    rating = models.IntegerField(default=0)

    class Meta:
        ordering = ['-is_solution', '-rating', 'created_at']

    def __str__(self):
        return f'Answer to "{self.question.title}"'

    def update_rating(self):
        likes = self.answer_likes.count()
        dislikes = self.answer_dislikes.count()
        self.rating = likes - dislikes
        self.save()

    def mark_as_solution(self):
        self.question.answers.update(is_solution=False)
        self.is_solution = True
        self.save()
        self.question.is_solved = True
        self.question.save()


class BaseVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class QuestionLike(BaseVote):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='question_likes')

    class Meta:
        unique_together = ('user', 'question')


class AnswerLike(BaseVote):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='answer_likes')

    class Meta:
        unique_together = ('user', 'answer')


class QuestionDislike(BaseVote):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='question_dislikes')

    class Meta:
        unique_together = ('user', 'question')


class AnswerDislike(BaseVote):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='answer_dislikes')

    class Meta:
        unique_together = ('user', 'answer')