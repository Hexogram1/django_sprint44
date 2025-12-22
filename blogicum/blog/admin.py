from django.contrib import admin

from blog.models import Category, Comment, Location, Post

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

TEXT = 'Описание публикации.'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'is_published',
        'category',
        'location',
        'created_at',
        'image',
    )
    list_editable = (
        'is_published',
        'category',
        'location',
    )
    search_fields = ('title',)
    list_filter = ('category',)
    list_display_links = ('title',)
    fieldsets = (
        ('Блок-1', {
            'fields': ('title', 'author', 'is_published',),
            'description': '%s' % TEXT,
        }),
        ('Доп. информация', {
            'classes': ('wide', 'extrapretty'),
            'fields': ('text', 'category', 'location', 'pub_date', 'image',),
        }),
    )


class PostInline(admin.TabularInline):
    model = Post
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = (
        PostInline,
    )
    list_display = (
        'title',
        'slug',
        'is_published',
        'description',
        'created_at',
    )
    list_filter = ('title',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    inlines = (
        PostInline,
    )
    list_display = (
        'name',
        'is_published',
    )
    list_filter = ('name',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'author',
        'is_published',
        'created_at',
    )
    list_filter = ('author',)
    list_editable = ('is_published',)

User = get_user_model()

# Разименуем стандартную регистрацию
admin.site.unregister(User)

# Регистрируем с кастомным админом
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Кастомизированный админ-класс для пользователей.
    UserAdmin скрывает пароли и предоставляет безопасный интерфейс.
    """
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name', 'email')}),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )