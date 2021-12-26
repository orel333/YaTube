import re

from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import User
import users.tests.constants as cst


class UserFormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.new_client = Client()

        INIT_PASSWORD = 'zqpm1111'

        cls.USER_DATA = {
            'first_name': 'Alex',
            'last_name': 'Orel',
            'username': 'orel333',
            'email': 'orel333@mail.ru',
            'password1': INIT_PASSWORD,
            'password2': INIT_PASSWORD,
        }

        cls.ANONYM = 'AnonymousUser'

        cls.DATA_TO_LOGIN = {
            'username': cls.USER_DATA['username'],
            'password': cls.USER_DATA['password1']
        }

    def test_signup_form(self):
        """При отправке формы регистрации
           создаётся новый пользователь."""

        users_num = User.objects.count()
        signup(UserFormsTest.new_client, UserFormsTest.USER_DATA)

        self.assertEqual(User.objects.count(), users_num + 1)
        new_user = User.objects.get(last_name='Orel')
        self.assertTrue(new_user.is_authenticated)

        list_to_check = list(UserFormsTest.USER_DATA.keys())[:4]
        for field in list_to_check:
            with self.subTest(field=field):
                self.assertEqual(
                    getattr(new_user, field),
                    UserFormsTest.USER_DATA[field])

    def test_wrong_password_or_username(self):
        """Вход только при верном пароле и username,
        отображаются верные шаблоны."""

        signup(UserFormsTest.new_client, UserFormsTest.USER_DATA)

        client_2 = Client()
        self.assertEqual(who_uses(client_2), UserFormsTest.ANONYM)

        login(client_2, UserFormsTest.DATA_TO_LOGIN)
        self.assertEqual(
            who_uses(client_2),
            UserFormsTest.DATA_TO_LOGIN['username'])

        client_2.get(cst.REVERSE['logout'][0])
        self.assertEqual(who_uses(client_2), UserFormsTest.ANONYM)

        # попытка входа не под тем логином или паролем

        DATA_TO_LOGIN_ER1 = {
            'username': 'orel334',
            'password': UserFormsTest.DATA_TO_LOGIN['password']
        }

        DATA_TO_LOGIN_ER2 = {
            'username': 'orel333',
            'password': 'nobody'
        }

        login(client_2, DATA_TO_LOGIN_ER1)
        self.assertEqual(who_uses(client_2), UserFormsTest.ANONYM)

        login(client_2, DATA_TO_LOGIN_ER2)
        self.assertEqual(who_uses(client_2), UserFormsTest.ANONYM)

    def test_change_password_and_logout(self):
        """Смена пароля и выход, отображаются верные шаблоны."""
        client = UserFormsTest.new_client
        signup(client, UserFormsTest.USER_DATA)
        login(client, UserFormsTest.DATA_TO_LOGIN)

        NEW_PASSWORD = 'qpzm2021'

        DATA_TO_CHANGE_PASSWORD = {
            'old_password': UserFormsTest.USER_DATA['password1'],
            'new_password1': NEW_PASSWORD,
            'new_password2': NEW_PASSWORD,
        }
        response = client.get(cst.REVERSE[
            'password_change_form'][0])
        self.assertTemplateUsed(
            response,
            cst.REVERSE['password_change_form'][1])
        response_2 = client.post(
            cst.REVERSE['password_change_form'][0],
            DATA_TO_CHANGE_PASSWORD,
            follow=True)
        self.assertTemplateUsed(
            response_2,
            cst.REVERSE['password_change_done'][1])

        response_3 = client.get(cst.REVERSE['logout'][0])
        self.assertTemplateUsed(response_3, cst.REVERSE['logout'][1])

        login(client, UserFormsTest.DATA_TO_LOGIN)
        self.assertEqual(who_uses(client), UserFormsTest.ANONYM)

        login(
            client,
            {
                'username': UserFormsTest.USER_DATA['username'],
                'password': NEW_PASSWORD}
        )
        self.assertEqual(who_uses(client), UserFormsTest.USER_DATA['username'])

    def test_restore_password(self):
        """Круг восстановления пароля, отображаются верные шаблоны."""
        client = UserFormsTest.new_client
        signup(client, UserFormsTest.USER_DATA)

        response = client.post(
            reverse('users:password_reset_form'),
            data={'email': UserFormsTest.USER_DATA['email']},
            follow=True)

        end_address = '/auth/password_reset/done/'
        self.assertTemplateUsed(
            response, cst.REVERSE['password_reset_done'][1])
        self.assertRedirects(response, end_address)
        mail_text = mail.outbox[0].__dict__['body']
        pre_url_end = r'/../......................../'
        url_end = re.findall(pre_url_end, mail_text)[0]
        url_to_restore = f'http://testserver/auth/reset{url_end}'
        response_2 = client.get(url_to_restore, follow=True)
        self.assertTemplateUsed(
            response_2,
            'users/password_reset_confirm.html')
        url_to_set_password = response_2.redirect_chain[0][0]

        NEW_PASSWORD_SET = {
            'new_password1': 'wxom2021',
            'new_password2': 'wxom2021'
        }

        response_3 = client.post(
            url_to_set_password,
            data=NEW_PASSWORD_SET,
            follow=True
        )
        self.assertTemplateUsed(
            response_3,
            cst.REVERSE['password_reset_complete'][1]
        )
        login(client, UserFormsTest.DATA_TO_LOGIN)
        self.assertEqual(who_uses(client), UserFormsTest.ANONYM)

        login(
            client,
            {
                'username': UserFormsTest.USER_DATA['username'],
                'password': NEW_PASSWORD_SET['new_password1']
            })
        self.assertEqual(who_uses(client), UserFormsTest.USER_DATA['username'])


def login(self, data_to_login):
    """Осуществляет ручной вход пользователя на сайт по имени и паролю."""
    self.post(
        cst.REVERSE['login'][0],
        data=data_to_login)


def who_uses(self):
    """Определяет username пользователя, привязанного к клиенту."""
    response = self.get(cst.REVERSE['index'][0])
    username = str(response.wsgi_request.user)
    return username


def signup(self, data_to_signup):
    """Ручная регистрация пользователя."""
    self.post(cst.REVERSE['signup'][0], data=data_to_signup)
