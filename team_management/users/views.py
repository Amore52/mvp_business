from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.utils import timezone

from .forms import RegisterForm, UserEditForm, UserDeleteForm
from tasks.models import Task, TaskRating


def register_view(request):
    """
    Представление для регистрации нового пользователя.
    Если метод POST и форма валидна — регистрирует пользователя и перенаправляет на dashboard.
    """
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


class CustomLoginView(LoginView):
    """
    Кастомное представление входа пользователя в систему.
    Использует шаблон 'login.html'.
    Автоматически перенаправляет авторизованных пользователей.
    Поддерживает опцию "Запомнить меня".
    """
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        remember_me = self.request.POST.get('remember_me')
        if not remember_me:
            self.request.session.set_expiry(0)
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    """
    Кастомное представление выхода пользователя из системы.
    После выхода перенаправляет на страницу входа.
    """
    next_page = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

def dashboard_view(request):
    """
    Представление главной страницы (dashboard).
    """
    return render(request, 'dashboard.html')

@login_required
def profile_view(request):
    """
    Представление профиля пользователя.
    Отображает форму редактирования профиля, возможность удаления аккаунта,
    статистику оценок задач за месяц и общую информацию по выполненным задачам.
    """
    completed_tasks = Task.objects.filter(assignee=request.user, status='done')
    ratings = TaskRating.objects.filter(task__in=completed_tasks)
    last_month_avg = ratings.filter(
        rated_at__gte=timezone.now() - timedelta(days=30)
    ).aggregate(Avg('score'))['score__avg'] or 0
    if request.method == 'POST':
        if 'edit_profile' in request.POST:
            form = UserEditForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Профиль успешно обновлен')
                return redirect('profile')
        elif 'delete_profile' in request.POST:
            delete_form = UserDeleteForm(request.POST)
            if delete_form.is_valid():
                request.user.delete()
                logout(request)
                messages.success(request, 'Ваш аккаунт был успешно удален')
                return redirect('login')
    else:
        form = UserEditForm(instance=request.user)
        delete_form = UserDeleteForm()

    return render(request, 'profile.html', {
        'form': form,
        'delete_form': delete_form,
        'user': request.user,
        'total_ratings': ratings.count(),
        'average_rating': ratings.aggregate(Avg('score'))['score__avg'] or 0,
        'last_month_avg': round(last_month_avg, 2),
        'ratings': ratings.order_by('-rated_at')
    })