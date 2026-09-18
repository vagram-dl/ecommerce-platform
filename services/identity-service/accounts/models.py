from idlelib.pyparse import trans

from django.db import models
from django.contrib.auth.models import AbstractUser



class User(AbstractUser):
    email = models.EmailField(
        'email_address',
        unique=True,
        blank=False,
        null=False
    )

    phone_number  = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    is_email_verified = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at =models.DateTimeField(
        auto_now=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'user'
        verbose_name_plural= 'users'
        ordering = ['-created_at']

    def __str__(self):
        return self.email

class OIDCClient(models.Model):
    client_id = models.CharField(
        max_length=64,
        unique=True,
        help_text="Публичный идентификатор приложения"
    )

    client_secret = models.CharField(
        max_length=128,
        help_text="Секретный ключ для проверки подлинности клиента"
    )

    name = models.CharField(
        max_length=100,
        help_text="Название приложения (например, 'Ecommerce Frontend')"
    )

    redirect_uri = models.URLField(
        help_text="URL,  куда перенаправлять пользователя после аутентификации"
    )

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='oidc_clients',
        help_text="Пользователь, который зарегистрировал это приложение"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Активен ли клиент (False = доступ отозван)"
    )

# Create your models here.
