from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
# from django.core.cache import cache
from django.core.paginator import Paginator
# from django.views.decorators.cache import cache_page

from .models import Follow, Group, Post, User
from yatube.settings import PAGINATOR_NUM
from .forms import CommentForm, PostForm


# @cache_page(60 * 15)
def index(request):
    """Создаёт представление главной страницы."""
    post_list = Post.objects.all().select_related(
        'author').select_related('group')
    page_obj = paginator_func(request, post_list, PAGINATOR_NUM)
    # id_list=[]
    # for post in page_obj:
    # id_list.append(post.id)

    # post_list_pro = Post.objects.filter(
    # id__in=id_list).select_related('author')

    context = {
        # 'index': True,
        'page_obj': page_obj,
    }
    template = 'posts/index.html'
    return render(request, template, context)


def group_posts(request, slug):
    """Создаёт представление страницы постов группы."""
    group = get_object_or_404(Group, slug=slug)
    # posts = group.posts.all()
    # posts = cache.get('posts')
    # if not posts:
    posts = Post.objects.filter(group=group).select_related('author').all()
    # cache.set('posts', posts, 30)
    page_obj = paginator_func(request, posts, PAGINATOR_NUM)
    template = 'posts/group_list.html'
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    """Создаёт представление профиля пользователя."""
    author = get_object_or_404(User, username=username)
    # author = user.username
    # posts = author.posts.all()
    posts = Post.objects.filter(author=author).select_related(
        'author').select_related('group')
    user_name = user_name_func(author)
    paginator = Paginator(posts, PAGINATOR_NUM)
    page_obj = paginator_func(request, posts, PAGINATOR_NUM)
    collision = False
    following = False
    if request.user.is_authenticated:
        if request.user == author:
            collision = True
        if Follow.objects.filter(user=request.user, author=author).exists():
            following = True
        else:
            following = False

    context = {
        'collision': collision,
        'following': following,
        'page_obj': page_obj,
        'posts_total': paginator.count,
        'author': author,  # чтобы пройти тест; не используется в шаблоне
        'user_name': user_name,
    }
    template = 'posts/profile.html'
    return render(request, template, context)


def post_detail(request, post_id):
    """Создаёт представление страницы поста."""
    post = get_object_or_404(Post, id=post_id)
    user = post.author
    user_name = user_name_func(user)
    # posts_total = user.posts.all().count()
    posts_total = Post.objects.filter(author=user.pk).count()
    comments = post.comments.all().select_related('author')
    context = {
        'post': post,
        'posts_total': posts_total,
        'author': user,
        'author_name': user_name,
        'form': CommentForm(),
        'comments': comments
    }
    template = 'posts/post_detail.html'
    return render(request, template, context)


def user_list(request, username):
    """Создаёт представление страницы постов пользователя."""
    user = get_object_or_404(User, username=username)
    user_name = user_name_func(user)
    # posts = user.posts.all()
    posts = Post.objects.filter(author=user.pk).select_related('author').all()
    page_obj = paginator_func(request, posts, PAGINATOR_NUM)
    context = {
        'page_obj': page_obj,
        'user': user,
        'user_name': user_name,
    }
    template = 'posts/user_list.html'
    return render(request, template, context)


@login_required
def post_create(request):
    """Создаёт представление страницы создания нового поста."""
    user = request.user
    template = 'posts/create_post.html'
    context = {}
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        data_post = form.save(commit=False)
        data_post.author = user
        data_post.group = form.cleaned_data['group']
        # data_post.pub_date = dt.datetime.now()
        data_post.text = form.cleaned_data['text']
        data_post.save()
        return redirect('posts:profile', user.username)
    else:
        context['form'] = form
        # print(form)
        return render(request, template, context)


@login_required
def post_edit(request, post_id):
    """Создаёт представление страницы редактирования существующего поста."""
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    """Обрабатывает запрос на добавление комментария."""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    # print(form.is_valid())
    if form.is_valid():
        # print('Valid')
        data_comment = form.save(commit=False)
        data_comment.author = request.user
        data_comment.post = post
        # data_comment.created = dt.datetime.now()
        data_comment.text = form.cleaned_data['text']
        data_comment.save()
    # return redirect('posts:post_detail', post_id)
    # print('Not valid')
    # form = CommentForm()
    return redirect('posts:post_detail', post_id)


@login_required
def follow_index(request):
    """Показать страницу с авторами, на
       которых пользователь подписан."""
    user = request.user
    # follows = user.follower.all()
    # follows = Follow.objects.filter(user=user)
    # authors = set([x.author for x in follows])
    # posts = Post.objects.filter(author__in=authors)
    posts = Post.objects.filter(author__following__user=user)
    # post_list = Post.objects.filter(author__in=authors)
    page_obj = paginator_func(request, posts, PAGINATOR_NUM)
    context = {
        #'follow': True,
        'page_obj': page_obj,
    }
    template = 'posts/follow.html'
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """Подписаться на автора."""
    author = get_object_or_404(User, username=username)
    if request.user != author and not Follow.objects.filter(
        user=request.user,
        author=author
    ).exists():
        Follow.objects.create(
            user=get_object_or_404(User, username=request.user.username),
            author=get_object_or_404(User, username=username)
        )
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    """Отписаться от автора."""
    unfollower = Follow.objects.get(
        user=get_object_or_404(User, username=request.user.username),
        author=get_object_or_404(User, username=username)
    )
    unfollower.delete()
    return redirect('posts:profile', username)


def user_name_func(user):
    """Определяет какое имя писать на странице: полное или username."""
    if user.first_name == '' and user.last_name == '':
        return user.username
    return user.get_full_name


def paginator_func(request, posts, num):
    """Готовит пагинацию."""
    paginator = Paginator(posts, num)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
