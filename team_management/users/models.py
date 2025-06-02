from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'Пользователь'),
        ('manager', 'Менеджер'),
        ('admin', 'Администратор команды'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    team = models.ForeignKey('teams.Team', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.username