from django.core.cache import cache
from django.test import Client, TestCase

from posts.models import Group, Post, User
import posts.tests.constants_methods as cst

class CacheTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.new_client = Client()
        cls.newuser = User.objects.create_user(
            username=cst.NEW_USER_DICT['username'])
        
        Group.objects.create(
            slug=cst.GROUPS_DICT[1],
            title=cst.GROUPS_DICT[1],
            description=cst.GROUPS_DICT[1])

        Post.objects.create(
            author=cls.newuser,
            text=cst.NEW_POST_TEXTS[0],
            id=1,
            group=Group.objects.get(slug=cst.GROUPS_DICT[1]))
    
    
    def test_templates_cache_functioning(self):
        """Проверяем работу кэша."""
        cache.clear()
        response_1 = CacheTest.new_client.get(
            cst.REVERSE_DICT['index'][0])
        post = Post.objects.get(id=1)
        self.assertEqual(post.text, cst.NEW_POST_TEXTS[0])
        self.assertContains(response_1, post.text)
        post.delete()
        response_2 = CacheTest.new_client.get(
            cst.REVERSE_DICT['index'][0])
        self.assertContains(response_2, post.text)
        cache.clear()
        response_3 = CacheTest.new_client.get(
            cst.REVERSE_DICT['index'][0])
        self.assertNotContains(response_3, post.text)