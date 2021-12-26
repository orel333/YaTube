from http import HTTPStatus

from django.test import Client, TestCase

from posts.models import Group, Post, User
import posts.tests.constants_methods as cst


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        """Главная страница доступна."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    # def test_author(self):
        # """Страница с информацией об авторе доступна."""
        # response = self.guest_client.get(cst.URLS_ABOUT_DICT['author'])
        # self.assertEqual(response.status_code, HTTPStatus.OK)

    # def test_tech(self):
        # """Страница с информацией об использованных технологиях доступна."""
        # response = self.guest_client.get(cst.URLS_ABOUT_DICT['tech'])
        # self.assertEqual(response.status_code, HTTPStatus.OK)


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        """Подготовка фикстур для теста страниц приложения posts."""
        super().setUpClass()
        cls.guest_client = Client()

        cls.nonauthor = User.objects.create_user(username=cst.WHOS_AUTHOR[0])
        cls.authorized_nonauthor = Client()
        cls.authorized_nonauthor.force_login(cls.nonauthor)

        cls.yesauthor = User.objects.create_user(username=cst.WHOS_AUTHOR[1])
        cls.authorized_yesauthor = Client()
        cls.authorized_yesauthor.force_login(cls.yesauthor)

        # now we should create some post by yesauthor

        cls.group_for_post = Group.objects.create(
            slug=cst.GROUPS_DICT[1],
            title=cst.GROUPS_DICT[1],
            description=cst.GROUPS_DICT[1]
        )

        Post.objects.create(
            author=cls.yesauthor,
            text=cst.NEW_POST_TEXTS[0],
            id=1,
            group=cls.group_for_post
        )

    def test_page_exists_for_all(self):
        """Проверка доступности общедоступных страниц
           для всех пользователей."""
        guest_client = PostsURLTests.guest_client
        for address in cst.UNAUTHORIZED_AVAILABLE.keys():
            with self.subTest(address=address):
                response = guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_exists_for_authorized(self):
        """Проверка доступности страницы создания поста
           для авторизованных пользователей."""
        nonauthor = PostsURLTests.authorized_nonauthor
        response = nonauthor.get(cst.REVERSE_DICT['create'][0])
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_right_template_for_all(self):
        """Проверка отображения корректных шаблонов
           общедоступных страниц для всех пользователей."""
        guest_client = PostsURLTests.guest_client
        for address, template in cst.UNAUTHORIZED_AVAILABLE.items():
            with self.subTest(address=address):
                response = guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_right_template_for_authorized(self):
        """Проверка отображения корректного шаблона
           страницы создания поста авторизованным пользователям."""
        nonauthor = PostsURLTests.authorized_nonauthor
        address = cst.REVERSE_DICT['create'][0]
        template = cst.REVERSE_DICT['create'][1]
        response = nonauthor.get(address)
        self.assertTemplateUsed(response, template)

    def test_redirect_for_unathorized(self):
        """Проверка переадресации неавторизованных пользователей
           при попытке доступа к страницам для авторизованных пользователей."""
        guest_client = PostsURLTests.guest_client
        # чтобы уменьшить длину строки 101
        url_dict = cst.UNAUTHORIZED_REDIRECT
        for start_address, end_address in url_dict.items():
            with self.subTest(start_address=start_address):
                response = guest_client.get(start_address, follow=True)
                self.assertRedirects(response, end_address)

    def test_redirect_when_edit_for_nonauthor(self):
        """Проверка переадресации авторизованного пользователя, не являющегося
           автором поста, на страницу соответствующего поста
           при попытке доступа к странице его редактирования."""
        nonauthor = PostsURLTests.authorized_nonauthor

        response = nonauthor.get(cst.REVERSE_DICT['edit'][0], follow=True)
        end_address = cst.REVERSE_DICT['post'][0]
        self.assertRedirects(response, end_address)

    def test_edit_available_for_author(self):
        """Проверка доступности страницы редактирования поста его автору."""
        yesauthor = PostsURLTests.authorized_yesauthor
        response = yesauthor.get(cst.REVERSE_DICT['edit'][0])
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_right_template_for_author(self):
        """Проверка отображения корректного шаблона автору поста при
           доступе к странице редактирования поста."""
        yesauthor = PostsURLTests.authorized_yesauthor
        template = cst.REVERSE_DICT['create'][1]
        address = cst.REVERSE_DICT['edit'][0]
        response = yesauthor.get(address)
        self.assertTemplateUsed(response, template)

    def test_redirect_after_edit(self):
        """Проверка переадресации автора поста на страницу поста после
           его редактирования."""
        yesauthor = PostsURLTests.authorized_yesauthor

        response = yesauthor.post(
            cst.REVERSE_DICT['edit'][0],
            {'text': 'new odd text'},
            follow=True)
        self.assertRedirects(response, cst.REVERSE_DICT['post'][0])

    def for_all_404(self):
        """Проверка наличия ошибки 404 при попытке
           доступа к несуществующим страницам."""
        yesauthor = PostsURLTests.authorized_yesauthor

        for address in cst.PAGES_DNT_EXIST:
            with self.subTest(address=address):
                response = yesauthor.get(address)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
