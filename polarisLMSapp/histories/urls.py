from django.urls import path
from . import views

app_name = 'histories'

urlpatterns = [
    path('', views.history_list, name='history_list'),
]