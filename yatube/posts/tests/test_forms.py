import datetime as dt
from http import HTTPStatus
import shutil
import tempfile

import posts.tests.constants_methods as cst
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.new_client = Client()
        cls.newuser = User.objects.create_user(
            username=cst.NEW_USER_DICT['username'], id=1)
        cls.new_client.force_login(cls.newuser)

        cls.form = PostForm()

        cls.post_data = {
            'text': cst.NEW_POST_TEXTS[0],
            'id': 1
        }

        cls.post_edit = {
            'text': cst.NEW_POST_TEXTS[1]
        }

        Group.objects.create(
            slug=cst.GROUPS_DICT[2],
            title=cst.GROUPS_DICT[2],
            description=cst.GROUPS_DICT[2])

        cls.group2 = Group.objects.get(slug=cst.GROUPS_DICT[2])

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_form_create_edit(self):
        """Поведение при отправке формы создания нового поста
           и редактирования существующего."""

        previous_count = Post.objects.count()

        FormTest.new_client.post(
            cst.REVERSE_DICT['create'][0],
            data=FormTest.post_data,
            follow=True)

        # Проверяем, что создана новая запись
        self.assertEqual(Post.objects.count(), previous_count + 1)
        # Проверяем, что это именно она
        self.assertTrue(
            Post.objects.filter(
                text=FormTest.post_data['text'],
                id=FormTest.post_data['id'],
                author=FormTest.newuser).exists()
        )

        # обращаемся к ней, чтобы отредактировать
        posts_count = Post.objects.count()

        response = FormTest.new_client.get(cst.REVERSE_DICT['edit'][0])
        self.assertEqual(response.status_code, HTTPStatus.OK)

        response = FormTest.new_client.post(
            cst.REVERSE_DICT['edit'][0],
            data=FormTest.post_edit)

        # проверяем, что после отправки
        # формы количество постов не поменялось

        self.assertEqual(Post.objects.count(), posts_count)

        response = FormTest.new_client.get(cst.REVERSE_DICT['post'][0])
        object = response.context['post']
        self.assertEqual(object.text, FormTest.post_edit['text'])

    def test_post_new_post_with_image(self):
        """Поведение при отправке нового поста с изображением."""
        posts_count = Post.objects.count()

        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cst.SMALL_GIF,
            content_type='image/gif'
        )

        form_data = {
            'text': cst.NEW_POST_TEXTS[2],
            'image': uploaded,
            'group': FormTest.group2.id,
        }
        FormTest.new_client.post(
            cst.REVERSE_DICT['create'][0],
            data=form_data,
            follow=True
        )

        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)

        # Готовим список страниц для проверки наличия
        # поста с изображением small.gif

        reverses = list(cst.REVERSE_DICT.keys())
        for key in cst.PAGES_WO_NEW_POST:
            reverses.remove(key)

        # Проверяем наличие поста с изображением
        # small.gif на нужных страницах

        image_sh_be = getattr(form_data['image'], 'name')
        post = Post.objects.get(text=form_data['text'])
        app_name = post.__class__._meta.app_label
        post = Post.objects.get(
            text=form_data['text'],
            image=f'{app_name}/{image_sh_be}',
            group=form_data['group'],
            author=FormTest.newuser,
            pub_date__date=dt.datetime.now().date())

        for reverse_name in reverses:
            with self.subTest(reverse_name=reverse_name):
                response = FormTest.new_client.get(
                    cst.REVERSE_DICT[reverse_name][0])
                object = response.context['page_obj']
                self.assertIn(post, object)

        # далее отловим этот пост и переходим на его страницу
        response = FormTest.new_client.get(
            reverse('posts:post_detail', kwargs={'post_id': post.id}))
        form_data['author'] = FormTest.newuser
        form_data['group'] = FormTest.group2
        object_post = response.context['post']
        cst.assert_context_machine(FormTest(), object_post, form_data)
        self.assertEqual(str(object_post.image).split('/')[1], image_sh_be)

    def test_post_existing_post_with_image(self):

        uploaded_2 = SimpleUploadedFile(
            name='small_2.gif',
            content=cst.SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'text': cst.NEW_POST_TEXTS[3],
            'group': FormTest.group2.id}

        # создаём пост без картинки
        FormTest.new_client.post(
            cst.REVERSE_DICT['create'][0],
            data=form_data,
            follow=True)

        # смотрим, что этот пост на всех страницах без картинки
        reverses = list(cst.REVERSE_DICT.keys())
        for key in cst.PAGES_WO_NEW_POST:
            reverses.remove(key)

        for page in reverses:
            with self.subTest(page=page):
                response = FormTest.new_client.get(cst.REVERSE_DICT[page][0])
                page_obj = response.context['page_obj']
                for item in page_obj:
                    if item.text == form_data['text']:
                        break
                self.assertEqual(item.text, form_data['text'])
                self.assertTrue(str(item.image) == '')

        response = FormTest.new_client.get(
            reverse('posts:post_detail', kwargs={'post_id': item.id}))
        object = response.context['post']
        self.assertEqual(object.text, form_data['text'])
        self.assertTrue(str(object.image) == '')

        # редактируем и добавляем картинку
        form_data['image'] = uploaded_2

        response = FormTest.new_client.post(
            reverse('posts:post_edit', kwargs={'post_id': item.id}),
            data=form_data)
        self.assertEqual(item.text, form_data['text'])

        # смотрим, что этот пост на всех страницах с картинкой

        image_sh_be = getattr(form_data['image'], 'name')
        post = Post.objects.get(text=form_data['text'])
        app_name = post.__class__._meta.app_label
        image_str = f'{app_name}/{image_sh_be}'

        for page in reverses:
            with self.subTest(page=page):
                response = FormTest.new_client.get(cst.REVERSE_DICT[page][0])
                page_obj = response.context['page_obj']
                for item in page_obj:
                    if item.text == form_data['text']:
                        break
                self.assertEqual(item.text, form_data['text'])
                self.assertTrue(str(item.image) == image_str)

        response = FormTest.new_client.get(
            reverse('posts:post_detail', kwargs={'post_id': item.id}))
        object = response.context['post']
        self.assertEqual(object.text, form_data['text'])
        self.assertTrue(str(object.image) == image_str)

    def test_comment_visibility(self):

        Post.objects.create(
            text=cst.NEW_POST_TEXTS[0],
            author=FormTest.newuser,
            group=FormTest.group2,
            id=1)

        self.assertEqual(Comment.objects.count(), 0)
        comment_num = Comment.objects.count()

        comment_data = {'text': 'New comment from TestForm'}

        FormTest.new_client.post(
            reverse(
                'posts:add_comment',
                kwargs=cst.KWARGS_DICT['post']),
            data=comment_data
        )

        response = FormTest.new_client.get(cst.REVERSE_DICT['post'][0])
        # comment = Comment.objects.get(text=comment_data['text'])
        self.assertEqual(Comment.objects.count(), comment_num + 1)
        self.assertContains(response, comment_data['text'])
