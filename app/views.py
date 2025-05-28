<<<<<<< HEAD
import os

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from .form import LoginForm, UserForm, QuestionForm, AnswerForm, ProfileSettingsForm
from .models import Question, Answer, Profile, Image, AnswerLike, AnswerDislike, QuestionDislike, QuestionLike
from django.db.models import Count
from django.shortcuts import render, redirect
from django.contrib.auth import login


def paginate(request, objects_list, per_page):
    paginator = Paginator(objects_list, per_page)
    page_num = request.GET.get('page', 1)
    return paginator.get_page(page_num)


from django.db.models import Prefetch, Exists, OuterRef


def index(request):
    if request.user.is_authenticated:
        user_likes = QuestionLike.objects.filter(
            question=OuterRef('pk'),
            user=request.user
        )
        user_dislikes = QuestionDislike.objects.filter(
            question=OuterRef('pk'),
            user=request.user
        )

        questions_list = Question.objects.all() \
            .annotate(answers_count=Count('answers')) \
            .annotate(user_liked=Exists(user_likes)) \
            .annotate(user_disliked=Exists(user_dislikes)) \
            .order_by('-created_at')

        for question in questions_list:
            if question.user_liked:
                question.current_user_vote = 'like'
            elif question.user_disliked:
                question.current_user_vote = 'dislike'
            else:
                question.current_user_vote = None
    else:
        questions_list = Question.objects.all() \
            .annotate(answers_count=Count('answers')) \
            .order_by('-created_at')

        for question in questions_list:
            question.current_user_vote = None

    page = paginate(request, questions_list, 20)
=======
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from .models import Question, Answer
from django.db.models import Count


def index(request):
    questions_list = Question.objects.all() \
        .annotate(answers_count=Count('answers')) \
        .order_by('-created_at')

    paginator = Paginator(questions_list, 20)
    page_num = request.GET.get('page', 1)
    page = paginator.get_page(page_num)

>>>>>>> 6182a2fc9cdbccc42e7d88b34e4061195c23250c
    return render(request, 'main.html', {
        'questions': page.object_list,
        'page_obj': page
    })


def hot(request):
<<<<<<< HEAD
    if request.user.is_authenticated:
        user_likes = QuestionLike.objects.filter(
            question=OuterRef('pk'),
            user=request.user
        )
        user_dislikes = QuestionDislike.objects.filter(
            question=OuterRef('pk'),
            user=request.user
        )

        questions_list = Question.objects.all() \
            .annotate(answers_count=Count('answers')) \
            .annotate(user_liked=Exists(user_likes)) \
            .annotate(user_disliked=Exists(user_dislikes)) \
            .annotate(
            rating_diff=Count('question_likes') - Count('question_dislikes')
        ) \
            .order_by('-rating_diff', '-created_at')

        for question in questions_list:
            if question.user_liked:
                question.current_user_vote = 'like'
            elif question.user_disliked:
                question.current_user_vote = 'dislike'
            else:
                question.current_user_vote = None
    else:
        questions_list = Question.objects.all() \
            .annotate(answers_count=Count('answers')) \
            .annotate(
            rating_diff=Count('question_likes') - Count('question_dislikes')
        ) \
            .order_by('-rating_diff', '-created_at')

        for question in questions_list:
            question.current_user_vote = None

    page = paginate(request, questions_list, 20)
=======
    questions_list = Question.objects.all() \
        .annotate(answers_count=Count('answers')) \
        .order_by('-rating', '-created_at')

    paginator = Paginator(questions_list, 20)
    page_num = request.GET.get('page', 1)
    page = paginator.get_page(page_num)

>>>>>>> 6182a2fc9cdbccc42e7d88b34e4061195c23250c
    return render(request, 'hot.html', {
        'questions': page.object_list,
        'page_obj': page
    })


<<<<<<< HEAD
def search_tag(request, tag_name):
    base_query = Question.objects.filter(tags__name=tag_name) \
        .annotate(answers_count=Count('answers'))

    if request.user.is_authenticated:
        questions_list = base_query \
            .annotate(
            user_liked=Exists(
                QuestionLike.objects.filter(
                    question=OuterRef('pk'),
                    user=request.user
                )
            ),
            user_disliked=Exists(
                QuestionDislike.objects.filter(
                    question=OuterRef('pk'),
                    user=request.user
                )
            ),
            rating_diff=Count('question_likes') - Count('question_dislikes')
        ) \
            .order_by('-rating_diff', '-created_at')

        for question in questions_list:
            if question.user_liked:
                question.current_user_vote = 'like'
            elif question.user_disliked:
                question.current_user_vote = 'dislike'
            else:
                question.current_user_vote = None
    else:
        questions_list = base_query \
            .annotate(
            rating_diff=Count('question_likes') - Count('question_dislikes')
        ) \
            .order_by('-rating_diff', '-created_at')

        for question in questions_list:
            question.current_user_vote = None

    page = paginate(request, questions_list, 20)

    return render(request, 'search_tag.html', {
        'questions': page.object_list,
        'page_obj': page,
        'tag_name': tag_name,
        'request': request
    })


def single_question(request, question_id):
    question = get_object_or_404(
        Question.objects.select_related('author').prefetch_related('tags'),
=======
def single_question(request, question_id):
    question = get_object_or_404(
        Question.objects
        .select_related('author')
        .prefetch_related('tags'),
>>>>>>> 6182a2fc9cdbccc42e7d88b34e4061195c23250c
        pk=question_id
    )

    question.views += 1
    question.save()

<<<<<<< HEAD
    if request.user.is_authenticated:
        answers_list = Answer.objects.filter(question=question) \
            .select_related('author') \
            .annotate(
            user_liked=Exists(
                AnswerLike.objects.filter(
                    answer=OuterRef('pk'),
                    user=request.user
                )
            ),
            user_disliked=Exists(
                AnswerDislike.objects.filter(
                    answer=OuterRef('pk'),
                    user=request.user
                )
            )
        ) \
            .order_by('-is_solution', '-rating', 'created_at')

        for answer in answers_list:
            if answer.user_liked:
                answer.current_user_vote = 'like'
            elif answer.user_disliked:
                answer.current_user_vote = 'dislike'
            else:
                answer.current_user_vote = None
    else:
        answers_list = Answer.objects.filter(question=question) \
            .select_related('author') \
            .order_by('-is_solution', '-rating', 'created_at')

        for answer in answers_list:
            answer.current_user_vote = None

    paginator = Paginator(answers_list, 5)
    page_number = request.GET.get('page')
    answers = paginator.get_page(page_number)

    form = AnswerForm(request.POST or None)
    if request.method == 'POST' and 'submit_answer' in request.POST:
        if request.user.is_authenticated:
            if form.is_valid():
                answer = form.save(commit=False)
                answer.author = request.user
                answer.question = question
                answer.save()
                return redirect('single_question', question_id=question.id)

    return render(request, 'single-question.html', {
        'question': question,
        'answers': answers,
        'form': form,
        'request': request
    })


@login_required(login_url=reverse_lazy('login'))
=======
    answers_list = Answer.objects.filter(question=question) \
        .select_related('author') \
        .order_by('-is_solution', '-rating', 'created_at')

    paginator = Paginator(answers_list, 5)
    page_num = request.GET.get('page', 1)
    page = paginator.get_page(page_num)

    user_votes = {}

    return render(request, 'single-question.html', {
        'question': question,
        'answers': page.object_list,
        'page_obj': page,
        'user_votes': user_votes,
    })


>>>>>>> 6182a2fc9cdbccc42e7d88b34e4061195c23250c
def add_question(request):
    return render(request, 'create-topic.html')


def create_account(request):
<<<<<<< HEAD
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            if 'avatar' in request.FILES:
                profile = user.profile
                profile.avatar = request.FILES['avatar']
                profile.save()
            auth.login(request, user)
            return redirect('main')
    else:
        form = UserForm()

    return render(request, 'create-account.html', {'form': form})


def log_in(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = auth.authenticate(request, **form.cleaned_data)
            auth.login(request, user)
            return redirect('main')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def log_out(request):
    auth.logout(request)
    return redirect(reverse('main'))


@login_required
def add_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(author=request.user)
            return redirect(reverse('main'))
    else:
        form = QuestionForm()

    return render(request, 'create-topic.html', {'form': form})


@login_required
def settings(request):
    if request.method == 'POST':
        form = ProfileSettingsForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()
            profile = user.profile
            old_avatar = profile.avatar

            if 'avatar' in request.FILES:
                if old_avatar:
                    old_avatar.delete(save=False)
                profile.avatar = request.FILES['avatar']
                profile.save()
            elif 'avatar-clear' in request.POST:
                if old_avatar:
                    old_avatar.delete(save=False)
                profile.avatar = None
                profile.save()
            return redirect('settings')
    else:
        form = ProfileSettingsForm(instance=request.user)

    return render(request, 'settings.html', {'form': form})


@require_POST
@login_required
def question_vote(request, pk, vote_type):
    try:
        question = Question.objects.get(pk=pk)
        user = request.user

        if vote_type == 'like':
            QuestionDislike.objects.filter(user=user, question=question).delete()
            like, created = QuestionLike.objects.get_or_create(user=user, question=question)
            if not created:
                like.delete()
        else:
            QuestionLike.objects.filter(user=user, question=question).delete()
            dislike, created = QuestionDislike.objects.get_or_create(user=user, question=question)
            if not created:
                dislike.delete()

        current_vote = question.get_user_vote(user)

        return JsonResponse({
            'rating': question.rating,
            'user_vote': current_vote if current_vote else 'none'
        })

    except Question.DoesNotExist:
        return JsonResponse({'error': 'Question not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_POST
@login_required
def answer_vote(request, pk, vote_type):
    try:
        answer = Answer.objects.get(pk=pk)
        user = request.user

        # Удаляем противоположный голос
        if vote_type == 'like':
            AnswerDislike.objects.filter(user=user, answer=answer).delete()
            like, created = AnswerLike.objects.get_or_create(user=user, answer=answer)
            if not created:
                like.delete()
        else:
            AnswerLike.objects.filter(user=user, answer=answer).delete()
            dislike, created = AnswerDislike.objects.get_or_create(user=user, answer=answer)
            if not created:
                dislike.delete()

        # Пересчитываем рейтинг
        answer.rating = answer.answer_likes.count() - answer.answer_dislikes.count()
        answer.save()

        return JsonResponse({
            'rating': answer.rating,  # Возвращаем актуальный рейтинг
            'user_vote': answer.get_user_vote(user)
        })

    except Answer.DoesNotExist:
        return JsonResponse({'error': 'Answer not found'}, status=404)




@require_POST
@ensure_csrf_cookie
def mark_as_solution(request, answer_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        answer = Answer.objects.get(pk=answer_id)

        if answer.question.author != request.user:
            return JsonResponse({'error': 'Only question author can mark solutions'}, status=403)

        answer.mark_as_solution()

        return JsonResponse({
            'success': True,
            'answer_id': answer.id,
            'question_id': answer.question.id,
            'is_solution': True
        })

    except Answer.DoesNotExist:
        return JsonResponse({'error': 'Answer not found'}, status=404)
=======
    return render(request, 'create-account.html')


def log_in(request):
    return render(request, 'login.html')


def settings(request):
    return render(request, 'settings.html')
>>>>>>> 6182a2fc9cdbccc42e7d88b34e4061195c23250c
