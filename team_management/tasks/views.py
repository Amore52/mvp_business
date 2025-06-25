from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect

from teams.models import TeamMember
from users.models import User
from .forms import TaskForm, TaskRatingForm
from .models import Task, Comment


@login_required
def my_tasks_view(request):
    """
    Представление для отображения задач, назначенных текущему пользователю.
    """
    my_tasks = Task.objects.filter(assignee=request.user).select_related('assignee', 'team')

    context = {
        'my_tasks': my_tasks.order_by('-created_at'),
    }
    return render(request, 'tasks/my_tasks.html', context)


@login_required
def task_detail_view(request, task_id):
    """
    Представление для отображения деталей задачи и управления ею.
    """
    task = get_object_or_404(Task, id=task_id)
    _check_task_access(request, task)

    if request.method == 'POST':
        if 'delete_task' in request.POST:
            return _handle_delete_task(request, task)
        elif 'status' in request.POST:
            return _handle_status_update(request, task)
        elif 'add_comment' in request.POST:
            return _handle_add_comment(request, task)
        elif 'delete_comment' in request.POST:
            return _handle_delete_comment(request, task)
        elif 'edit_comment' in request.POST:
            return _handle_edit_comment(request, task)
        elif 'rate_task' in request.POST:
            return _handle_task_rating(request, task)
        else:
            return _handle_task_edit(request, task)

    context = _prepare_task_context(request, task)
    return render(request, 'tasks/task_detail.html', context)


def _check_task_access(request, task):
    """
    Проверяет, имеет ли пользователь доступ к задаче.
    Если нет — вызывает PermissionDenied и выводит сообщение об ошибке.
    """
    if not (request.user.is_staff or request.user == task.assignee):
        messages.error(request, "У вас нет доступа к этой задаче")
        raise PermissionDenied


def _handle_delete_task(request, task):
    """
    Обработчик удаления задачи.
    Право удаления есть только у администратора.
    """
    if not request.user.is_staff:
        messages.error(request, "Только администратор может удалять задачи")
        return redirect('task_detail', task_id=task.id)
    task.delete()
    messages.success(request, "Задача успешно удалена")
    return redirect('dashboard')


def _handle_task_edit(request, task):
    """
    Обработчик редактирования задачи.
    Право редактирования есть только у администратора.
    """
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


def _handle_add_comment(request, task):
    """
    Обработчик добавления комментария к задаче.
    """
    text = request.POST.get('comment_text', '').strip()
    if not text:
        messages.error(request, "Комментарий не может быть пустым")
        return redirect('task_detail', task_id=task.id)

    Comment.objects.create(
        task=task,
        author=request.user,
        text=text
    )
    messages.success(request, "Комментарий добавлен")
    return redirect('task_detail', task_id=task.id)


def _handle_edit_comment(request, task):
    """
    Обработчик редактирования комментария к задаче.
    Редактировать может автор комментария или администратор.
    """
    comment_id = request.POST.get('comment_id')
    new_text = request.POST.get('comment_text', '').strip()

    if not new_text:
        messages.error(request, "Комментарий не может быть пустым")
        return redirect('task_detail', task_id=task.id)

    try:
        comment = Comment.objects.get(id=comment_id, task=task)
        if comment.author == request.user or request.user.is_staff:
            comment.text = new_text
            comment.save()
            messages.success(request, "Комментарий обновлен")
        else:
            messages.error(request, "Вы не можете редактировать этот комментарий")
    except Comment.DoesNotExist:
        messages.error(request, "Комментарий не найден")

    return redirect('task_detail', task_id=task.id)


def _handle_delete_comment(request, task):
    """
     Обработчик удаления комментария к задаче.
     Удалить может автор комментария или администратор.
     """
    comment_id = request.POST.get('comment_id')
    try:
        comment = Comment.objects.get(id=comment_id, task=task)
        if comment.author == request.user or request.user.is_staff:
            comment.delete()
            messages.success(request, "Комментарий удален")
        else:
            messages.error(request, "Вы не можете удалить этот комментарий")
    except Comment.DoesNotExist:
        messages.error(request, "Комментарий не найден")
    return redirect('task_detail', task_id=task.id)


@login_required
def create_task_view(request):
    """
    Представление для создания новой задачи.
    """
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


@login_required
def rate_task(request, task_id):
    """
    Представление для оценки завершённой задачи.
    """
    task = get_object_or_404(Task, id=task_id)

    if not request.user.is_staff:
        raise PermissionDenied("Только администратор может оценивать задачи")

    if task.status != 'done':
        messages.error(request, "Можно оценивать только завершенные задачи")
        return redirect('task_detail', task_id=task.id)

    if request.method == 'POST':
        form = TaskRatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.task = task
            rating.rated_by = request.user
            rating.save()
            messages.success(request, "Оценка сохранена")
            return redirect('task_detail', task_id=task.id)
    else:
        form = TaskRatingForm()

    return render(request, 'tasks/task_detail.html', {
        'form': form,
        'task': task
    })


def _handle_status_update(request, task):
    """
    Обработчик изменения статуса задачи.
    Право изменять статус есть у администратора или исполнителя.
    """
    if not (request.user.is_staff or request.user == task.assignee):
        messages.error(request, "Вы не можете изменять статус этой задачи")
        return redirect('task_detail', task_id=task.id)

    new_status = request.POST['status']
    task.status = new_status
    task.save()
    messages.success(request, "Статус задачи обновлен")
    return redirect('task_detail', task_id=task.id)


def _handle_task_rating(request, task):
    """
    Обработчик сохранения оценки задачи.
    Право оценивать есть только у администратора.
    Задача должна быть завершена.
    """
    if not request.user.is_staff:
        messages.error(request, "Только администратор может оценивать задачи")
        return redirect('task_detail', task_id=task.id)

    if task.status != 'done':
        messages.error(request, "Можно оценивать только завершенные задачи")
        return redirect('task_detail', task_id=task.id)

    form = TaskRatingForm(request.POST)
    if form.is_valid():
        rating = form.save(commit=False)
        rating.task = task
        rating.rated_by = request.user
        rating.save()
        messages.success(request, "Оценка сохранена")
    else:
        messages.error(request, "Ошибка при сохранении оценки")

    return redirect('task_detail', task_id=task.id)


def _prepare_task_context(request, task):
    """
    Подготавливает контекст для отображения страницы задачи.
    """
    team_members = User.objects.filter(team_memberships__team=task.team) if task.team else User.objects.none()
    existing_rating = task.ratings.filter(rated_by=request.user).first() if hasattr(task, 'ratings') else None

    return {
        'task': task,
        'status_choices': Task.STATUS_CHOICES,
        'team_members': team_members,
        'can_edit': request.user.is_staff,
        'can_delete': request.user.is_staff,
        'can_change_status': request.user.is_staff or request.user == task.assignee,
        'can_rate': request.user.is_staff and task.status == 'done',
        'existing_rating': existing_rating,
        'rating_form': TaskRatingForm(instance=existing_rating),
        'comments': task.comments.all().select_related('author'),
    }
