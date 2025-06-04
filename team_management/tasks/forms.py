from django import forms
from .models import Task, TaskRating


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'deadline', 'team']
        widgets = {
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class TaskRatingForm(forms.ModelForm):
    class Meta:
        model = TaskRating
        fields = ['score', 'comment']
        widgets = {
            'score': forms.Select(choices=[(i, str(i)) for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 3}),
        }