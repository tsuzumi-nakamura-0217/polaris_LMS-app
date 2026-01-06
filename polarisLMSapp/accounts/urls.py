from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('welcome/', views.welcome, name='welcome'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('student_home/', views.student_home, name='student_home'),
    path('guardian_home/', views.guardian_home, name='guardian_home'),
    path('staff_home/', views.staff_home, name='staff_home'),    
    path('admin_home/', views.admin_home, name='admin_home'),
]