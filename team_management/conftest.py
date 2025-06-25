from datetime import timedelta, time

import factory
import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from tasks.models import Task, TaskRating
from teams.models import Team, TeamMember, User


@pytest.fixture
def admin_user(db):
    """Фикстура для создания администратора"""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123'
    )


@pytest.fixture
def admin_client(client, admin_user):
    """Фикстура для авторизованного администратора"""
    client.login(username='admin', password='adminpass123')
    return client


@pytest.fixture
def user(db):
    """
    Фикстура создаёт тестового пользователя с username='testuser' и паролем 'password123'.
    Используется в тестах, где нужен конкретный залогиненный пользователь.
    """
    User = get_user_model()
    return User.objects.create_user(username='testuser', password='password123')


@pytest.fixture
def authenticated_client(client, user):
    """
    Фикстура возвращает клиент, авторизованный как пользователь из фикстуры `user`.
    Используется для тестирования view, требующих аутентификации.
    """
    client.login(username='testuser', password='password123')
    return client


@pytest.fixture
def team(db, user):
    """Фикстура для создания тестовой команды с создателем"""
    return Team.objects.create(name='Test Team', created_by=user)


@pytest.fixture
def team_member(db, user, team):
    """Фикстура для добавления пользователя в команду"""
    return TeamMember.objects.create(user=user, team=team)


@pytest.fixture
def user_factory():
    """
    Фикстура предоставляет класс UserFactory для создания тестовых пользователей.
    Можно использовать для генерации множества пользователей с уникальными именами.
    """
    return UserFactory

class UserFactory(factory.django.DjangoModelFactory):
    """
    Фабрика для создания пользователей.
    Генерирует уникальные username и email, устанавливает один и тот же пароль для всех.
    """
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda o: f'{o.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'password123')


class TeamFactory(factory.django.DjangoModelFactory):
    """
    Фабрика для создания команд.
    Генерирует уникальное имя и случайное описание для каждой команды.
    """
    class Meta:
        model = Team

    name = factory.Sequence(lambda n: f"Team {n}")
    description = factory.Faker("sentence")


class TeamMemberFactory(factory.django.DjangoModelFactory):
    """
    Фабрика для создания участников команды.
    Связывает случайного пользователя с командой, устанавливает роль по умолчанию — 'member'.
    """
    class Meta:
        model = TeamMember

    user = factory.SubFactory(UserFactory)
    team = factory.SubFactory(TeamFactory)
    role = "member"


class TaskFactory(factory.django.DjangoModelFactory):
    """
    Фабрика для создания задач.
    Создаёт задачи со случайным заголовком и описанием, назначает исполнителя,
    устанавливает статус 'done' и дедлайн через 7 дней от текущего времени.
    """
    class Meta:
        model = Task

    title = factory.Faker('sentence')
    description = factory.Faker('paragraph')
    assignee = factory.SubFactory(UserFactory)
    status = 'done'
    deadline = factory.LazyFunction(lambda: timezone.now() + timedelta(days=7))


class TaskRatingFactory(factory.django.DjangoModelFactory):
    """
    Фабрика для создания оценок задач.
    Связывает оценку с задачей, устанавливает фиксированную оценку 5.
    """
    class Meta:
        model = TaskRating

    task = factory.SubFactory(TaskFactory)
    score = 5


