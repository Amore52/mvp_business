from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy

from .forms import RegisterForm

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'login.html'  # ваш кастомный шаблон
    redirect_authenticated_user = True  # перенаправлять уже авторизованных пользователей
    success_url = reverse_lazy('dashboard')  # куда перенаправлять после успешного входа

    def form_valid(self, form):
        """Дополнительные действия при успешном входе"""
        remember_me = self.request.POST.get('remember_me')
        if not remember_me:
            # Устанавливаем сессию на время закрытия браузера, если не стоит "запомнить меня"
            self.request.session.set_expiry(0)
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')  # куда перенаправлять после выхода

    def dispatch(self, request, *args, **kwargs):
        """Дополнительные действия перед выходом"""
        # Можно добавить логирование выхода или другие действия
        return super().dispatch(request, *args, **kwargs)

def dashboard_view(request):
    return render(request, 'dashboard.html')