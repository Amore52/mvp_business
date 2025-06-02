from django.urls import path
from . import views

app_name = 'teams'

urlpatterns = [
    path('create/', views.team_create, name='team_create'),
    path('<int:team_id>/', views.team_detail, name='team_detail'),
    path('<int:team_id>/members/<int:user_id>/remove/', views.remove_member, name='remove_member'),
    path('<int:team_id>/members/<int:user_id>/update_role/', views.update_member_role, name='update_member_role'),
    path('<int:pk>/edit/', views.TeamUpdateView.as_view(), name='team_edit'),
    path('<int:pk>/delete/', views.TeamDeleteView.as_view(), name='team_delete'),
    path('my-teams/', views.my_teams, name='my_teams'),
]
