from django.test import TestCase

from ..models import Group, Post, User
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
