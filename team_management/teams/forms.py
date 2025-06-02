from django import forms
from .models import Team, TeamMember, User


class TeamCreateForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class TeamMemberForm(forms.ModelForm):
    class Meta:
        model = TeamMember
        fields = ['user', 'role']

    def __init__(self, *args, **kwargs):
        team = kwargs.pop('team', None)
        super().__init__(*args, **kwargs)
        if team:
            # Исключаем пользователей, уже входящих в команду
            existing_members = team.members.values_list('user_id', flat=True)
            self.fields['user'].queryset = User.objects.exclude(id__in=existing_members)