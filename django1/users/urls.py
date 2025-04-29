from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path('', views.index, name='main_page'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('accounts/profile/', views.profile_view, name='profile'),
    path('scores/<str:poll_code>', views.poll_score, name='poll_score'),

    path('create_poll/', views.create_poll, name='create_poll'),
    path('success/<str:poll_code>/', views.poll_success, name='success'),
]