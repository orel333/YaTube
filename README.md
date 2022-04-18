### Социальная сеть для блогеров
[сам сайт](http://orel333.pythonanywhere.com/)
- Сервис позволяет регистрироваться, менять и сбрасывать пароль через электронную почту, зарегистрированным пользователям публиковать посты, писать комментарии к постам, редактировать и удалять свои посты и комментарии, подписываться на авторов, менять ленту выдачи постов так, чтобы содержала только посты авторов, на которые пользователь подписан.
- Настроена пагинация для отображения постов.
- При переходе на экран мобильного телефона в приложении настроена адаптация меню хедера в бургер, раскрывающийся при нажатии.
- Абсолютно весь функционал приложения покрыт тестами.

#### Технологии:
- Python 3.8.0
- Django 2.2.16
- Bootstrap 5.1.3

#### Запуск проекта
- Установите и активируйте виртуальное окружение
- Установите зависимости из файла requirements.txt
```
pip install -r requirements.txt
``` 
- В папке с файлом manage.py выполните команду:
```
python3 manage.py runserver
```
