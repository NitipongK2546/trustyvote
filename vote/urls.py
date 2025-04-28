from django.urls import path
from . import views

app_name = "vote"

urlpatterns = [
    path('create_poll/', views.create_poll, name='create_poll'),

    path('success/<str:poll_code>/', views.poll_success, name='success'),

    path('vote/<str:poll_code>/', views.poll, name='vote_pass'),

    path('vote/<str:poll_code>/authen', views.poll_authen, name='vote_authen'),

    path('results/<str:poll_code>/', views.results, name='results'),
]
