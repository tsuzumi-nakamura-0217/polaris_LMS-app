from django.urls import path
from . import views

app_name = 'problems'
 
urlpatterns = [
    path('', views.problem_list, name='problem_list'),
    path('<int:pk>/', views.problem_detail, name='problem_detail'),
    path('<int:pk>/answer/', views.problem_answer, name='problem_answer'),
]