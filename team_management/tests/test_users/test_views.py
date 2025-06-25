import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from users.forms import RegisterForm

User = get_user_model()


def test_register_view_get(client):
    """
    Проверяет, что страница регистрации доступна через GET-запрос.
    Ожидается статус 200 и наличие формы регистрации в контексте.
    """
    response = client.get(reverse('register'))
    assert response.status_code == 200
    assert 'form' in response.context
    assert isinstance(response.context['form'], RegisterForm)


@pytest.mark.django_db
def test_register_view_post_valid(client):
    """
    Проверяет успешную регистрацию пользователя с корректными данными.
    Ожидается редирект на dashboard и создание пользователя в БД.
    """
    data = {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password1': 'StrongPass123!',
        'password2': 'StrongPass123!'
    }
    response = client.post(reverse('register'), data)
    assert response.status_code == 302
    assert User.objects.filter(username='newuser').exists()
    assert reverse('dashboard') in response.url


@pytest.mark.django_db
def test_login_remember_me(authenticated_client, user):
    """
    Проверяет, что при входе с 'remember_me=True' сессия не истечёт после закрытия браузера.
    """
    url = reverse('login')
    data = {
        'username': user.username,
        'password': 'password123!',
        'remember_me': True
    }
    authenticated_client.post(url, data)
    assert '_auth_user_id' in authenticated_client.session
    assert authenticated_client.session.get_expiry_age() > 0


def test_dashboard_authenticated(authenticated_client):
    """
    Проверяет, что авторизованный пользователь может открыть страницу dashboard.
    Ожидается статус 200 и использование правильного шаблона.
    """
    response = authenticated_client.get(reverse('dashboard'))
    assert response.status_code == 200
    assert 'dashboard.html' in [t.name for t in response.templates]
