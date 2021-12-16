from django.urls import path
from django.contrib.auth import views as view

from .views import PasswordChanges, PasswordReset
from . import views

app_name = 'users'

# чтобы избежать длинных строк
TEMPLATES_DICT = {
    'login': 'users/login.html',
    'logout': 'users/logged_out.html',
    'password_change': 'users/password_change_form.html',
    'password_reset': 'users/password_reset_form.html',
    'mail_sent': 'users/password_reset_done.html',
    'token_used': 'users/password_reset_confirm.html',
    'reset_fin': 'users/password_reset_complete.html',
}


urlpatterns = [
    path(
        'login/',
        view.LoginView.as_view(
            template_name=TEMPLATES_DICT['login']),
        name='login'
    ),
    path(
        'logout/',
        view.LogoutView.as_view(
            template_name=TEMPLATES_DICT['logout']),
        name='logout'
    ),
    path(
        'password_change/',
        PasswordChanges.as_view(
            template_name=TEMPLATES_DICT['password_change']),
        name='password_change_form'
    ),
    path(
        'password_change/done/',
        views.password_changed,
        name='password_change_done'
    ),
    path(
        'password_reset/',
        PasswordReset.as_view(
            template_name=TEMPLATES_DICT['password_reset']),
        name='password_reset_form'
    ),
    path(
        'password_reset/done/',
        view.PasswordResetDoneView.as_view(
            template_name=TEMPLATES_DICT['mail_sent']),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        view.PasswordResetConfirmView.as_view(
            template_name=TEMPLATES_DICT['token_used']),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        view.PasswordResetCompleteView.as_view(
            template_name=TEMPLATES_DICT['reset_fin']),
        name='password_reset_complete'
    ),
    path(
        'signup/',
        views.SignUp.as_view(),
        name='signup'
    ),
]
