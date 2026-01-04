from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('welcome/', views.welcome, name='welcome'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('student_home/<user_name>/', views.tohome, name='student_home'),
    path('guardian_home/<user_name>/', views.tohome, name='guardian_home'),
    path('staff_home/<user_name>/', views.tohome, name='staff_home'),    
    path('admin_home/<user_name>/', views.tohome, name='admin_home'),
]