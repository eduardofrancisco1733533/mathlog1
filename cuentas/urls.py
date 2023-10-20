from django.urls import path
from . import views

urlpatterns = [
    path('registro/', views.register_view, name='registro'),
    path('login/', views.login_view, name='login'),
    path('bienvenido/', views.bienvenido_view, name='bienvenido'),
    path('perfil/', views.profile_view, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('prueba/', views.some_view, name='prueba'),
    path('drag_drop_view/', views.drag_drop_view, name='drag_drop_view'),
    path('bienvenido_invitado/', views.bienvenido_invitado_view, name='bienvenido_invitado'),
    path('ingresar/', views.ingresar_ecuacion, name='ingresar_ecuacion'),
    path('crearEcuacion/', views.crear_ecuacion, name='crear_ecuacion'),
    path('crear/', views.crear_salon, name='crear_salon'),
    path('agregar_estudiante/<int:salon_id>/', views.agregar_estudiante, name='agregar_estudiante'),
    path('misClases/', views.mis_salones, name='mis_salones'),
    path('detalleSalon/<int:salon_id>/', views.detalle_salon, name='detalle_salon'),



]

