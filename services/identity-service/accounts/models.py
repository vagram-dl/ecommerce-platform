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

# Create your models here.
