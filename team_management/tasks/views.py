from calendar import monthrange
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Task
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib import messages

@login_required
def dashboard_view(request):
    tasks = Task.objects.all()
    try:
        year = int(request.GET.get('year', timezone.now().year))
        month = int(request.GET.get('month', timezone.now().month))
        day = int(request.GET.get('day', timezone.now().day))
        selected_date = datetime(year, month, day).date()
    except:
        selected_date = timezone.now().date()
        year = selected_date.year
        month = selected_date.month
        day = selected_date.day

    # Фильтрация задач для выбранного дня
    daily_tasks = tasks.filter(deadline__date=selected_date)

    # Генерация данных для календаря
    first_day = datetime(year, month, 1).date()
    last_day = datetime(year, month, monthrange(year, month)[1]).date()

    # Создаем словарь для подсчета задач по дням
    tasks_count = {}
    for task in tasks:
        day = task.deadline.date()
        tasks_count[day] = tasks_count.get(day, 0) + 1

    # Генерируем календарь
    weeks = []
    current_date = first_day - timedelta(days=first_day.weekday())

    for _ in range(6):  # Максимум 6 недель в месяце
        week = []
        for _ in range(7):  # 7 дней в неделе
            week_day = {
                'date': current_date,
                'in_month': current_date.month == month,
                'tasks_count': tasks_count.get(current_date, 0),
                'is_today': current_date == timezone.now().date(),
                'is_selected': current_date == selected_date,
            }
            week.append(week_day)
            current_date += timedelta(days=1)
        weeks.append(week)

        if current_date > last_day:
            break

    context = {
        'tasks': tasks.order_by('-created_at'),
        'daily_tasks': daily_tasks,
        'calendar': {
            'year': year,
            'month': month,
            'day': day,
            'selected_date': selected_date,
            'next_date': selected_date + timedelta(days=1),
            'prev_date': selected_date - timedelta(days=1),
            'next_month': month + 1 if month < 12 else 1,
            'next_year': year if month < 12 else year + 1,
            'prev_month': month - 1 if month > 1 else 12,
            'prev_year': year if month > 1 else year - 1,
            'weeks': weeks,
        }
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


@login_required
def task_detail_view(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    # Проверяем, имеет ли пользователь доступ к задаче
    if not (request.user.is_staff or request.user == task.assignee or request.user == task.created_by):
        messages.error(request, "У вас нет доступа к этой задаче")
        return redirect('dashboard')

    if request.method == 'POST':
        # Обновление статуса задачи
        if 'status' in request.POST and (request.user.is_staff or request.user == task.assignee):
            task.status = request.POST['status']
            task.save()
            messages.success(request, "Статус задачи обновлен")
            return redirect('task_detail', task_id=task.id)

        # Редактирование задачи (только для админа или создателя)
        if request.user.is_staff or request.user == task.created_by:
            task.title = request.POST.get('title', task.title)
            task.description = request.POST.get('description', task.description)
            task.deadline = request.POST.get('deadline', task.deadline)
            assignee_id = request.POST.get('assignee')
            if assignee_id:
                task.assignee_id = assignee_id
            task.save()
            messages.success(request, "Задача обновлена")
            return redirect('task_detail', task_id=task.id)

    context = {
        'task': task,
        'status_choices': Task.STATUS_CHOICES,
        'team_members': task.team.members.all() if task.team else [],
    }
    return render(request, 'task_detail.html', context)