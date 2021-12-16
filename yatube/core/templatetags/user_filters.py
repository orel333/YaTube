from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    """Добавляет класс к полю формы, вставленной через контекст."""
    return field.as_widget(attrs={'class': css})


@register.filter
def firsttitle(text):
    """Делает первую букву строки заглавной."""
    a = text[0].upper()
    firsttitle_text = a + text[1:]
    return firsttitle_text


@register.filter
def text_processor(text, length):
    """Оставляет указанное количество предложений текста."""
    processored_text = text.split('. ')
    if len(processored_text) <= length:
        return text
    else:
        post_text1 = '. '.join((processored_text)[:length])
        brief_text = post_text1 + '... <есть продолжение>'
        return brief_text
