from calendar import monthrange
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone

from meetings.models import Meeting
from tasks.models import Task


@login_required
def dashboard_view(request):
    # Получаем задачи
    tasks = Task.objects.all()

    today = timezone.now().date()
    meetings = Meeting.objects.all()

    # Обработка даты для календаря
    try:
        year = int(request.GET.get('year', today.year))
        month = int(request.GET.get('month', today.month))
        day = int(request.GET.get('day', today.day))
        selected_date = datetime(year, month, day).date()
    except:
        selected_date = today

    # Ежедневные задачи и встречи
    daily_tasks = tasks.filter(deadline__date=selected_date)
    daily_meetings = meetings.filter(date=selected_date)

    # Подготовка данных для календаря
    first_day = datetime(year, month, 1).date()
    last_day = datetime(year, month, monthrange(year, month)[1]).date()

    tasks_count = {}
    meetings_count = {}

    for task in tasks:
        day = task.deadline.date()
        tasks_count[day] = tasks_count.get(day, 0) + 1

    for meeting in meetings:
        day = meeting.date
        meetings_count[day] = meetings_count.get(day, 0) + 1

    weeks = []
    current_date = first_day - timedelta(days=first_day.weekday())

    for _ in range(6):
        week = []
        for _ in range(7):
            week_day = {
                'date': current_date,
                'in_month': current_date.month == month,
                'tasks_count': tasks_count.get(current_date, 0),
                'meetings_count': meetings_count.get(current_date, 0),
                'is_today': current_date == today,
                'is_selected': current_date == selected_date,
            }
            week.append(week_day)
            current_date += timedelta(days=1)
        weeks.append(week)
        if current_date > last_day:
            break

    context = {
        'tasks': tasks.order_by('-created_at'),
        'upcoming_meetings': meetings,
        'daily_tasks': daily_tasks,
        'daily_meetings': daily_meetings,
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