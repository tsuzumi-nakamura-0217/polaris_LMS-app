from django.urls import path
from . import views

app_name = 'schedules'

urlpatterns = [
    path('', views.schedule_list, name='schedule_list'),
    path('today/', views.today_schedule, name='today_schedule'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('calendar/<int:year>/<int:month>/', views.calendar_view, name='calendar_month'),
    path('batch-create/', views.schedule_batch_create, name='schedule_batch_create'),
    path('create/', views.schedule_create, name='schedule_create'),
    path('<int:pk>/solve/', views.solve_problem, name='solve_problem'),
]