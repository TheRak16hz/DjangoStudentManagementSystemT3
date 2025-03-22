from django.urls import path, include
from . import views
from masters import urls

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('api/register/', views.register_staff, name='api_register_staff'),
    path('login_staff/', views.login_staff, name='login_staff'),
    path('logout_staff/', views.logout_staff, name='logout_staff'),
    path('dashboard_staff/', views.staff_dashboard, name='staff_dashboard'),
    path('dashboard/', views.dashboard, name='user_dashboard'),
]
