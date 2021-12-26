from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User
import posts.tests.constants_methods as cst
from yatube.settings import PAGINATOR_NUM


class PaginatorViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.new_client = Client()
        cls.newuser = User.objects.create_user(
            username=cst.NEW_USER_DICT['username'])
        # cls.new_client.force_login(cls.newuser)

        groups_for_bulk = []

        for group in cst.GROUPS_DICT.values():
            groups_for_bulk.append(Group(
                slug=group,
                title=group,
                description=group))

        Group.objects.bulk_create(groups_for_bulk)

        cls.group1 = Group.objects.get(id=list(cst.GROUPS_DICT.keys())[0])
        cls.group2 = Group.objects.get(id=list(cst.GROUPS_DICT.keys())[1])

        posts_for_bulk = []

        for i in range(1, len(cst.POSTS_STR) + 1):
            if i <= cst.SCND_GROUP_EDGE:
                posts_for_bulk.append(Post(
                    author=cls.newuser,
                    text=cst.POSTS_STR[i - 1],
                    id=i,
                    group=cls.group1))
            else:
                posts_for_bulk.append(Post(
                    author=cls.newuser,
                    text=cst.POSTS_STR[i - 1],
                    id=i,
                    group=cls.group2))

        Post.objects.bulk_create(posts_for_bulk)

    @classmethod
    def first_page_volume(cls, total_volume):
        """Определение объема первой страницы."""
        if total_volume - PAGINATOR_NUM >= 0:
            return PAGINATOR_NUM
        return total_volume

    @classmethod
    def second_page_volume(cls, total_volume):
        """Определение объема второй страницы."""
        if total_volume <= PAGINATOR_NUM:
            return 0
        if total_volume < 2 * PAGINATOR_NUM:
            return total_volume - PAGINATOR_NUM
        return PAGINATOR_NUM

    def test_first_page_of_index(self):
        """Количество постов на первой странице главной страницы."""
        response = self.new_client.get(cst.REVERSE_DICT['index'][0])
        total_count = Post.objects.count()
        self.assertEqual(len(
            response.context['page_obj']),
            PaginatorViewsTest.first_page_volume(total_count))

    def test_second_page_of_index(self):
        """Количество постов на второй странице главной страницы."""
        response = self.new_client.get(
            cst.REVERSE_DICT['index'][0] + page_str(2))
        total_count = Post.objects.count()
        self.assertEqual(len(
            response.context['page_obj']),
            PaginatorViewsTest.second_page_volume(total_count))

    def test_group_paginator_first_page(self):
        """Количество постов на первой странице первой группы."""
        response = self.new_client.get(cst.REVERSE_DICT['group1'][0])
        group = Group.objects.get(slug=cst.GROUPS_DICT[1])
        total_count = Post.objects.filter(group=group).count()
        self.assertEqual(len(
            response.context['page_obj']),
            PaginatorViewsTest.first_page_volume(total_count))

    def test_group_paginator_second_page(self):
        """Количество постов на второй странице первой группы."""
        response = self.new_client.get(
            cst.REVERSE_DICT['group1'][0] + page_str(2))
        group = Group.objects.get(slug=cst.GROUPS_DICT[1])
        total_count = Post.objects.filter(group=group).count()
        self.assertEqual(len(
            response.context['page_obj']),
            PaginatorViewsTest.second_page_volume(total_count))

    def test_profile_paginator_first_page(self):
        """Количество постов на первой странице профиля."""
        response = self.new_client.get(cst.REVERSE_DICT['profile'][0])
        total_count = Post.objects.filter(author=self.newuser).count()
        self.assertEqual(len(
            response.context['page_obj']),
            PaginatorViewsTest.first_page_volume(total_count))

    def test_profile_paginator_second_page(self):
        """Количество постов на второй странице профиля."""
        response = self.new_client.get(
            cst.REVERSE_DICT['profile'][0] + page_str(2))
        total_count = Post.objects.filter(author=self.newuser).count()
        self.assertEqual(len(
            response.context['page_obj']),
            PaginatorViewsTest.second_page_volume(total_count))


class TemplatesViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.new_client = Client()
        cls.newuser = User.objects.create_user(
            username=cst.NEW_USER_DICT['username'])
        cls.new_client.force_login(cls.newuser)

        Group.objects.create(
            slug=cst.GROUPS_DICT[1],
            title=cst.GROUPS_DICT[1],
            description=cst.GROUPS_DICT[1])

        Post.objects.create(
            author=cls.newuser,
            text=cst.NEW_POST_TEXTS[0],
            id=1,
            group=Group.objects.get(slug=cst.GROUPS_DICT[1]))

    def test_correct_templates_for_pages(self):
        """Корректный выбор шаблонов."""
        list_to_check = list(cst.REVERSE_DICT.keys())
        list_to_check.remove('group2')
        for keyword in list_to_check:
            reverse_name = cst.REVERSE_DICT[keyword][0]
            with self.subTest(reverse_name=reverse_name):
                response = TemplatesViewsTest.new_client.get(reverse_name)
                self.assertTemplateUsed(response, cst.REVERSE_DICT[keyword][1])


class ContextViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client_authorized = Client()
        cls.newuser = User.objects.create_user(
            username=cst.NEW_USER_DICT['username'])
        cls.client_authorized.force_login(cls.newuser)
        cls.client_nonauthorized = Client()

        groups_for_bulk = []

        for group in cst.GROUPS_DICT.values():
            groups_for_bulk.append(Group(
                slug=group,
                title=group,
                description=group))

        Group.objects.bulk_create(groups_for_bulk)

        cls.group1 = Group.objects.get(id=1)
        cls.group2 = Group.objects.get(id=2)

        cls.post_data = {
            'author': cls.newuser,
            'text': cst.NEW_POST_TEXTS[0],
            'id': 1,
            'group': cls.group1
        }

        cls.post = Post.objects.create(
            author=cls.post_data['author'],
            text=cls.post_data['text'],
            id=cls.post_data['id'],
            group=cls.post_data['group']
        )

    # def assert_context_machine(self, object, dict):
    # fields = cst.FIELDS_TO_ASSERT_POST
    # for field in fields:
    # with self.subTest(field=field):
    # self.assertEqual(getattr(object, field), dict[field])
    # self.assertEqual(object.pub_date.date(), dt.datetime.now().date())

    def test_context_of_many_posts_pages_premade(self):
        """Проверка контекста на страницах нескольких постов
           без создания дополнительного поста."""
        dict = ContextViewsTest.post_data
        for page in cst.PREMADE_POST_PAGES:
            reverse_name = cst.REVERSE_DICT[page][0]
            with self.subTest(reverse_name=reverse_name):
                response = ContextViewsTest.client_authorized.get(reverse_name)
                object = response.context['page_obj'][0]
                cst.assert_context_machine(ContextViewsTest(), object, dict)

    def test_context_for_post_page_premade(self):
        """Проверка контекста на странице поста."""
        dict = ContextViewsTest.post_data
        response = ContextViewsTest.client_authorized.get(
            cst.REVERSE_DICT['post'][0])
        object = response.context['post']
        cst.assert_context_machine(ContextViewsTest(), object, dict)

    def test_context_for_post_editing_page(self):
        """Проверка контекста при редактировании поста."""
        dict = ContextViewsTest.post_data
        response = self.client_authorized.get(cst.REVERSE_DICT['edit'][0])
        actual_text = response.context.get('form').instance.text
        self.assertEqual(actual_text, dict['text'])

    def test_context_and_volume_when_post_appears(self):
        """Проверка контекста и изменения объема страниц
           при добавлении нового поста."""
        form_data = {
            # Пост присваиваем второй группе
            'group': ContextViewsTest.group2.id,
            'text': cst.NEW_POST_TEXTS[1],
            # 'author': ContextViewsTest.newuser.id,
            'id': 2
        }

        index_count = Post.objects.count()
        group1_count = Post.objects.filter(
            group=ContextViewsTest.group1).count()
        group2_count = Post.objects.filter(
            group=ContextViewsTest.group2).count()
        profile_count = Post.objects.filter(
            author=ContextViewsTest.newuser).count()

        # публикуем новый пост
        ContextViewsTest.client_authorized.post(
            cst.REVERSE_DICT['create'][0],
            data=form_data,
            follow=True
        )

        count_dict = {
            'index': [index_count, Post.objects.count()],
            'group2': [group2_count, Post.objects.filter(
                group=ContextViewsTest.group1).count()],
            'profile': [profile_count, Post.objects.filter(
                author=ContextViewsTest.newuser).count()],
        }

        # На всех страницах с несколькими постами, кроме группы 1,
        # количество постов увеличилось на 1
        for keyword in count_dict.keys():
            with self.subTest(keyword=keyword):
                self.assertEqual(
                    count_dict[keyword][0] + 1,
                    count_dict[keyword][1])
        # В группе 1 количество постов не изменилось
        self.assertEqual(group1_count, Post.objects.filter(
            group=ContextViewsTest.group1).count())

        # Проверяем контекст, который был передан
        # страницам, на которых количество постов увеличилось на 1

        form_data['group'] = ContextViewsTest.group2
        form_data['author'] = ContextViewsTest.newuser
        dict = form_data
        list_to_check = list(cst.REVERSE_DICT.keys())

        for page in cst.PAGES_WO_NEW_POST:
            list_to_check.remove(page)

        for page in list_to_check:
            reverse_name = cst.REVERSE_DICT[page][0]
            with self.subTest(page=page):
                response = ContextViewsTest.client_authorized.get(reverse_name)
                object = response.context['page_obj'][0]
                cst.assert_context_machine(ContextViewsTest(), object, dict)

        # print(form_data['id'])
        # Смотрим, что у этого поста есть своя страница,
        # где мы его непременно найдём
        response = ContextViewsTest.client_authorized.get(
            reverse('posts:post_detail', kwargs={'post_id': form_data['id']}))
        self.assertEqual(response.status_code, 200)
        object = response.context['post']
        cst.assert_context_machine(ContextViewsTest(), object, dict)
        # просто попробовал получить имя вьюшки
        self.assertEqual(response.resolver_match.func.__name__, 'post_detail')


class FormFieldsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.new_client = Client()
        cls.newuser = User.objects.create_user(
            username=cst.NEW_USER_DICT['username'])
        cls.new_client.force_login(cls.newuser)

        Group.objects.create(
            slug=cst.GROUPS_DICT[1],
            title=cst.GROUPS_DICT[1],
            description=cst.GROUPS_DICT[1])

        Post.objects.create(
            author=cls.newuser,
            text=cst.NEW_POST_TEXTS[0],
            id=1,
            group=Group.objects.get(slug=cst.GROUPS_DICT[1]))

        cls.FIELDS_DICT = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

    def field_processor(self, response, dict):
        """Метод проверки полей формы."""
        for value, expected in dict.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_context_for_form_editing_post(self):
        """Форма редактирования поста."""
        response = self.new_client.get(cst.REVERSE_DICT['edit'][0])
        form_fields = FormFieldsTest.FIELDS_DICT
        self.field_processor(response, form_fields)

    def test_context_for_form_creating_post(self):
        """Форма для создания поста."""
        response = self.new_client.get(cst.REVERSE_DICT['create'][0])
        form_fields = FormFieldsTest.FIELDS_DICT
        self.field_processor(response, form_fields)


def page_str(num):
    return f'?page={num}'
