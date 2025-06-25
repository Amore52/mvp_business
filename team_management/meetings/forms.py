from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Meeting


class MeetingForm(forms.ModelForm):
    """
    Форма для создания и редактирования встречи (Meeting).
    """

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        meeting = super().save(commit=False)
        if commit:
            meeting.save()
            team_member = self.user.teammember_set.first()
            meeting.participants.add(team_member)
        return meeting

    class Meta:
        model = Meeting
        fields = ['title', 'description', 'date', 'time', 'duration', 'participants']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'duration': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        from .views import _check_time_conflict
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        duration = cleaned_data.get('duration')

        if date and time and duration:
            if date < timezone.now().date():
                raise ValidationError("Нельзя создать встречу в прошлом")

            if (date == timezone.now().date() and
                    time < timezone.now().time()):
                raise ValidationError("Нельзя создать встречу в прошедшем времени")
            for participant in cleaned_data.get('participants', []):
                if _check_time_conflict(
                        participant,
                        date,
                        time,
                        duration,
                        self.instance.id if self.instance else None
                ):
                    raise ValidationError(
                        f"У участника {participant.username} уже есть встреча в это время"
                    )

        return cleaned_data
