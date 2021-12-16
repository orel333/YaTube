from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """Создаёт представление страницы 'Об авторе'."""
    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    """Создаёт представление страницы 'Технологии'."""
    template_name = 'about/tech.html'
# Create your views here.
