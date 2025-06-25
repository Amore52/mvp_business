from django.urls import path

from tasks.views import my_tasks_view, task_detail_view, create_task_view, rate_task

urlpatterns = [
    path('my-tasks/', my_tasks_view, name='my_tasks'),
    path('task/<int:task_id>/', task_detail_view, name='task_detail'),
    path('tasks/create/', create_task_view, name='create_task'),
    path('task/<int:task_id>/rate/', rate_task, name='rate_task'),
]