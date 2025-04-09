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

    return render(request, 'main.html', {
        'questions': page.object_list,
        'page_obj': page
    })


def hot(request):
    questions_list = Question.objects.all() \
        .annotate(answers_count=Count('answers')) \
        .order_by('-rating', '-created_at')

    paginator = Paginator(questions_list, 20)
    page_num = request.GET.get('page', 1)
    page = paginator.get_page(page_num)

    return render(request, 'hot.html', {
        'questions': page.object_list,
        'page_obj': page
    })


def single_question(request, question_id):
    question = get_object_or_404(
        Question.objects
        .select_related('author')
        .prefetch_related('tags'),
        pk=question_id
    )

    question.views += 1
    question.save()

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


def add_question(request):
    return render(request, 'create-topic.html')


def create_account(request):
    return render(request, 'create-account.html')


def log_in(request):
    return render(request, 'login.html')


def settings(request):
    return render(request, 'settings.html')