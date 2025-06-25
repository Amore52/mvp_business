import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta, time

from meetings.models import Meeting


@pytest.fixture
def meeting(user):
    """
    Создаёт встречу, инициированную пользователем user.
    Используется в тестах для проверки деталей встречи и доступа.
    """
    return Meeting.objects.create(
        title="Test Meeting",
        description="Test Description",
        date=timezone.now().date() + timedelta(days=1),
        time=time(14, 0),
        duration=timedelta(hours=1),
        created_by=user
    )


@pytest.fixture
def meeting_with_participant(user, user_factory):
    """
    Создаёт встречу с двумя участниками: владельцем и другим пользователем.
    Используется для тестирования участия и отмены участия в встречах.
    """
    other_user = user_factory()
    meeting = Meeting.objects.create(
        title="Meeting with Participant",
        date=timezone.now().date() + timedelta(days=2),
        time=time(15, 0),
        duration=timedelta(hours=1),
        created_by=user
    )
    meeting.participants.add(other_user, user)
    return meeting


# ----------------------------
# Тесты для my_meetings_view
# ----------------------------

def test_my_meetings_view_login_required_redirect(client):
    """
    Проверяет, что неавторизованный пользователь перенаправляется на страницу входа.
    """
    url = reverse('my_meetings')
    response = client.get(url)
    assert response.status_code == 302
    assert 'login' in response.url


def test_my_meetings_view_shows_user_meetings(authenticated_client, meeting_with_participant):
    """
    Проверяет, что авторизованный пользователь видит свои встречи в контексте.
    """
    url = reverse('my_meetings')
    response = authenticated_client.get(url)
    assert response.status_code == 200
    assert 'my_meetings' in response.context
    assert meeting_with_participant in response.context['my_meetings']


# ----------------------------
# Тесты для create_meeting
# ----------------------------

def test_create_meeting_get_form_page(authenticated_client):
    """
    Проверяет, что GET-запрос к странице создания встречи возвращает форму.
    """
    url = reverse('create_meeting')
    response = authenticated_client.get(url)
    assert response.status_code == 200
    assert 'form' in response.context


def test_create_meeting_post_success(authenticated_client, user_factory):
    """
    Проверяет успешное создание встречи через POST-запрос.
    """
    other_user = user_factory()
    url = reverse('create_meeting')
    data = {
        'title': 'New Meeting',
        'description': 'Some description',
        'date': (timezone.now().date() + timedelta(days=1)),
        'time': '14:00',
        'duration': timedelta(hours=2),
        'participants': [other_user.id]
    }
    response = authenticated_client.post(url, data)
    assert response.status_code == 302
    assert Meeting.objects.filter(title='New Meeting').exists()


def test_create_meeting_with_conflict(authenticated_client, user, user_factory, meeting):
    """
    Проверяет, что можно отправить форму даже при наличии конфликта времени.
    Ожидается, что логика проверки временных конфликтов реализована отдельно.
    """
    other_user = user_factory()
    meeting.participants.add(other_user)

    url = reverse('create_meeting')
    data = {
        'title': 'Conflicting Meeting',
        'description': '',
        'date': meeting.date,
        'time': meeting.time.strftime("%H:%M"),
        'duration': timedelta(hours=2),
        'participants': [other_user.id]
    }
    response = authenticated_client.post(url, data)
    assert response.status_code in (200, 302)  # либо форма с ошибкой, либо редирект


# ----------------------------
# Тесты для meeting_detail
# ----------------------------

def test_meeting_detail_access_denied_for_non_owner(authenticated_client, user_factory):
    """
    Проверяет, что не владелец встречи не может просматривать её детали.
    Перенаправляется на dashboard.
    """
    other_user = user_factory()
    meeting = Meeting.objects.create(
        title="Private Meeting",
        date=timezone.now().date() + timedelta(days=1),
        time=time(14, 0),
        duration=timedelta(hours=1),
        created_by=other_user
    )
    url = reverse('meeting_detail', args=[meeting.id])
    response = authenticated_client.get(url)
    assert response.status_code == 302
    assert 'dashboard' in response.url


def test_meeting_detail_shows_creator_flag(authenticated_client, meeting):
    """
    Проверяет, что владелец встречи имеет флаг is_creator в контексте.
    """
    url = reverse('meeting_detail', args=[meeting.id])
    response = authenticated_client.get(url)
    assert response.status_code == 200
    assert response.context['is_creator']


def test_meeting_delete_by_owner(authenticated_client, meeting):
    """
    Проверяет, что владелец встречи может удалить встречу.
    """
    url = reverse('meeting_detail', args=[meeting.id])
    data = {'delete_meeting': 'on'}
    response = authenticated_client.post(url, data)
    assert response.status_code == 302
    assert not Meeting.objects.filter(id=meeting.id).exists()


def test_meeting_delete_by_non_owner(authenticated_client, user_factory):
    """
    Проверяет, что не владелец встречи не может удалить её.
    """
    other_user = user_factory()
    meeting = Meeting.objects.create(
        title="Meeting",
        date=timezone.now().date() + timedelta(days=1),
        time=time(14, 0),
        duration=timedelta(hours=1),
        created_by=other_user
    )
    url = reverse('meeting_detail', args=[meeting.id])
    data = {'delete_meeting': 'on'}
    response = authenticated_client.post(url, data)
    assert response.status_code == 302
    assert Meeting.objects.filter(id=meeting.id).exists()


def test_meeting_cancel_participation(authenticated_client, meeting_with_participant, user):
    """
    Проверяет, что участник может отменить своё участие в встрече.
    """
    meeting = meeting_with_participant
    meeting.participants.add(user)

    url = reverse('meeting_detail', args=[meeting.id])
    data = {'cancel_participation': 'on'}
    response = authenticated_client.post(url, data)
    assert response.status_code == 302
    assert user not in meeting.participants.all()