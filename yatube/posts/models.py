# from django.utils import dateformat
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F, Q
from django.db.models.fields.related import ForeignKey
# from django.conf import settings

from yatube.settings import TRUNCATE_NUM

User = get_user_model()


class Group(models.Model):
    """Описывает модель группы."""
    description = models.TextField('Описание группы')
    slug = models.SlugField('Индекс URL', unique=True)
    title = models.CharField('Название группы', max_length=200)

    class Meta:
        verbose_name = 'группа'
        verbose_name_plural = 'группы'

    def __str__(self):
        return self.title


class Post(models.Model):
    """Описывает модель поста."""
    author = models.ForeignKey(
        User,
        help_text='Здесь отображается полное имя автора либо его username',
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор поста',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        default=None,
        help_text='Группа, к которой будет относиться пост',
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
    )
    # pub_date = models.DateTimeField(CreatedModel.created)
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        help_text=(
            'Дата отображается в формате,',
            ' принятом в Российской Федерации')
    )
    text = models.TextField(
        verbose_name='Текст поста',
        blank=False,
        null=False,
        help_text='Текст поста не должен быть пустым',
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'пост'
        verbose_name_plural = 'посты'

    def __str__(self):
        """Определяет отображение поста при преобразовании его в строку."""
        return self.text[:TRUNCATE_NUM]

        # formatted_date = dateformat.format(
        # self.pub_date, settings.DATE_FORMAT
        # )
        # processored_text = self.text.split(". ")
        # text_to_return_1 = "\n" + "Автор: " + self.author.username
        # text_to_return = text_to_return_1 + "\n" + formatted_date + "\n"
        # if len(processored_text) <= 5:
        # post_text = self.text
        # else:
        # post_text_1 = ". ".join((processored_text)[:5])
        # post_text = post_text_1 + ". <...read more on the website...>"
        # text_to_return += post_text + "\n" * 2
        # return text_to_return


class Comment(models.Model):
    """Описывает модель комментариев."""
    post = models.ForeignKey(
        Post,
        verbose_name='Пост',
        related_name='comments',
        on_delete=models.CASCADE
    )

    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='comments',
        on_delete=models.CASCADE
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        default=None,
        blank=False,
        null=False
    )
    created = models.DateTimeField(
        verbose_name='Создано',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'

    def __str__(self):
        """Определяет отображение комментария
           при преобразовании его в строку."""
        return self.text


class Follow(models.Model):
    """Подписка на авторов."""
    user = ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = ForeignKey(
        User,
        verbose_name='Интересный автор',
        on_delete=models.CASCADE,
        related_name='following'
    )
    subscribe_date = models.DateTimeField(
        verbose_name='Дата и время подписки',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-subscribe_date',)
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
        constraints = [
            # models.CheckConstraint(
                # check=~(F('user')==F('author')), name='not_for_self'),
            models.UniqueConstraint(
                fields=['user', 'author'], name="unique_follow"),]
