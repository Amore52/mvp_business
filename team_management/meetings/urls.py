from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_meeting, name='create_meeting'),
    path('<int:meeting_id>/', views.meeting_detail, name='meeting_detail'),
]