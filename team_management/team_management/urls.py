from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from tasks.views import dashboard_view, my_tasks_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('', RedirectView.as_view(url='users/login/')),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('my-tasks/', my_tasks_view, name='my_tasks'),
    path('teams/', include('teams.urls', namespace='teams')),
]