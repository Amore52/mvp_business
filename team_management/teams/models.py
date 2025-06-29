from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Team(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название команды")
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_teams',
        verbose_name="Создатель",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Команда"
        verbose_name_plural = "Команды"

    def __str__(self):
        return self.name


class TeamMember(models.Model):
    ROLE_CHOICES = (
        ('member', 'Сотрудник'),
        ('manager', 'Менеджер'),
        ('admin', 'Администратор'),
    )

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='members',
        verbose_name="Команда"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='team_memberships',
        verbose_name="Пользователь"
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='member',
        verbose_name="Роль"
    )
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата вступления", null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['team', 'user'],
                name='unique_team_member'
            )
        ]
        verbose_name = "Участник команды"
        verbose_name_plural = "Участники команд"

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()}) в {self.team.name}"