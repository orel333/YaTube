from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from posts.models import User


class SpecialPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.csrf_client = Client(enforce_csrf_checks=True)
        cls.INIT_PASSWORD = 'zqmp1111'
        cls.careless_user = User.objects.create_user(
            username='I_use_suspicious_sites',
            password=cls.INIT_PASSWORD)
        cls.normal_client = Client()
        cls.normal_user = User.objects.create_user(
            username='I_am_cautious'
        )
# не нашёл как сделать
    # def test_403(self):
        # pass

    def test_403csrf(self):
        """Ошибка 403csrf при попытке cross-site-request-forgery
        через страницу смены пароля."""
        NEW_PASSWORD = 'qpzm2021'

        DATA_TO_CHANGE_PASSWORD = {
            'old_password': SpecialPagesTest.INIT_PASSWORD,
            'new_password1': NEW_PASSWORD,
            'new_password2': NEW_PASSWORD,
        }

        response = SpecialPagesTest.csrf_client.post(
            reverse('users:password_change_form'),
            DATA_TO_CHANGE_PASSWORD,
            follow=True)
        self.assertTrue(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertTemplateUsed(response, 'core/403csrf.html')

    def test_404(self):
        """Тест страницы 404."""
        client = SpecialPagesTest.normal_client
        response = client.get('/some/imaginary/page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')

# не нашёл как сделать
    # def test_500(self):
        # pass
