from django.urls import path
from . import views 

urlpatterns = [
    path('register/', views.register, name='register_page'),
    path('login/', views.photographer_login, name='photographer_login'),
    path('logout/', views.photographer_logout, name='photographer_logout'),
    path('dashboard/', views.photographer_dashboard, name='photographer_dashboard'),
]
