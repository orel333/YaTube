from django.views.generic import CreateView
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render

from .forms import CreationForm


class SignUp(CreateView):
    """Создаёт представление страницы регистрации нового пользователя."""
    form_class = CreationForm
    success_url = reverse_lazy('users:login')
    template_name = 'users/signup.html'


class PasswordChanges(PasswordChangeView):
    """Создаёт представление страницы изменения пароля."""
    form_class = PasswordChangeForm
    success_url = reverse_lazy('users:password_change_done')


def password_changed(request):
    """Создаёт представление страницы после изменения пароля."""
    return render(request, 'users/password_change_done.html')


class PasswordReset(PasswordResetView):
    """Создаёт представление страницы сброса пароля."""
    form_class = PasswordResetForm
    success_url = reverse_lazy('users:password_reset_done')


class PasswordResetFinal(PasswordResetConfirmView):
    """Создаёт представление страницы изменения пароля после сброса."""
    form_class = SetPasswordForm
    success_url = reverse_lazy('users:password_reset_complete')
