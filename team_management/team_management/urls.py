from django.contrib import admin
from django.contrib.auth.views import LogoutView, LoginView
from django.urls import path, include
from django.views.generic import RedirectView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from dashboard.views import dashboard_view

schema_view = get_schema_view(
    openapi.Info(
        title="Team Management API",
        default_version='v1',
        description="API для управления командами, задачами и встречами",
        terms_of_service="https://www.example.com/policies/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', RedirectView.as_view(url='users/login/')),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('tasks/', include('tasks.urls')),
    path('teams/', include('teams.urls', namespace='teams')),
    path('meetings/', include('meetings.urls')),
    path('api/', include('api.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('accounts/logout/', LogoutView.as_view(http_method_names=['get', 'post'])),
    path('accounts/login/', LoginView.as_view(http_method_names=['get', 'post'])),

]
