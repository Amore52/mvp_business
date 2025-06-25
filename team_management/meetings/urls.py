from django.urls import path, include
from . import views
from .views import my_meetings_view

urlpatterns = [
    path('create/', views.create_meeting, name='create_meeting'),
    path('<int:meeting_id>/', views.meeting_detail, name='meeting_detail'),
    path('my-meetings/', my_meetings_view, name='my_meetings'),
]