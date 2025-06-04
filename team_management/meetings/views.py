from calendar import monthrange
from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Q
from teams.models import Team
from users.models import User

from .forms import MeetingForm
from .models import Meeting


@login_required
def my_meetings_view(request):
    my_meetings = Meeting.objects.filter(participants=request.user).prefetch_related('participants', 'team')

    context = {
        'my_meetings': my_meetings,
    }
    return render(request, 'meetings/my_meetings.html', context)


@login_required
def create_meeting(request):
    if request.method == 'POST':
        form = MeetingForm(request.POST, user=request.user)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.created_by = request.user
            meeting.save()
            form.save_m2m()  # Сохраняем участников
            messages.success(request, "Встреча успешно создана")
            return redirect('dashboard')
    else:
        form = MeetingForm(user=request.user)

    return render(request, 'meetings/create_meeting.html', {
        'form': form,
    })


@login_required
def meeting_detail(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id)
    all_users = User.objects.exclude(id=request.user.id)  # Получаем всех пользователей кроме текущего
    if not (request.user in meeting.participants.all() or request.user == meeting.created_by):
        messages.error(request, "У вас нет доступа к этой встрече")
        return redirect('dashboard')

    if request.method == 'POST':
        if 'delete_meeting' in request.POST:
            if request.user == meeting.created_by or request.user.is_staff:
                meeting.delete()
                messages.success(request, "Встреча удалена")
                return redirect('dashboard')
            else:
                messages.error(request, "Только организатор может удалить встречу")
        elif 'cancel_participation' in request.POST:
            meeting.participants.remove(request.user)
            messages.success(request, "Вы отменили участие во встрече")
            return redirect('dashboard')
        else:
            # Обработка формы редактирования
            if request.user == meeting.created_by:
                meeting.title = request.POST.get('title')
                meeting.description = request.POST.get('description')
                meeting.date = request.POST.get('date')
                meeting.time = request.POST.get('time')
                meeting.duration = request.POST.get('duration')

                # Получаем список ID выбранных участников
                participants_ids = request.POST.getlist('participants')
                # Очищаем текущих участников и добавляем новых
                meeting.participants.clear()
                for user_id in participants_ids:
                    user = get_object_or_404(User, id=user_id)
                    meeting.participants.add(user)

                meeting.save()
                messages.success(request, "Встреча успешно обновлена")
                return redirect('meeting_detail', meeting_id=meeting.id)

    return render(request, 'meetings/meeting_detail.html', {
        'meeting': meeting,
        'is_creator': request.user == meeting.created_by,
        'all_users': all_users
    })


def _check_time_conflict(user, date, time, duration, meeting_id=None):
    """Проверка наложения встреч по времени"""
    end_time = (datetime.combine(date, time) + duration).time()

    conflicts = Meeting.objects.filter(
        Q(participants=user) | Q(created_by=user),
        date=date
    ).exclude(
        id=meeting_id
    ).filter(
        Q(time__lt=end_time,
          time__gte=time) |
        Q(time__lt=time,
          time__gte=(datetime.combine(date, time) - duration).time())
    )

    return conflicts.exists()