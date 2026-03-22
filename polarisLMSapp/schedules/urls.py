from django.urls import path
from . import views

app_name = 'schedules'

urlpatterns = [
    path('', views.schedule_list, name='schedule_list'),
    path('today/', views.today_schedule, name='today_schedule'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('calendar/<int:year>/<int:month>/', views.calendar_view, name='calendar_month'),
    path('create/', views.schedule_create, name='schedule_create'),
    path('<int:pk>/solve/', views.solve_problem, name='solve_problem'),
]