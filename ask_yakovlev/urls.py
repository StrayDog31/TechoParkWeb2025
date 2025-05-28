"""
URL configuration for ask_yakovlev project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='main'),
    path('hot', views.hot, name='hot'),
    path('question/<int:question_id>/', views.single_question, name='single_question'),
    path('tag/<str:tag_name>/', views.search_tag, name='search_tag'),
    path('ask', views.add_question, name='ask'),
    path('settings', views.settings, name='settings'),
    path('login', views.log_in, name='login'),
    path('register', views.create_account, name='register'),
    path('logout', views.log_out, name='logout'),
    path('question/<int:pk>/vote/<str:vote_type>/', views.question_vote, name='question_vote'),
    path('answer/<int:pk>/vote/<str:vote_type>/', views.answer_vote, name='answer_vote'),
    path('answer/<int:answer_id>/mark_as_solution/', views.mark_as_solution, name='mark_as_solution'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)