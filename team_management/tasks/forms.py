from django import forms

from .models import Task, TaskRating


class TaskForm(forms.ModelForm):
    """
    Форма для создания и редактирования задачи.
    Используется в представлениях для отображения и валидации данных при создании/редактировании задач.
    """

    class Meta:
        model = Task
        fields = ['title', 'description', 'deadline', 'team']
        widgets = {
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class TaskRatingForm(forms.ModelForm):
    """
    Форма для оценки задачи (TaskRating).
    Оценка выбирается из выпадающего списка (1–5), комментарий — текстовое поле с 3 строками.
    Используется для оценки выполненных задач.
    """

    class Meta:
        model = TaskRating
        fields = ['score', 'comment']
        widgets = {
            'score': forms.Select(choices=[(i, str(i)) for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 3}),
        }
