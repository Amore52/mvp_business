from django.contrib.auth import get_user_model
from django.urls import reverse

from teams.models import Team, TeamMember

User = get_user_model()


def test_my_teams_view_get(authenticated_client):
    """
    Проверяет, что авторизованный пользователь может открыть страницу своих команд.
    """
    url = reverse('teams:my_teams')
    response = authenticated_client.get(url)
    assert response.status_code == 200
    assert 'created_teams' in response.context
    assert 'member_teams' in response.context


def test_team_create_success(authenticated_client):
    """
    Проверяет успешное создание новой команды.
    После создания команда принадлежит пользователю, он становится администратором.
    """
    url = reverse('teams:team_create')
    data = {
        'name': 'Новая команда',
        'description': 'Описание команды'
    }
    response = authenticated_client.post(url, data)
    assert response.status_code == 302
    team = Team.objects.get(name='Новая команда')
    assert team.created_by.username == 'testuser'
    assert TeamMember.objects.filter(team=team, user__username='testuser', role='admin').exists()


def test_team_detail_view(authenticated_client, db):
    """
    Проверяет, что детальная страница команды доступна владельцу.
    В контексте должны быть: команда, участники, форма и флаг is_admin.
    """
    user = User.objects.get(username='testuser')
    team = Team.objects.create(name='Тестовая команда', created_by=user)
    TeamMember.objects.create(team=team, user=user, role='admin')

    url = reverse('teams:team_detail', kwargs={'team_id': team.id})
    response = authenticated_client.get(url)

    assert response.status_code == 200
    assert 'team' in response.context
    assert 'members' in response.context
    assert 'member_form' in response.context
    assert 'is_admin' in response.context
    assert response.context['is_admin'] is True


def test_add_member_to_team_as_admin(authenticated_client, db):
    """
    Проверяет, что админ может добавить нового пользователя в команду.
    """
    user = User.objects.get(username='testuser')
    team = Team.objects.create(name='Тестовая команда', created_by=user)
    TeamMember.objects.create(team=team, user=user, role='admin')

    new_user = User.objects.create_user(username='newuser', password='password123')

    url = reverse('teams:team_detail', kwargs={'team_id': team.id})
    data = {'user': new_user.id}
    response = authenticated_client.post(url, data)

    assert response.status_code == 200


def test_remove_member_success(authenticated_client, db):
    """
    Проверяет, что админ может удалить участника из команды.
    """
    user = User.objects.get(username='testuser')
    team = Team.objects.create(name='Тестовая команда', created_by=user)
    TeamMember.objects.create(team=team, user=user, role='admin')

    other_user = User.objects.create_user(username='otheruser', password='password123')
    TeamMember.objects.create(team=team, user=other_user, role='member')

    url = reverse('teams:remove_member', kwargs={'team_id': team.id, 'user_id': other_user.id})
    response = authenticated_client.post(url)

    assert response.status_code == 302
    assert not TeamMember.objects.filter(team=team, user=other_user).exists()


def test_remove_member_not_admin(authenticated_client, db):
    """
    Проверяет, что не-админ не может удалить участника.
    Ожидается перенаправление и сообщение об ошибке.
    """
    user = User.objects.get(username='testuser')
    team = Team.objects.create(name='Тестовая команда', created_by=user)
    TeamMember.objects.create(team=team, user=user, role='member')  # не админ

    other_user = User.objects.create_user(username='otheruser', password='password123')
    TeamMember.objects.create(team=team, user=other_user, role='member')

    url = reverse('teams:remove_member', kwargs={'team_id': team.id, 'user_id': other_user.id})
    response = authenticated_client.post(url)

    assert response.status_code == 302
    messages = list(response.wsgi_request._messages)
    assert any("Недостаточно прав" in str(m) for m in messages)


def test_update_member_role(authenticated_client, db):
    """
    Проверяет, что админ может изменить роль участника.
    """
    user = User.objects.get(username='testuser')
    team = Team.objects.create(name='Тестовая команда', created_by=user)
    TeamMember.objects.create(team=team, user=user, role='admin')

    other_user = User.objects.create_user(username='otheruser', password='password123')
    member = TeamMember.objects.create(team=team, user=other_user, role='member')

    url = reverse('teams:update_member_role', kwargs={'team_id': team.id, 'user_id': other_user.id})
    data = {'role': 'manager'}
    authenticated_client.post(url, data)
    member.refresh_from_db()
    assert member.role == 'manager'


def test_update_member_role_invalid_role(authenticated_client, db):
    """
    Проверяет, что при попытке установить недопустимую роль,
    она остаётся без изменений.
    """
    user = User.objects.get(username='testuser')
    team = Team.objects.create(name='Тестовая команда', created_by=user)
    TeamMember.objects.create(team=team, user=user, role='admin')

    other_user = User.objects.create_user(username='otheruser', password='password123')
    member = TeamMember.objects.create(team=team, user=other_user, role='member')

    url = reverse('teams:update_member_role', kwargs={'team_id': team.id, 'user_id': other_user.id})
    data = {'role': 'invalid_role'}
    authenticated_client.post(url, data)

    member.refresh_from_db()
    assert member.role == 'member'


def test_team_update_view(authenticated_client, db):
    """
    Проверяет, что владелец может отредактировать информацию о команде.
    """
    user = User.objects.get(username='testuser')
    team = Team.objects.create(name='Старое название', created_by=user)

    url = reverse('teams:team_edit', kwargs={'pk': team.id})
    data = {'name': 'Новое название', 'description': 'Обновлённое описание'}
    response = authenticated_client.post(url, data)

    team.refresh_from_db()
    assert response.status_code == 302
    assert team.name == 'Новое название'


def test_team_delete_view(authenticated_client, db):
    """
    Проверяет, что владелец может удалить команду.
    """
    user = User.objects.get(username='testuser')
    team = Team.objects.create(name='Команда к удалению', created_by=user)

    url = reverse('teams:team_delete', kwargs={'pk': team.id})
    response = authenticated_client.post(url)

    assert response.status_code == 302
    assert not Team.objects.filter(id=team.id).exists()
