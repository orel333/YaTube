from django.contrib import admin

from .models import Comment, Follow, Group, Post
from yatube.settings import EMPTY_VALUE


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = EMPTY_VALUE


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'slug',
        'title',
        'description',
    )
    search_fields = ('title', 'slug')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'author',
        'text',
        'created'
    )
    search_fields = ('text', 'author')
    # list_editable = ('text',)
    list_filter = ('created',)
    empty_value_display = EMPTY_VALUE


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'subscribe_date',
        'user',
        'author',
    )
    search_fields = ('user', 'author')
    list_filter = ('subscribe_date', 'user', 'author')
    empty_value_display = EMPTY_VALUE

# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
#   list_display = (
#       'username',
#       'first_name',
#       'second_name'
#   )
#   search_fields = ('username', 'second_name')
#   list_filter = ('username')
#   empty_value_display = EMPTY_VALUE
