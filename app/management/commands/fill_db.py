from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker
import random
from django.db import transaction, connection
from app.models import Profile, Tag, Question, Answer, QuestionLike, QuestionDislike, AnswerLike, AnswerDislike
from tqdm import tqdm


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int)

    def handle(self, *args, **options):
        ratio = options['ratio']
        fake = Faker()
        Faker.seed(0)
        random.seed(0)

        with connection.cursor() as cursor:
            cursor.execute('SET CONSTRAINTS ALL DEFERRED;')

        with transaction.atomic():
            self.stdout.write("Creating users...")
            batch_size = 5000
            user_count = ratio

            users = User.objects.bulk_create([
                User(
                    username=f'user_{i}',
                    email=f'user_{i}@example.com',
                    password='testpass123'
                )
                for i in tqdm(range(user_count), desc="Users")
            ])

            Profile.objects.bulk_create([
                Profile(user=user) for user in tqdm(users, desc="Profiles")
            ])

            self.stdout.write("Creating tags...")
            tags = Tag.objects.bulk_create([
                Tag(name=f'tag_{i}', slug=f'tag-{i}')
                for i in tqdm(range(ratio), desc="Tags")
            ])

            self.stdout.write("Creating questions...")
            questions = Question.objects.bulk_create([
                Question(
                    title=f"Question {i}",
                    text=fake.text(max_nb_chars=500),
                    author_id=random.choice(users).id,
                    rating=0,
                    is_solved=random.random() > 0.8,
                    views=random.randint(0, 1000)
                )
                for i in tqdm(range(ratio * 10), desc="Questions")
            ], batch_size=batch_size)

            self.stdout.write("Adding tags to questions...")
            question_tags = []
            for question in tqdm(questions, desc="Tagging"):
                selected_tags = random.sample(tags, k=random.randint(1, 5))
                question_tags.extend([
                    Question.tags.through(question_id=question.id, tag_id=tag.id)
                    for tag in selected_tags
                ])
                if len(question_tags) >= 10000:
                    Question.tags.through.objects.bulk_create(question_tags)
                    question_tags = []
            if question_tags:
                Question.tags.through.objects.bulk_create(question_tags)

            self.stdout.write("Creating answers...")
            answers = Answer.objects.bulk_create([
                Answer(
                    text=fake.text(max_nb_chars=300),
                    question_id=random.choice(questions).id,
                    author_id=random.choice(users).id,
                    is_solution=random.random() > 0.95,
                    rating=0
                )
                for _ in tqdm(range(ratio * 100), desc="Answers")
            ], batch_size=batch_size)

            self.stdout.write("Creating votes...")
            vote_count = ratio * 200

            question_votes = []
            for _ in tqdm(range(vote_count // 2), desc="Question votes"):
                q = random.choice(questions)
                u = random.choice(users)
                if random.random() > 0.3:
                    question_votes.append(QuestionLike(question=q, user=u))
                else:
                    question_votes.append(QuestionDislike(question=q, user=u))

                if len(question_votes) >= 10000:
                    QuestionLike.objects.bulk_create(
                        [v for v in question_votes if isinstance(v, QuestionLike)],
                        ignore_conflicts=True
                    )
                    QuestionDislike.objects.bulk_create(
                        [v for v in question_votes if isinstance(v, QuestionDislike)],
                        ignore_conflicts=True
                    )
                    question_votes = []

            if question_votes:
                QuestionLike.objects.bulk_create(
                    [v for v in question_votes if isinstance(v, QuestionLike)],
                    ignore_conflicts=True
                )
                QuestionDislike.objects.bulk_create(
                    [v for v in question_votes if isinstance(v, QuestionDislike)],
                    ignore_conflicts=True
                )

            answer_votes = []
            for _ in tqdm(range(vote_count // 2), desc="Answer votes"):
                a = random.choice(answers)
                u = random.choice(users)
                if random.random() > 0.3:
                    answer_votes.append(AnswerLike(answer=a, user=u))
                else:
                    answer_votes.append(AnswerDislike(answer=a, user=u))

                if len(answer_votes) >= 10000:
                    AnswerLike.objects.bulk_create(
                        [v for v in answer_votes if isinstance(v, AnswerLike)],
                        ignore_conflicts=True
                    )
                    AnswerDislike.objects.bulk_create(
                        [v for v in answer_votes if isinstance(v, AnswerDislike)],
                        ignore_conflicts=True
                    )
                    answer_votes = []

            if answer_votes:
                AnswerLike.objects.bulk_create(
                    [v for v in answer_votes if isinstance(v, AnswerLike)],
                    ignore_conflicts=True
                )
                AnswerDislike.objects.bulk_create(
                    [v for v in answer_votes if isinstance(v, AnswerDislike)],
                    ignore_conflicts=True
                )

            self.stdout.write("Updating ratings...")
            self._update_ratings(Question, 'question')
            self._update_ratings(Answer, 'answer')

        self.stdout.write(self.style.SUCCESS("\nDatabase filled successfully!"))
        self.print_stats()

    def _update_ratings(self, model, prefix):
        with connection.cursor() as cursor:
            if prefix == 'question':
                cursor.execute(f"""
                    UPDATE app_{prefix} SET rating = (
                        SELECT COALESCE((
                            SELECT COUNT(*) FROM app_questionlike 
                            WHERE question_id = app_question.id
                        ), 0) - COALESCE((
                            SELECT COUNT(*) FROM app_questiondislike 
                            WHERE question_id = app_question.id
                        ), 0)
                    )
                """)
            else:  # answer
                cursor.execute(f"""
                    UPDATE app_{prefix} SET rating = (
                        SELECT COALESCE((
                            SELECT COUNT(*) FROM app_answerlike 
                            WHERE answer_id = app_answer.id
                        ), 0) - COALESCE((
                            SELECT COUNT(*) FROM app_answerdislike 
                            WHERE answer_id = app_answer.id
                        ), 0)
                    )
                """)

    def print_stats(self):
        stats = {
            'Users': User.objects.count(),
            'Questions': Question.objects.count(),
            'Answers': Answer.objects.count(),
            'Tags': Tag.objects.count(),
            'Question Likes': QuestionLike.objects.count(),
            'Question Dislikes': QuestionDislike.objects.count(),
            'Answer Likes': AnswerLike.objects.count(),
            'Answer Dislikes': AnswerDislike.objects.count()
        }

        for name, count in stats.items():
            self.stdout.write(f"- {name}: {count:,}")