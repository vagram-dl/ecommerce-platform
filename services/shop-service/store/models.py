from dataclasses import fields

from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.conf import settings
import uuid
from django.db import models,transaction
from django.core.exceptions import ValidationError

class Category(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Название",
        help_text="Например: 'Смартфоны','Ноутбуки'"
    )

    slug = models.SlugField(
        max_length=100,
        unique = True,
        blank = True,
        verbose_name = "URL-адрес",
        help_text = "Автоматически заполняется из названия. Например: 'smartfony'"
    )

    parent = models.ForeignKey(
         'self',
         on_delete=models.CASCADE,
         null = True,
         blank = True,
         related_name = 'children',
         verbose_name = "Родительская категория",
         help_text = "Выберите родительскую категорию или оставьте пустым для корневой"

     )

    order = models.IntegerField(
        default = 0,
        verbose_name = "Порядок сортировки",
        help_text = "Чем меньше число, тем выше в списке"
    )

    is_active = models.BooleanField(
        default = True,
        verbose_name = "Активна",
        help_text = "Отображать категорию на сайте"
    )

    description = models.TextField(
        blank = True,
        verbose_name = "Описание",
        help_text = "Используется для SEO и отображения на странице категории"
    )

    seo_title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="SEO заголовок",
        help_text="Для поисковиков.Если пусто - используем название"
    )

    seo_description = models.CharField(
        max_length=160,
        blank=True,
        verbose_name="SEO описание",
        help_text="Короткое описание для поиска (до 160 символов)"
    )

    created_at = models.DateTimeField(auto_now_add=True,verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True,verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['order','name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['parent']),
            models.Index(fields=['is_active']),
        ]



    def __str__(self):
        if self.parent:
            return f"{self.parent}->{self.name}"
        return self.name

    def save(self,*args,**kwargs):
        if not self.slug:
            if self.name:
                self.slug = slugify(self.name)
            else:
                self.slug = f"category-{Category.objects.count() + 1}"

        original_slug = self.slug
        counter = 1

        while Category.objects.filter(slug = self.slug).exclude(pk = self.pk).exists():
            self.slug = f"{original_slug}-{counter}"
            counter += 1
        if not self.seo_title and self.name:
            self.seo_title= self.name
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('category_detail',kwargs={'slug':self.slug})

    def get_ancestors(self, include_self = False):
        ancestors = []
        current = self.parent

        while current:
            ancestors.append(current)
            current = current.parent
        ancestors.reverse()

        if include_self:
            ancestors.append(self)
        return ancestors

    def get_descendants(self, include_self = False):
        descendants = []

        def _collect_descendants(category):
            for child in category.children.all():
                descendants.append(child)
                _collect_descendants(child)
        _collect_descendants(self)

        if include_self:
            descendants.insert(0,self)
        return descendants

    def product_count(self):
        from .models import Product
        category_ids = [cat.id for cat in self.get_descendants(include_self=True)]
        return Product.objects.filter(category_id__in=category_ids).count()

    @property
    def children_count(self):
        return self.children.count()

    @property
    def is_root(self):
        return self.parent is None





class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete = models.CASCADE,
        related_name = 'products'
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank = True)
    price = models.DecimalField(max_digits=10,decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField('Активен', default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class Wallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet'
    )
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Баланс"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Кошелек"
        verbose_name_plural = "Кошельки"

    def __str__(self):
        return f"Wallet of {self.user.username} ({self.balance} ₽)"

class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Ожидает'
        SUCCESS = 'success', 'Успешно'
        FAILED = 'failed', 'Ошибка'

    class Type(models.TextChoices):
        DEPOSIT = 'deposit','Пополнение'
        WITHDRAWAL = 'withdraw','Списание (Покупка)'

    idempotency_key = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        db_index=True,
        verbose_name="Ключ идемпотентности"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=10,decimal_places=2,verbose_name="Сумма")
    type = models.CharField(max_length=20, choices=Type.choices, verbose_name="Тип операции")

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Статус"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Платеж",
        verbose_name_plural = "Платежи"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user','status']),
        ]

    def __str__(self):
        return f"{self.get_type_display()} {self.amount} ₽ ({self.get_status_display()})"


# Create your models here.
