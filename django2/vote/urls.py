from django.urls import path
from . import views

app_name = "vote"

urlpatterns = [

    path('vote/<str:poll_code>/', views.poll, name='vote_pass'),

    path('vote/<str:poll_code>/authen', views.poll_authen, name='vote_authen'),

    path('vote/results/<str:poll_code>/', views.results, name='results'),
]
