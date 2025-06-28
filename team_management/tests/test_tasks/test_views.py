from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.urls import reverse
from django.utils import timezone

from tasks.forms import TaskForm
from tasks.models import Task, Comment, TaskRating

User = get_user_model()


@pytest.fixture
def task(db, user, team):
    """Фикстура для создания тестовой задачи"""
    return Task.objects.create(
        title='Test Task',
        description='Test Description',
        deadline=timezone.now() + timedelta(days=7),
        status='open',
        assignee=user,
        team=team
    )


def test_my_tasks_view_unauthenticated(client):
    """Неавторизованный пользователь перенаправляется на страницу входа"""
    response = client.get(reverse('my_tasks'))
    assert response.status_code == 302
    assert '/accounts/login/' in response.url


def test_my_tasks_view_authenticated(authenticated_client, task):
    """Авторизованный пользователь видит свои задачи"""
    response = authenticated_client.get(reverse('my_tasks'))
    assert response.status_code == 200
    assert b'Test Task' in response.content


# Тесты для task_detail_view
def test_task_detail_view_access(authenticated_client, task):
    """Пользователь может просматривать назначенные ему задачи"""
    response = authenticated_client.get(reverse('task_detail', args=[task.id]))
    assert response.status_code == 200
    assert b'Test Task' in response.content


def test_task_detail_view_no_access(authenticated_client,  team):
    """Пользователь не может просматривать чужие задачи"""
    other_user = User.objects.create_user(username='other', password='pass123')
    task = Task.objects.create(
        title='Test Task',
        description='Test Description',
        deadline=timezone.now() + timedelta(days=7),
        status='open',
        assignee=other_user,
        team=team
    )

    response = authenticated_client.get(reverse('task_detail', args=[task.id]))
    assert response.status_code == 403


# Тесты для create_task_view
def test_create_task_view_get(authenticated_client, user, team_member):
    """GET-запрос возвращает форму"""
    response = authenticated_client.get(reverse('create_task'))
    assert response.status_code == 200
    assert isinstance(response.context['form'], TaskForm)


def test_create_task_view_post_valid(authenticated_client, user, team):
    """Успешное создание задачи"""
    data = {
        'title': 'New Task',
        'description': 'New Description',
        'deadline': (timezone.now() + timedelta(days=5)).strftime('%Y-%m-%dT%H:%M'),
        'status': 'open',
        'assignee': user.id,
        'team': team.id
    }
    response = authenticated_client.post(reverse('create_task'), data)
    assert response.status_code == 302
    assert Task.objects.filter(title='New Task').exists()


def test_update_task_status(authenticated_client, task):
    """Пользователь может обновить статус своей задачи"""
    response = authenticated_client.post(
        reverse('task_detail', args=[task.id]),
        {'status': 'in_progress'}
    )
    assert response.status_code == 302
    task.refresh_from_db()
    assert task.status == 'in_progress'


def test_add_comment(authenticated_client, task):
    """Пользователь может добавить комментарий"""
    response = authenticated_client.post(
        reverse('task_detail', args=[task.id]),
        {'add_comment': '', 'comment_text': 'Test comment'}
    )
    assert response.status_code == 302
    assert Comment.objects.filter(text='Test comment').exists()


def test_add_empty_comment(authenticated_client, task):
    """Нельзя добавить пустой комментарий"""
    response = authenticated_client.post(
        reverse('task_detail', args=[task.id]),
        {'add_comment': '', 'comment_text': ''}
    )
    assert response.status_code == 302
    messages = list(get_messages(response.wsgi_request))
    assert str(messages[0]) == "Комментарий не может быть пустым"


def test_rate_task_admin(admin_client, team):
    """Админ может оценить завершенную задачу"""
    task = Task.objects.create(
        title='Done Task',
        description='Task Description',
        deadline=timezone.now() + timedelta(days=7),
        status='done',
        assignee=None,
        team=team
    )

    response = admin_client.post(
        reverse('task_detail', args=[task.id]),
        {'rate_task': '', 'score': 5, 'comment': 'Good job!'}
    )
    assert response.status_code == 302
    assert TaskRating.objects.filter(task=task).exists()


def test_rate_task_non_admin(authenticated_client, user, team):
    """Обычный пользователь не может оценить задачу"""
    task = Task.objects.create(
        title='Done Task',
        description='Task Description',
        deadline=timezone.now() + timedelta(days=7),
        status='done',
        assignee=None,
        team=team
    )

    response = authenticated_client.post(
        reverse('task_detail', args=[task.id]),
        {'rate_task': '', 'score': 5, 'comment': 'Good job!'}
    )
    assert response.status_code == 403
    assert not TaskRating.objects.filter(task=task).exists()
    messages = list(get_messages(response.wsgi_request))
    assert str(messages[0]) == "У вас нет доступа к этой задаче"


def test_rate_unfinished_task(admin_client, team):
    """Нельзя оценить незавершенную задачу"""
    task = Task.objects.create(
        title='In Progress Task',
        description='Task Description',
        deadline=timezone.now() + timedelta(days=7),
        status='in_progress',
        assignee=None,
        team=team
    )

    response = admin_client.post(
        reverse('task_detail', args=[task.id]),
        {'rate_task': '', 'score': 5, 'comment': 'Good job!'}
    )
    assert response.status_code == 302
    assert not TaskRating.objects.filter(task=task).exists()
    messages = list(get_messages(response.wsgi_request))
    assert str(messages[0]) == "Можно оценивать только завершенные задачи"
