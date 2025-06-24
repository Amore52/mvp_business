# conftest.py
from datetime import timedelta

import factory
import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from tasks.models import Task, TaskRating
from teams.models import Team, TeamMember


@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(username='testuser', password='password123')


@pytest.fixture
def authenticated_client(client, user):
    client.login(username='testuser', password='password123')
    return client


@pytest.fixture
def user_factory():
    return UserFactory

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda o: f'{o.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'password123')


class TeamFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Team

    name = factory.Sequence(lambda n: f"Team {n}")
    description = factory.Faker("sentence")


class TeamMemberFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TeamMember

    user = factory.SubFactory(UserFactory)
    team = factory.SubFactory(TeamFactory)
    role = "member"


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task

    title = factory.Faker('sentence')
    description = factory.Faker('paragraph')
    assignee = factory.SubFactory(UserFactory)
    status = 'done'
    deadline = factory.LazyFunction(lambda: timezone.now() + timedelta(days=7))


class TaskRatingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TaskRating

    task = factory.SubFactory(TaskFactory)
    score = 5
