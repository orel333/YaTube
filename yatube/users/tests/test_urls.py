from django.test import Client, TestCase

import users.tests.constants as cst


class UserFormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.new_client = Client()

    def test_common_pages_templates(self):
        """Корректные шаблоны при обращении
        к общедоступным страницам с формами."""
        for item in cst.LIST_FOR_REVERSE[:3]:
            with self.subTest(item=item):
                response = UserFormsTest.new_client.get(
                    cst.REVERSE[item][0]
                )
                self.assertTemplateUsed(
                    response, cst.REVERSE[item][1]
                )

# Остальные шаблоны протестированы в test_forms
# при "ручном" прохождении форм зарегистрированным
# пользователем
