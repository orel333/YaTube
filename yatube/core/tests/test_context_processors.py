import datetime as dt
import unittest

from django.http.request import HttpRequest

from core.context_processors.year import year

# На самом деле этот тест бесполезен, так как
# проверка осуществляется через такой же синтаксис,
# как и функция.


class ContextProcessorsTest(unittest.TestCase):
    def test_year(self):
        """Контекстный процессор year, который
        добавляет переменную с текущим годом."""
        call = year(HttpRequest)
        result = {'year': dt.datetime.now().year}
        self.assertEqual(call, result)
