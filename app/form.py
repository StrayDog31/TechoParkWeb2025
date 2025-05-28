from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django import forms
from prompt_toolkit.validation import ValidationError

from .models import Question, Answer, Image, Profile
from django import forms
from .models import Question, Tag
from django.contrib.auth import get_user_model
User = get_user_model()

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control answer-textarea',
                'rows': 5,
                'placeholder': 'Write your answer here...'
            }),
        }
class QuestionForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'tag1, tag2, tag3',
            'data-role': 'tagsinput'
        }),
        help_text='your tags...'
    )

    class Meta:
        model = Question
        fields = ['title', 'text']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial['tags'] = ', '.join(tag.name for tag in self.instance.tags.all())

    def save(self, commit=True, author=None):
        question = super().save(commit=False)

        # Добавляем автора (текущего пользователя)
        if author:
            question.author = author

        if commit:
            question.save()
            question.tags.clear()
            tags = [tag.strip() for tag in self.cleaned_data['tags'].split(',') if tag.strip()]
            for tag_name in tags:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                question.tags.add(tag)

        return question
class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(
                username=username,
                password=password
            )
            if user is None:
                self.add_error('password', 'Wrong username or password')
            elif not user.is_active:
                self.add_error(None, 'This account is disabled.')

        return cleaned_data


class UserForm(forms.ModelForm):
    avatar = forms.ImageField(required=False)
    username = forms.CharField(max_length=100)
    display_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    password = forms.CharField(
        widget=forms.PasswordInput(),
        min_length=4
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(),
        min_length=4
    )
    avatar = forms.ImageField(
        required=False,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])]
    )

    class Meta:
        model = User
        fields = ['avatar', 'username', 'display_name', 'email', 'password']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            if avatar.size > 2*1024*1024:  # 2MB
                raise ValidationError("Avatar image too large ( > 2MB )")
        return avatar

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')

        if User.objects.filter(username=username).exists():
            self.add_error('username', "This username is already taken.")

        if User.objects.filter(email=email).exists():
            self.add_error('email', "This email is already registered.")

        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            self.add_error('confirm_password', 'Passwords must match')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()  # Важно: сначала сохраняем пользователя

            # Затем создаем/обновляем профиль
            profile, created = Profile.objects.get_or_create(user=user)
            if self.cleaned_data['avatar']:
                profile.avatar = self.cleaned_data['avatar']
                profile.save()

        return user


class ProfileSettingsForm(UserChangeForm):
    avatar = forms.ImageField(
        required=False,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])]
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'avatar']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }