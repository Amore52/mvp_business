import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from users.forms import RegisterForm

User = get_user_model()


def test_register_view_get(client):
    response = client.get(reverse('register'))
    assert response.status_code == 200
    assert 'form' in response.context
    assert isinstance(response.context['form'], RegisterForm)


@pytest.mark.django_db
def test_register_view_post_valid(client):
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
    response = authenticated_client.get(reverse('dashboard'))
    assert response.status_code == 200
    assert 'dashboard.html' in [t.name for t in response.templates]
