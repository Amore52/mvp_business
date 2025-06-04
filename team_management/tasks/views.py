from calendar import monthrange
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from teams.models import TeamMember
from users.models import User

from .forms import TaskForm
from .models import Task


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
    daily_tasks = tasks.filter(deadline__date=selected_date)
    first_day = datetime(year, month, 1).date()
    last_day = datetime(year, month, monthrange(year, month)[1]).date()
    tasks_count = {}
    for task in tasks:
        day = task.deadline.date()
        tasks_count[day] = tasks_count.get(day, 0) + 1
    weeks = []
    current_date = first_day - timedelta(days=first_day.weekday())

    for _ in range(6):
        week = []
        for _ in range(7):
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
    my_tasks = Task.objects.filter(
        team=request.user.team,
        assignee=request.user
    ).select_related('assignee')

    context = {
        'my_tasks': my_tasks.order_by('-created_at'),
    }
    return render(request, 'tasks/my_tasks.html', context)


@login_required
def task_detail_view(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    _check_task_access(request, task)

    if request.method == 'POST':
        if 'delete_task' in request.POST:
            return _handle_delete_task(request, task)
        elif 'status' in request.POST:
            return _handle_status_update(request, task)
        else:
            return _handle_task_edit(request, task)

    context = _prepare_task_context(request, task)
    return render(request, 'tasks/task_detail.html', context)


def _check_task_access(request, task):
    """Проверка прав доступа к задаче"""
    if not (request.user.is_staff or request.user == task.assignee):
        messages.error(request, "У вас нет доступа к этой задаче")
        raise PermissionDenied


def _handle_delete_task(request, task):
    """Обработка удаления задачи"""
    if not request.user.is_staff:
        messages.error(request, "Только администратор может удалять задачи")
        return redirect('task_detail', task_id=task.id)
    task.delete()
    messages.success(request, "Задача успешно удалена")
    return redirect('dashboard')


def _handle_status_update(request, task):
    """Обновление статуса задачи"""
    if not (request.user.is_staff or request.user == task.assignee):
        messages.error(request, "Вы не можете изменять статус этой задачи")
        return redirect('task_detail', task_id=task.id)
    task.status = request.POST['status']
    task.save()
    messages.success(request, "Статус задачи обновлен")
    return redirect('task_detail', task_id=task.id)


def _handle_task_edit(request, task):
    """Редактирование задачи"""
    if not request.user.is_staff:
        messages.error(request, "Вы не можете редактировать эту задачу")
        return redirect('task_detail', task_id=task.id)
    task.title = request.POST.get('title', task.title)
    task.description = request.POST.get('description', task.description)
    deadline_str = request.POST.get('deadline')
    if deadline_str:
        try:
            task.deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            messages.error(request, "Неверный формат даты")
            return redirect('task_detail', task_id=task.id)
    assignee_id = request.POST.get('assignee')
    if assignee_id == '':
        task.assignee = None
        messages.success(request, "Исполнитель удалён")
    elif assignee_id:
        try:
            assignee = User.objects.get(id=assignee_id)
            if TeamMember.objects.filter(user=assignee, team=task.team).exists():
                task.assignee = assignee
                messages.success(request, f"Исполнитель {assignee.username} назначен")
            else:
                messages.error(request, "Этот пользователь не в вашей команде")
                return redirect('task_detail', task_id=task.id)
        except User.DoesNotExist:
            messages.error(request, "Пользователь не найден")
            return redirect('task_detail', task_id=task.id)

    task.save()
    return redirect('task_detail', task_id=task.id)


def _prepare_task_context(request, task):
    """Подготовка контекста для шаблона"""
    team_members = User.objects.filter(team_memberships__team=task.team) if task.team else User.objects.none()
    return {
        'task': task,
        'status_choices': Task.STATUS_CHOICES,
        'team_members': team_members,
        'can_edit': request.user.is_staff,
        'can_delete': request.user.is_staff,
        'can_change_status': request.user.is_staff or request.user == task.assignee,
    }


@login_required
def create_task_view(request):
    """Создание таски"""
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.save()
            messages.success(request, "Задача успешно создана")
            return redirect('task_detail', task_id=task.id)
    else:
        form = TaskForm()

    return render(request, 'tasks/create_task.html', {
        'form': form,
        'teams': request.user.team_memberships.all()
    })
