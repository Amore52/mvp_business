from datetime import time, timedelta

import pytest
from django.utils import timezone

from meetings.forms import MeetingForm


@pytest.fixture
def valid_form_data(user):
    """
    Возвращает валидные данные для формы встречи.
    Используется в тестах, проверяющих корректное поведение формы.
    """
    now = timezone.now()
    future_date = now.date() + timedelta(days=1)
    start_time = time(10, 0)
    duration = timedelta(hours=1)

    return {
        'title': 'Test Meeting',
        'description': 'This is a test meeting.',
        'date': future_date,
        'time': start_time,
        'duration': duration,
        'participants': [user.id],
    }


def test_valid_meeting_form(valid_form_data, user):
    """
    Проверяет, что форма валидна при корректных данных.
    """
    form = MeetingForm(data=valid_form_data, user=user)
    assert form.is_valid(), form.errors


def test_meeting_cannot_be_in_past(user):
    """
    Проверяет, что нельзя создать встречу на прошедшую дату.
    """
    past_date = timezone.now().date() - timedelta(days=1)
    data = {
        'title': 'Past Meeting',
        'description': '',
        'date': past_date,
        'time': time(10, 0),
        'duration': timedelta(hours=1),
        'participants': [user.id]
    }
    form = MeetingForm(data=data, user=user)
    assert not form.is_valid()
    assert '__all__' in form.errors
    assert any("Нельзя создать встречу в прошлом" in str(e) for e in form.errors['__all__'])


def test_meeting_cannot_start_in_past_today(user):
    """
    Проверяет, что нельзя создать встречу на сегодня, но во времени, которое уже прошло.
    """
    today = timezone.now().date()
    past_time = (timezone.now() - timedelta(hours=1)).time()
    data = {
        'title': 'Today Past Time Meeting',
        'description': '',
        'date': today,
        'time': past_time,
        'duration': timedelta(hours=1),
        'participants': [user.id]
    }
    form = MeetingForm(data=data, user=user)
    assert not form.is_valid()
    assert '__all__' in form.errors
    assert any("Нельзя создать встречу в прошедшем времени" in str(e) for e in form.errors['__all__'])
