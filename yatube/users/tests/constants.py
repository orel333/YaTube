from django.urls import reverse

LIST_FOR_REVERSE = [
    'login',
    'signup',
    'password_reset_form',
    'password_change_form',
    'password_change_done',
    'password_reset_done',
    # 'password_reset_confirm',
    'password_reset_complete',
]

REVERSE = {
    'logout': [reverse('users:logout'), 'users/logged_out.html'],
    'index': [reverse('posts:index'), 'posts/index.html']
}


for item in LIST_FOR_REVERSE:
    REVERSE[item] = [
        reverse(f'users:{item}'), f'users/{item}.html'
    ]
