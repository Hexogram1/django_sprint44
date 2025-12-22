Раздел 1

1. Модели Category, Location, Post, Comment должны быть представлены в админке –  admin.py

Файл:admin.py

```python
from django.contrib import admin
from blog.models import Category, Comment, Location, Post

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

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'created_at')
    list_editable = ('is_published',)
    list_filter = ('is_published',)
    search_fields = ('title', 'description')


```
 
Все модели проекта зарегистрированы в Django-админке с использованием декоратора @admin.register(), что позволяет администраторам управлять данными через веб-интерфейс.

2. В моделях у всех полей для связи между таблицами с типом ForeignKey должны быть заданы параметры on_delete . Для большинства — со значением CASCADE , для локации и категории — SET_NULL .

Файл:models.py

```python
(class Post(PublishedModel))
author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        null=True,
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Местоположение',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        verbose_name='Категория',
    )

(class Comment(PublishedModel))
post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
```

CASCADE для автора и поста комментария: при удалении пользователя или поста удаляются связанные записи
SET_NULL для локации и категории: при удалении локации или категории поле становится NULL, что предотвращает каскадное удаление постов

3. При настройке формы в forms.py для поста нужно предоставить на редактирование поля is_published, pub_date , чтобы автор смог изменять их: публиковать, откладывать, снимать с публикации конкретный пост.
 
Файл:forms.py

```python
class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author','text', 'pub_date', 'is_published')
        widgets = {
            'pub_date': forms.DateTimeInput(format='%Y-%m-%dT%H:%M',
                                            attrs={'type': 'datetime-local'})
        }

```

Использование exclude = ('author',) включает все поля модели Post в форму, кроме автора. Автор устанавливается автоматически. Виджет для pub_date предоставляет удобный интерфейс для выбора даты и времени

4. Извлекаемые из URL ключи — в urls.py — должны быть содержательными: pk или id не годятся. Нужно добавлять имя модели или таблицы.
 
Файл:urls.py

```python
path(
        '<int:post_id>/edit/',
        views.PostUpdateView.as_view(),
        name='edit_post'
    ),
    path(
        '<int:post_id>/delete/',
        views.PostDeleteView.as_view(),
        name='delete_post'
    ),
    path(
        '<int:post_id>/comment/',
        views.CommentCreateView.as_view(),
        name='add_comment'
    ),
    path(
        '<int:post_id>/edit_comment/<int:comment_id>/',
        views.CommentUpdateView.as_view(),
        name='edit_comment'
    ),
    path(
        '<int:post_id>/delete_comment/<int:comment_id>/',
        views.CommentDeleteView.as_view(),
        name='delete_comment',
    ),
```

Использование post_id и comment_id вместо абстрактного pk делает URL понятными и самодокументируемыми, указывая на тип объект

5. В маршрутах, которые настраиваются в urls.py , для ника пользователя тип параметра в URL не может быть slug 
path ('profile/<slug:username>/', ...) , так как у слага мало вариантов.
 
Файл:urls.py

```python
    path(
        '<str:username>/',
        views.ProfileView.as_view(),
        name='profile'
    ),
```

Использование str вместо slug позволяет использовать любые символы в имени пользователя, включая кириллицу и специальные символы. Slug ограничивает символы латиницей, цифрами, дефисами и подчеркиваниями

6. Явные URL – например, '/' или 'posts/create/' или 'profile/oleg/' — не могут применяться нигде, кроме вызовов path() в urls.py . Во всех остальных частях проекта URL должны вычисляться через имя маршрута, заданного в path(url, контроллер, name='имя-маршрута') .
Допустимые способы: 
•	В контроллерах в views.py через reverse('имя-маршрута', параметр) (можно и без параметра) или redirect('имя-маршрута', параметр ) . 
•	В шаблонах через {% url 'имя-маршрута' параметр %} .
 
Файл:views.py

```python
def get_success_url(self) -> str:
        return reverse('blog:post_detail',
                       kwargs={'pk': self.kwargs.get('post_id')})

```
 
Избегание явных URL ('/posts/1/') в пользу именованных маршрутов делает код гибким: при изменении структуры URL достаточно обновить urls.py

7. Извлечение поста, категории, комментария из базы выполняется только через вызов get_object_or_404() .
 
Файл:views.py

```python
(class CategoryListView(CustomListMixin, ListView))
def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['category_slug'], is_published=True)
        
        # Получаем базовый QuerySet с аннотацией комментариев
        base_qs = super().get_queryset()
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

(class PostCreateView(LoginRequiredMixin, CreateView))
def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
```
 
get_object_or_404() объединяет получение объекта и обработку случая, когда объект не найден (возвращает 404 вместо исключения)

8.	Все посты в наборах, попадающих на страницы «Главная», «Посты категории», «Посты автора», должны быть дополнены количеством комментариев.
 
Файл:mixins.py

```python
(class CustomListMixin)
def get_queryset(self):
        queryset = Post.objects.select_related(
            'category', 'location', 'author'
        ).annotate(
            comment_count=Count('comments') 
        )
        return queryset.order_by(*Post._meta.ordering)

```

Метод annotate(comment_count=Count('comments')) добавляет к каждому посту в QuerySet поле comment_count с количеством комментариев, что позволяет отображать эту информацию без N+1 запросов

9. Вычисление количества комментариев к постам должно находится в единственном месте — в новой функции. Само вычисление выполняется методом кверисета annotate() .
 
Файл:mixins.py

```python
(class CustomListMixin)
def get_queryset(self):
        queryset = Post.objects.select_related(
            'category', 'location', 'author'
        ).annotate(
            comment_count=Count('comments') 
        )
        return queryset.order_by(*Post._meta.ordering)

```

Логика подсчета комментариев централизована в миксине CustomListMixin, что исключает дублирование кода и обеспечивает согласованность

10. После вызова annotate() обязательно нужен вызов сортирующего метода: сортировка из модели уже будет неприменима, так как добавилось поле. Без сортировки пагинация работать не сможет.
 
Файл:mixins.py

```python
(class CustomListMixin)
def get_queryset(self):
        queryset = Post.objects.select_related(
            'category', 'location', 'author'
        ).annotate(
            comment_count=Count('comments') 
        )
        return queryset.order_by(*Post._meta.ordering)

```

После добавления аннотации (annotate) необходимо явно указать сортировку, так как автоматическая сортировка из модели становится недоступной. Это критически важно для корректной работы пагинации

11. Вычисление одной страницы пагинатора нужно разместить в новой функции.
 
Файл:utils.py

```python
def get_paginated_page(queryset, request, per_page=10):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
```

Централизованная функция для создания пагинированных страниц, обеспечивающая единообразие и упрощающая поддержку

12. Набор постов на странице автора должен зависеть от посетителя. Только посетитель-автор может видеть свои неопубликованные посты.
 
Файл:views.py

```python
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
        
        return author_qs  
```

Автор видит все свои посты (включая неопубликованные), а другие пользователи — только опубликованные. Проверка if self.author != self.request.user реализует эту логику.

13. Фильтрация записей из таблицы постов по опубликованности должна размещаться в новой функции.
 
Файл:utils.py

```python
def published_only(queryset=None):
    if queryset is None:
        from .models import Post
        queryset = Post.objects.all()
    
    return queryset.filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    )
```

Централизованная функция для фильтрации только опубликованных постов с учетом времени публикации и статуса категории

14. Контроллер-функции для создания, редактирования, удаления работают не с анонимом. Нужно применить Django-декоратор @login_required .
  
Файл:views.py

```python
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
```
 
LoginRequiredMixin автоматически перенаправляет неаутентифицированных пользователей на страницу входа при попытке доступа к защищенным представлениям

15. Для применения redirect() не нужно вычислять URL через reverse() . redirect() сам умеет работать с маршрутами.
 
Файл:mixins.py

```python
    def dispatch(self, request, *args, **kwargs):
        """
        При получении объекта не указываем автора.
        Результат сохраняем в переменную.
        Сверяем автора объекта и пользователя из запроса.
        """
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)
```

Функция redirect() автоматически разрешает имена маршрутов, поэтому нет необходимости предварительно вызывать reverse(), что упрощает код

16. В контроллере post_detail () нужно анализировать автора поста, чтобы отказать в показе неопубликованного не авторам.
 
Файл:views.py

```python
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
```

Двухэтапная проверка: сначала получается пост без фильтров (для проверки авторства), затем, если пользователь не автор, повторный запрос с фильтрами опубликованности

Раздел 2
1. В гит-репозитории не должны храниться папки static , static-dev , html 
2. Класс формы для поста в forms.py лучше настраивать не через fields , а через exclude , так как нужны изменения всех полей кроме автора. Проверить, что поле created_at не попадёт в форму: по модели оно нередактируемое.
 
Файл:forms.py

```python
class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateTimeInput(format='%Y-%m-%dT%H:%M',
                                            attrs={'type': 'datetime-local'})
        }
```

Использование exclude = ('author',) вместо явного перечисления полей (fields = ...) автоматически включает все поля модели, кроме автора. Поле created_at не редактируемое (auto_now_add=True), поэтому Django автоматически исключает его из формы

3. Функции «фильтрация по опубликованным» и «дополнение числа комментариев» может быть объединена в одну. Тогда для этой функции потребуется параметр со значениями «Да» или «Нет», чтобы можно было пропускать лишнюю фильтрацию для постов на странице автора для самого автора.
 
Файл:utils.py

```python
def get_posts_with_comments(show_all=False, queryset=None):
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
```

4. Функция, фильтрующая по опубликованности, может принимать параметром набор постов для фильтрации. Этому параметру можно дать значение по умолчанию «все посты таблицы», что будет ещё лучше.
 
Файл:utils.py

```python
def published_only(queryset=None):
    if queryset is None:
        from .models import Post
        queryset = Post.objects.all()
    
    return queryset.filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    )
```


5.Чтобы в контроллере post_detail() отказать в показе неопубликованного поста не автору, лучше всего делать два вызова get_object_or_404() : 
• Первый для извлечения поста по ключу из полной таблицы. 
• Второй, после проверки авторства — из набора опубликованных постов.
 
Файл:views.py

```python
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
```

6. Извлечения постов для уже излвеченной категории лучше выполнять, применяя «поле связи». То есть вместо посты = Post.objects.filter(category=категория) писать посты = категория.поле-связи . То же самое с постами автора: посты = автор.поле-связи . И с комментариями к постам комментарии = пост.поле-связи .  Важно: внутри шаблонов второй способ практически единственный, так как Python-вставки не допускают прямых вызовов методов с параметрами. А вот обращения к свойствам выполняются легко.
  
 
Файл:views.py

```python
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context
```

7. При указании сортировки после вызова annotate() лучше не угадывать значение, а брать точно такое же, какое уже есть в модели. Пригодится магическое поле ._meta и распаковка. Код будет иметь следующий вид:
предыдущие-действия.order_by(*Post._meta.ordering )
 
Файл:mixins.py

```python
def get_queryset(self):
        queryset = Post.objects.select_related(
            'category', 'location', 'author'
        ).annotate(
            comment_count=Count('comments') 
        )
        return queryset.order_by(*Post._meta.ordering)
```

8. В контроллерах, которые создают или редактируют пост, нужна разная обработка для GET и POST-запросов. Есть способ избежать прямых проверок вида 
if request.method == 'POST': .
Для этого форма создается так: form = PostForm(request.POST or None, ...) .Такая форма годится для обоих запросов. Её валидация form.is_valid() всегда неуспешна при GET-запросе. Значит, проверку метода выполнит проверка ответа от .is_valid() . Удачное совмещение: и при провале валидации, и при GET-запросе как раз и нужно вызывать рендер:
if not form.is_valid():
…
return render(...)
 
Файл:views.py

```python
class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание нового поста."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user}
        )
```


9. У модели «Пользователь» есть поля — например, пароль,— которые нельзя показывать в админке. Поэтому админ-класс нельзя наследовать от django.contrib.admin.ModelAdmin . Для этого есть класс django.contrib.auth.admin.UserAdmin , который будет прятать секреты.
 
Файл:admin.py

```python
@admin.register(User)
class CustomUserAdmin(UserAdmin):
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
```

