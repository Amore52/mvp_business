from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Task


@login_required
def dashboard_view(request):
    tasks = Task.objects.all()
    context = {
        'tasks': tasks.order_by('-created_at'),
    }
    return render(request, 'dashboard.html', context)


@login_required
def my_tasks_view(request):
    # Только задачи, назначенные текущему пользователю
    my_tasks = Task.objects.filter(
        team=request.user.team,
        assignee=request.user
    ).select_related('assignee', 'created_by')

    context = {
        'my_tasks': my_tasks.order_by('-created_at'),
    }
    return render(request, 'my_tasks.html', context)