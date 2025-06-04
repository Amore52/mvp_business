from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from meetings.views import my_meetings_view
from tasks.views import my_tasks_view, task_detail_view, create_task_view, rate_task

from dashboard.views import dashboard_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('', RedirectView.as_view(url='users/login/')),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('my-tasks/', my_tasks_view, name='my_tasks'),
    path('task/<int:task_id>/', task_detail_view, name='task_detail'),
    path('teams/', include('teams.urls', namespace='teams')),
    path('tasks/create/', create_task_view, name='create_task'),
    path('task/<int:task_id>/rate/', rate_task, name='rate_task'),
    path('meetings/', include('meetings.urls')),
    path('my-meetings/', my_meetings_view, name='my_meetings'),

]
