# blog/utils.py
from django.utils import timezone
from .models import Post
from django.core.paginator import Paginator
from django.db.models import Count

def published_only(queryset=None):
    if queryset is None:
        from .models import Post
        queryset = Post.objects.all()
    
    return queryset.filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    )


def get_paginated_page(queryset, request, per_page=10):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)

def get_posts_with_comments(show_all=False, queryset=None):
    """
    Возвращает QuerySet постов с комментариями.
    
    Args:
        show_all (bool): True - показать все посты (для автора)
                         False - показать только опубликованные
        queryset: Базовый QuerySet для обработки
    """
    if queryset is None:
        queryset = Post.objects.all()
    
    if not show_all:
        queryset = published_only(queryset)
    
    queryset = queryset.select_related(
        'category', 'location', 'author'
    ).annotate(
        comment_count=Count('comments')
    )
    
    return queryset.order_by(*Post._meta.ordering)