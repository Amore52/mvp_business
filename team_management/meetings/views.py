from calendar import monthrange
from datetime import timedelta

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Meeting
from datetime import datetime, timedelta
from django.utils import timezone


@login_required
def dashboard_view(request):
    meeteng = Meeting.objects.filter(team=request.user.team)

    # Получаем параметры для календаря (если есть в GET-запросе)
    try:
        year = int(request.GET.get('year', timezone.now().year))
        month = int(request.GET.get('month', timezone.now().month))
        day = int(request.GET.get('day', timezone.now().day))
        selected_date = datetime(year, month, day).date()
    except:
        selected_date = timezone.now().date()
        year = selected_date.year
        month = selected_date.month
        day = selected_date.day

    # Фильтрация задач для выбранного дня
    daily_tasks = meeteng.filter(deadline__date=selected_date)

    # Генерация данных для календаря
    first_day = datetime(year, month, 1).date()
    last_day = datetime(year, month, monthrange(year, month)[1]).date()

    # Создаем словарь для подсчета задач по дням
    tasks_count = {}
    for meeteng in meetengs:
        day = meeteng.deadline.date()
        tasks_count[day] = tasks_count.get(day, 0) + 1

    # Генерируем календарь
    weeks = []
    current_date = first_day - timedelta(days=first_day.weekday())

    for _ in range(6):  # Максимум 6 недель в месяце
        week = []
        for _ in range(7):  # 7 дней в неделе
            week_day = {
                'date': current_date,
                'in_month': current_date.month == month,
                'tasks_count': tasks_count.get(current_date, 0),
                'is_today': current_date == timezone.now().date(),
                'is_selected': current_date == selected_date,
            }
            week.append(week_day)
            current_date += timedelta(days=1)
        weeks.append(week)

        if current_date > last_day:
            break

    context = {
        'tasks': meeteng.order_by('-created_at'),
        'daily_tasks': daily_tasks,
        'calendar': {
            'year': year,
            'month': month,
            'day': day,
            'selected_date': selected_date,
            'next_date': selected_date + timedelta(days=1),
            'prev_date': selected_date - timedelta(days=1),
            'next_month': month + 1 if month < 12 else 1,
            'next_year': year if month < 12 else year + 1,
            'prev_month': month - 1 if month > 1 else 12,
            'prev_year': year if month > 1 else year - 1,
            'weeks': weeks,
        }
    }
    return render(request, 'dashboard.html', context)

