import datetime as dt
from typing import Dict, Tuple
from typing_extensions import Literal

from django.test import TestCase
from django.urls import reverse

from ..models import Post

GROUPS_DICT: Dict[int, str] = {1: 'one', 2: 'two'}

NEW_POST_TEXTS: Tuple[str] = (
    'Carpe diem',
    'Absolutely new text',
    'Beautiful day',
    'Here we go again'
)

NEW_USER_DICT: Dict[str, str] = {'username': 'Neo'}

SCND_GROUP_EDGE: str = 11

KWARGS_DICT: Dict[str, str] = {
    'user': NEW_USER_DICT,
    'group1': {'slug': GROUPS_DICT[1]},
    'group2': {'slug': GROUPS_DICT[2]},
    'post': {'post_id': 1}
}

REVERSE_DICT: Dict[str, str] = {
    'index': [reverse(
        'posts:index'),
        'posts/index.html'],
    'group1': [reverse(
        'posts:group_list',
        kwargs=KWARGS_DICT['group1']),
        'posts/group_list.html'],
    'group2': [reverse(
        'posts:group_list',
        kwargs=KWARGS_DICT['group2']),
        'posts/group_list.html'],
    'post': [reverse(
        'posts:post_detail',
        kwargs=KWARGS_DICT['post']),
        'posts/post_detail.html'],
    'create': [reverse(
        'posts:post_create'),
        'posts/create_post.html'],
    'edit': [reverse(
        'posts:post_edit',
        kwargs=KWARGS_DICT['post']),
        'posts/create_post.html'],
    'profile': [reverse(
        'posts:profile',
        kwargs=KWARGS_DICT['user']),
        'posts/profile.html']
}

PAGES_WO_NEW_POST: Tuple[str] = ('group1', 'post', 'create', 'edit')

FIELDS_TO_ASSERT_POST: Tuple[str] = ('author', 'group', 'text')

PREMADE_POST_PAGES: Tuple[str] = ('index', 'profile', 'group1')

POSTS_STR: str = 'abcdefghijklm'

WHOS_AUTHOR: Tuple[str] = ('nonauthor', 'yesauthor')

URLS_ABOUT_DICT: Dict[str, str] = {
    'author': '/about/author/',
    'tech': '/about/tech/'}

UNAUTHORIZED_REDIRECT: Dict[str, str] = {
    REVERSE_DICT['create'][0]: '/auth/login/?next=/create/',
    REVERSE_DICT['edit'][0]:
    f'/auth/login/?next=/posts/{KWARGS_DICT["post"]["post_id"]}/edit/',
}

UNAUTHORIZED_AVAILABLE: Dict[str, str] = {
    REVERSE_DICT['index'][0]: REVERSE_DICT['index'][1],
    REVERSE_DICT['group1'][0]: REVERSE_DICT['group1'][1],
    # здесь профиль должен ссылаться на автора поста - yesauthor
    reverse(
        'posts:profile',
        kwargs={'username': WHOS_AUTHOR[1]}): REVERSE_DICT['profile'][1],
    REVERSE_DICT['post'][0]: REVERSE_DICT['post'][1]}

PAGES_DNT_EXIST: Tuple[str] = (
    '/unexisting_page/',
    '/group/newgroup/',
    '/profile/dead_moroz/',
    '/posts/10000/')

FIELD_VERBOSES: Dict[str, str] = {
    'author': 'Автор поста',
    'group': 'Группа',
    'pub_date': 'Дата публикации',
    'text': 'Текст поста',
}

FIELD_HELP_TEXTS: Dict[str, str] = {
    'author': 'Здесь отображается полное имя автора либо его username',
    'group': 'Группа, к которой будет относиться пост',
    'pub_date': (
        'Дата отображается в формате,',
        ' принятом в Российской Федерации'),
    'text': 'Текст поста не должен быть пустым'}

SMALL_GIF: Literal = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


def assert_context_machine(
        self: TestCase,
        object: Post,
        dict: Dict[str, str]) -> None:
    """Проверяет значения полей поста на соответствие
       значениям в словаре."""
    fields = FIELDS_TO_ASSERT_POST
    for field in fields:
        with self.subTest(field=field):
            self.assertEqual(getattr(object, field), dict[field])
    self.assertEqual(object.pub_date.date(), dt.datetime.now().date())
