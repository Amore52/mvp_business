from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import UpdateView, DeleteView

from .models import Team, TeamMember
from .forms import TeamCreateForm, TeamMemberForm


@login_required
def my_teams(request):
    """
    Представление для отображения команд текущего пользователя:
        - Команды, созданные пользователем (created_teams)
        - Команды, в которых пользователь состоит как участник (member_teams)
    """
    created_teams = Team.objects.filter(created_by=request.user)
    member_teams = Team.objects.filter(
        members__user=request.user
    ).exclude(
        created_by=request.user
    ).distinct()

    return render(request, 'teams/my_teams.html', {
        'created_teams': created_teams,
        'member_teams': member_teams
    })

@login_required
def team_create(request):
    """
    Представление для создания новой команды.
    Если метод POST и форма валидна — создаёт команду и назначает создателя администратором.
    Перенаправляет на страницу деталей команды.
    """
    if request.method == 'POST':
        form = TeamCreateForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.created_by = request.user
            team.save()
            TeamMember.objects.create(team=team, user=request.user, role='admin')
            messages.success(request, 'Команда успешно создана!')
            return redirect('teams:team_detail', team_id=team.id)
    else:
        form = TeamCreateForm()
    return render(request, 'teams/team_create.html', {'form': form})


@login_required
def team_detail(request, team_id):
    """
    Представление для отображения детальной информации о команде.
    Только участники команды могут просматривать её.
    Администратор может добавлять новых участников через форму.
    """
    team = get_object_or_404(Team, id=team_id)
    members = team.members.select_related('user')

    is_admin = team.members.filter(user=request.user, role='admin').exists()

    if request.method == 'POST' and is_admin:
        member_form = TeamMemberForm(request.POST, team=team)
        if member_form.is_valid():
            member = member_form.save(commit=False)
            member.team = team
            member.save()
            messages.success(request, 'Пользователь добавлен в команду!')
            return redirect('teams:team_detail', team_id=team.id)
    else:
        member_form = TeamMemberForm(team=team)

    context = {
        'team': team,
        'members': members,
        'member_form': member_form,
        'is_admin': is_admin,
    }
    return render(request, 'teams/team_detail.html', context)

@login_required
def remove_member(request, team_id, user_id):
    """
    Представление для удаления участника из команды.
    Доступно только администраторам команды.
    """
    team = get_object_or_404(Team, id=team_id)
    if team.members.filter(user=request.user, role='admin').exists():
        member = get_object_or_404(TeamMember, team=team, user_id=user_id)
        member.delete()
        messages.success(request, 'Пользователь удалён из команды')
    else:
        messages.error(request, 'Недостаточно прав')
    return redirect('teams:team_detail', team_id=team.id)


@login_required
def update_member_role(request, team_id, user_id):
    """
    Представление для изменения роли участника команды.
    Доступно только администраторам команды.
    """
    team = get_object_or_404(Team, id=team_id)
    if team.members.filter(user=request.user, role='admin').exists():
        member = get_object_or_404(TeamMember, team=team, user__id=user_id)
        if request.method == 'POST':
            new_role = request.POST.get('role')
            if new_role in dict(TeamMember.ROLE_CHOICES).keys():
                member.role = new_role
                member.save()
                messages.success(request, 'Роль обновлена')
        else:
            messages.error(request, 'Неверный запрос')
    else:
        messages.error(request, 'Недостаточно прав')
    return redirect('teams:team_detail', team_id=team.id)


class TeamUpdateView(UpdateView):
    """
    Класс-представление для редактирования информации о команде.
    Использует форму `TeamCreateForm` и шаблон `teams/team_edit.html`.
    После успешного редактирования перенаправляет на страницу деталей команды.
    """
    model = Team
    form_class = TeamCreateForm
    template_name = 'teams/team_edit.html'
    pk_url_kwarg = 'pk'

    def get_success_url(self):
        return reverse_lazy('teams:team_detail', kwargs={'team_id': self.object.id})


class TeamDeleteView(DeleteView):
    """
     Класс-представление для удаления команды.
     Отображает страницу подтверждения удаления.
     Удаление доступно только владельцу команды.
     После удаления перенаправляет на dashboard.
     """
    model = Team
    template_name = 'teams/team_confirm_delete.html'
    success_url = reverse_lazy('dashboard')
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        return super().get_queryset().filter(created_by=self.request.user)