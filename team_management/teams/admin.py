from django.contrib import admin
from .models import Team, TeamMember

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Только при создании
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
        if not obj.members.filter(user=request.user).exists():
            TeamMember.objects.create(team=obj, user=request.user, role='admin')

admin.site.register(TeamMember)