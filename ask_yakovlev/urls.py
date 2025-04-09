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
from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='main'),
    path('hot', views.hot, name='hot'),
    path('question/<int:question_id>/', views.single_question, name='single_question'),
    path('ask', views.add_question, name='ask'),
    path('settings', views.settings, name='settings'),
    path('login', views.log_in, name='login'),
    path('register', views.create_account, name='register'),
]
