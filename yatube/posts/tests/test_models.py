from django.test import Client, TestCase
from django.urls import reverse

from ..models import Comment, Follow, Group, Post, User
import posts.tests.constants_methods as cst
from yatube.settings import TRUNCATE_NUM


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username=cst.NEW_USER_DICT['username'])
        cls.group = Group.objects.create(
            title=cst.GROUPS_DICT[1],
            slug=cst.GROUPS_DICT[1],
            description=cst.GROUPS_DICT[1],
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=cst.NEW_POST_TEXTS[0],
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        group = PostModelTest.group
        expected_post_str = post.text[:TRUNCATE_NUM]
        expected_group_str = group.title
        self.assertEqual(expected_post_str, str(post))
        self.assertEqual(expected_group_str, str(group))

    def test_post_verbose_name(self):
        """Проверяем, что verbose_name полей модели POST
        совпадает с ожидаемым."""
        for field, expected_value in cst.FIELD_VERBOSES.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Post._meta.get_field(field).verbose_name, expected_value
                )

    def test_post_helptexts(self):
        """Проверяем, что help_text полей модели POST
        совпадает с ожидаемым."""
        for field, expected_value in cst.FIELD_HELP_TEXTS.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Post._meta.get_field(field).help_text, expected_value
                )


class CommentModelTest(TestCase):

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

    def test_comments_only_for_authorized(self):
        """Комментировать посты может только авторизованный
           пользователь."""

        comment_data = {'text': 'New comment'}
        comment_num = Comment.objects.count()
        CommentModelTest.client_nonauthorized.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': CommentModelTest.post.id}),
            data=comment_data)
        self.assertEqual(Comment.objects.count(), comment_num)

        CommentModelTest.client_authorized.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': CommentModelTest.post.id}),
            data=comment_data)
        self.assertEqual(Comment.objects.count(), comment_num + 1)


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

        posts_for_bulk = []

        for i in range(cls.WROTE_BY_NONFOLLOWED):
            posts_for_bulk.append(Post(
                text=cls.TEXT_DICT['nonfollowed'],
                author=cls.nonfollowed))

        for i in range(cls.WROTE_BY_FOLLOWED):
            posts_for_bulk.append(Post(
                text=cls.TEXT_DICT['followed'],
                author=cls.followed))

        Post.objects.bulk_create(posts_for_bulk)

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
        """Новый пост автора, выбранного подписчиком,
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

    def test_follow_for_self_is_impossible(self):
        """Подписываться на себя нельзя."""
        follow_num = Follow.objects.count()
        response = FollowViewsTest.authorized_fol.get(
            cst.REVERSE_DICT['index'][0])
        username = response.wsgi_request._cached_user.username
        FollowViewsTest.authorized_fol.get(
            reverse('posts:profile_follow', kwargs={'username': username})
        )
        self.assertEqual(Follow.objects.count(), follow_num)

    def test_double_follow_is_impossible(self):
        """Нельзя подписаться дважды на одного и того же автора."""
        FollowViewsTest.authorized_fol.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': FollowViewsTest.followed.username})
        )
        follow_num = Follow.objects.count()
        FollowViewsTest.authorized_fol.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': FollowViewsTest.followed.username})
        )
        self.assertEqual(Follow.objects.count(), follow_num)
