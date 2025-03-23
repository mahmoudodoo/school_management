# /urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('register/', views.register, name='register'),  # User registration
    path('login/', views.user_login, name='login'),  # User login
    path('logout/', views.user_logout, name='logout'),  # User logout
    path('profile/', views.profile, name='profile'),  # User profile
]
