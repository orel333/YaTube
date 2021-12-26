from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class AboutURLsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()

        cls.REVERSE = {
            'author': [reverse('about:author'), 'about/author.html'],
            'tech': [reverse('about:tech'), 'about/tech.html'],
        }

    def test_pages(self):
        """Проверка доступности страниц и корректности
        выбора шаблонов для их отображения."""
        guest_client = AboutURLsTest.guest_client
        for page in AboutURLsTest.REVERSE.keys():
            with self.subTest(page=page):
                response = guest_client.get(AboutURLsTest.REVERSE[page][0])
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(
                    response, AboutURLsTest.REVERSE[page][1])
