from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from .utils import published_only
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from blog.forms import CommentForm, PostForm, UserForm
from blog.mixins import CommentChangeMixin, CustomListMixin, PostChangeMixin
from blog.models import Category, Comment, Post, User


class IndexHome(CustomListMixin, ListView):
    """Главная страница блога."""

    template_name = 'blog/index.html'

    def get_queryset(self):
        # Используем объединенную функцию
        from .utils import get_posts_with_comments
        return get_posts_with_comments(show_all=False)


class CategoryListView(CustomListMixin, ListView):
    """Рендеринг публикаций в конкретной категории."""

    template_name = 'blog/category.html'

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['category_slug'], is_published=True)
        
        # Получаем базовый QuerySet с аннотацией комментариев
        base_qs = super().get_queryset()
        
        # Фильтруем по категории
        filtered_qs = base_qs.filter(category__slug=self.kwargs['category_slug'])
        
        # Применяем фильтрацию опубликованных
        from .utils import published_only
        return published_only(filtered_qs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context

class ProfileView(CustomListMixin, ListView):
    """Рендеринг профиля пользователя."""

    template_name = 'blog/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        return context

    def get_queryset(self):
        self.author = get_object_or_404(User, username=self.kwargs['username'])
        
        # Получаем базовый QuerySet с аннотацией комментариев
        base_qs = super().get_queryset()
        
        # Фильтруем по автору
        author_qs = base_qs.filter(author=self.author)
        
        # Применяем фильтрацию (если пользователь не автор)
        if self.author != self.request.user:
            from .utils import published_only
            return published_only(author_qs)
        
        return author_qs  # Автор видит все свои посты (включая аннотацию)

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля."""

    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание нового поста."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        """
        При создании поста мы не можем указывать автора вручную,
        для этого переопределим метод валидации:
        """
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


class PostUpdateView(LoginRequiredMixin, PostChangeMixin, UpdateView):
    """Редактирование поста."""

    form_class = PostForm

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.kwargs['post_id']])


class PostDeleteView(LoginRequiredMixin, PostChangeMixin, DeleteView):
    """Удаление поста."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


class PostDetailView(DetailView):
    """
    Рендеринг страницы с отдельным постом.
    Сначала проверяем наличие поста в БД по pk без фильтров.
    Затем проверяем авторство, используя фильтры.
    """

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'pk'

    def get_object(self, queryset=None):
    # Первый вызов - проверка существования
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
    
    # Второй вызов - проверка доступности
        if post.author != self.request.user:
            post = get_object_or_404(
                published_only(Post.objects.all()),
                pk=self.kwargs['pk']
        )
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Создание нового комментария."""

    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            Post, pk=self.kwargs.get('post_id')
        )
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse('blog:post_detail',
                       kwargs={'pk': self.kwargs.get('post_id')})


class CommentUpdateView(LoginRequiredMixin, CommentChangeMixin, UpdateView):
    """Редактирование комментария."""

    form_class = CommentForm


class CommentDeleteView(LoginRequiredMixin, CommentChangeMixin, DeleteView):
    """Удаление комментария."""
