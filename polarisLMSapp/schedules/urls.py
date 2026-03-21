from django.urls import path
from . import views

app_name = 'schedules'

urlpatterns = [
    path('', views.schedule_list, name='schedule_list'),
    path('today/', views.today_schedule, name='today_schedule'),
    path('create/', views.schedule_create, name='schedule_create'),
]