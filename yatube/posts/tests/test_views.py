from django import forms
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post, User
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

    def test_templates_cache_functioning(self):
        """Проверяем работу кэша."""
        cache.clear()
        response_1 = TemplatesViewsTest.new_client.get(
            cst.REVERSE_DICT['index'][0])
        post = Post.objects.get(id=1)
        self.assertEqual(post.text, cst.NEW_POST_TEXTS[0])
        self.assertContains(response_1, post.text)
        post.delete()
        response_2 = TemplatesViewsTest.new_client.get(
            cst.REVERSE_DICT['index'][0])
        self.assertContains(response_2, post.text)
        cache.clear()
        response_3 = TemplatesViewsTest.new_client.get(
            cst.REVERSE_DICT['index'][0])
        self.assertNotContains(response_3, post.text)


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

    def test_comments_only_for_authorized(self):
        """Комментировать посты может только авторизованный
           пользователь."""

        comment_data = {'text': 'New comment'}
        comment_num = Comment.objects.count()
        ContextViewsTest.client_nonauthorized.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': ContextViewsTest.post.id}),
            data=comment_data)
        self.assertEqual(Comment.objects.count(), comment_num)

        ContextViewsTest.client_authorized.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': ContextViewsTest.post.id}),
            data=comment_data)
        self.assertEqual(Comment.objects.count(), comment_num + 1)


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


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.non_authorized = Client()
        cls.authorized_fol_auth = Client()
        cls.authorized_fol = Client()
        cls.authorized_nonfol = Client()
        # авторы: followed и nonfollowed
        # пользователи: follower и nonfollower
        cls.followed = User.objects.create_user(username='followed')
        cls.new_follower = User.objects.create_user(username='follower')
        cls.new_nonfollower = User.objects.create_user(username='nonfollower')
        cls.authorized_fol_auth.force_login(cls.followed)
        cls.authorized_fol.force_login(cls.new_follower)
        cls.authorized_nonfol.force_login(cls.new_nonfollower)
        cls.nonfollowed = User.objects.create_user(username='nonfollowed')

        cls.WROTE_BY_NONFOLLOWED = 10
        cls.WROTE_BY_FOLLOWED = 3

        cls.TEXT_DICT = {
            'followed': 'This post was posted by followed_author',
            'nonfollowed': 'This post was posted by nonfollowed_author'
        }

        for i in range(cls.WROTE_BY_NONFOLLOWED):
            Post.objects.create(
                text=cls.TEXT_DICT['nonfollowed'],
                author=cls.nonfollowed)

        for i in range(cls.WROTE_BY_FOLLOWED):
            Post.objects.create(
                text=cls.TEXT_DICT['followed'],
                author=cls.followed)

        cls.REVERSE_CONST = reverse('posts:follow_index')

    def test_unathorized_user_cant_subscribe(self):
        """Неавторизованный пользователь не может
        подписаться на любимого автора."""
        follow_num = Follow.objects.count()
        FollowViewsTest.non_authorized.get(
            reverse('posts:profile_follow', kwargs={'username': 'followed'}),
        )
        self.assertEqual(Follow.objects.count(), follow_num)

    def test_authorized_user_can_follow_and_unfollow(self):
        """Авторизованный пользователь может подписаться
           на любимого автора и отписаться от нелюбимого."""

        follow_num = Follow.objects.count()
        response_fol0 = FollowViewsTest.authorized_fol.get(
            FollowViewsTest.REVERSE_CONST)
        response_nonfol0 = FollowViewsTest.authorized_nonfol.get(
            FollowViewsTest.REVERSE_CONST)

        self.assertTrue(len(response_fol0.context['page_obj']) == 0)
        self.assertTrue(len(response_nonfol0.context['page_obj']) == 0)
        FollowViewsTest.authorized_fol.get(
            reverse('posts:profile_follow', kwargs={'username': 'followed'}))
        self.assertEqual(Follow.objects.count(), follow_num + 1)
        response_fol1 = FollowViewsTest.authorized_fol.get(
            FollowViewsTest.REVERSE_CONST
        )
        response_nonfol1 = FollowViewsTest.authorized_nonfol.get(
            FollowViewsTest.REVERSE_CONST
        )
        fol1_page_cont = response_fol1.context['page_obj']
        self.assertTrue(
            len(fol1_page_cont) == FollowViewsTest.WROTE_BY_FOLLOWED)
        nonfol1_page_cont = response_nonfol1.context['page_obj']
        self.assertTrue(
            len(nonfol1_page_cont) == 0)

        for item in fol1_page_cont:
            with self.subTest(item=item):
                self.assertEqual(
                    item.text, FollowViewsTest.TEXT_DICT['followed'])

        follow_num = Follow.objects.count()
        FollowViewsTest.authorized_fol.get(
            reverse('posts:profile_unfollow', kwargs={'username': 'followed'})
        )
        self.assertEqual(Follow.objects.count(), follow_num - 1)

        response_fol2 = FollowViewsTest.authorized_fol.get(
            FollowViewsTest.REVERSE_CONST
        )
        response_nonfol2 = FollowViewsTest.authorized_nonfol.get(
            FollowViewsTest.REVERSE_CONST
        )

        self.assertTrue(len(response_fol2.context['page_obj']) == 0)
        self.assertTrue(len(response_nonfol2.context['page_obj']) == 0)

    def test_posts_of_followed_author_appear_at_follow_index_of_follower(self):
        """Новый пост автора, выбранного подписчика,
           появляется только на странице подписчика."""

        FollowViewsTest.authorized_fol.get(
            reverse('posts:profile_follow', kwargs={'username': 'followed'})
        )
        response_fol0 = FollowViewsTest.authorized_fol.get(
            FollowViewsTest.REVERSE_CONST
        )
        response_nonfol0 = FollowViewsTest.authorized_nonfol.get(
            FollowViewsTest.REVERSE_CONST
        )
        posts_num_fol_start = len(response_fol0.context['page_obj'])
        posts_num_nonfol_start = len(response_nonfol0.context['page_obj'])
        self.assertTrue(
            posts_num_fol_start == FollowViewsTest.WROTE_BY_FOLLOWED)
        self.assertTrue(posts_num_nonfol_start == 0)
        NEW_TEXT_OF_FOLLOWED = 'Here I am again with new post'
        FollowViewsTest.authorized_fol_auth.post(
            reverse('posts:post_create'), data={'text': NEW_TEXT_OF_FOLLOWED}
        )
        response_fol1 = FollowViewsTest.authorized_fol.get(
            FollowViewsTest.REVERSE_CONST
        )
        response_nonfol1 = FollowViewsTest.authorized_nonfol.get(
            FollowViewsTest.REVERSE_CONST
        )
        fol_context = response_fol1.context['page_obj']
        posts_num_fol_final = len(fol_context)
        posts_num_nonfol_final = len(response_nonfol1.context['page_obj'])
        self.assertEqual(posts_num_fol_final, posts_num_fol_start + 1)
        self.assertEqual(posts_num_nonfol_start, posts_num_nonfol_final)
        new_post = Post.objects.get(text=NEW_TEXT_OF_FOLLOWED)
        self.assertIn(new_post, fol_context)


def page_str(num):
    return f'?page={num}'
