from django.urls import path
from . import views

urlpatterns = [
    path('registro/', views.register_view, name='registro'),
    path('login/', views.login_view, name='login'),
    path('bienvenido/', views.bienvenido_view, name='bienvenido'),
    path('logout/', views.logout_view, name='logout'),
    path('prueba/', views.some_view, name='prueba'),
]
