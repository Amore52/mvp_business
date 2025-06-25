from django import forms

from .models import Team, TeamMember, User


class TeamCreateForm(forms.ModelForm):
    """
    Форма для создания или редактирования команды (Team).
    Используется в представлениях создания и редактирования команд.
    """

    class Meta:
        model = Team
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class TeamMemberForm(forms.ModelForm):
    """
    Форма для добавления участника в команду (TeamMember).
    При инициализации принимает параметр `team`, чтобы исключить уже добавленных пользователей.
    """

    class Meta:
        model = TeamMember
        fields = ['user', 'role']

    def __init__(self, *args, **kwargs):
        team = kwargs.pop('team', None)
        super().__init__(*args, **kwargs)
        if team:
            existing_members = team.members.values_list('user_id', flat=True)
            self.fields['user'].queryset = User.objects.exclude(id__in=existing_members)
