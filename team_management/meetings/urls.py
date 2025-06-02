from django.urls import path
from . import views

app_name = 'meetings'

urlpatterns = [
    path('', views.meeting_list, name='meeting_list'),
    path('new/', views.create_meeting, name='create_meeting'),
    path('<int:pk>/edit/', views.edit_meeting, name='edit_meeting'),
    path('<int:pk>/delete/', views.delete_meeting, name='delete_meeting'),
]