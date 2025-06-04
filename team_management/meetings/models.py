from django.db import models

from teams.models import Team
from users.models import User


class Meeting(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date = models.DateField()
    time = models.TimeField()
    duration = models.DurationField(default="01:00")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)
    participants = models.ManyToManyField(User)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_meetings')

    def __str__(self):
        return self.title