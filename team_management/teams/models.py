from django.db import models

from users.models import User


class Team(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=6, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class TeamMember(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=User.ROLE_CHOICES)

    def __str__(self):
        return f"{self.user} - {self.role}"