import random
from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from cuentas.models import Actividad, Ecuacion, Salon
from .forms import (
    ActividadForm,
    AgregarEstudianteForm,
    CustomUserCreationForm,
    EcuacionForm,
    SalonForm,
    UserProfileForm,
)
from django.contrib import messages
from sympy import symbols, Eq, solve, sympify
import re

def teacher_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != "TEACHER":
            return HttpResponseForbidden("No tienes permiso para acceder a esta página.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func

def agregar_multiplicacion_implicita(expr):
    return re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expr)

def some_view(request):
    messages.success(request, "Esto es una prueba")
    return render(request, 'some_template.html')

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Usuario registrado con éxito! Por favor, inicie sesión.")
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registro.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        if 'continue_as_guest' in request.POST:
            user = authenticate(request, username="invitado", password="password_del_invitado")
        else:
            user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            return redirect('bienvenido')
        else:
            messages.error(request, 'Email o contraseña inválidos')
    return render(request, 'login.html')

def bienvenido_view(request):
    context = {'username': request.user.username if request.user.is_authenticated else "invitado"}
    return render(request, 'bienvenido.html', context)

def bienvenido_invitado_view(request):
    return render(request, 'bienvenido_invitado.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def drag_drop_view(request):
    return render(request, 'drag_and_drop.html')

def ingresar_ecuacion(request, salon_id):
    salon = Salon.objects.get(id=salon_id)
    if request.method == "POST":
        form = EcuacionForm(request.POST)
        if form.is_valid():
            ecuacion_str = agregar_multiplicacion_implicita(form.cleaned_data['ecuacion'])
            x = symbols('x')
            try:
                sol = solve(Eq(sympify(ecuacion_str), 0), x)
                ecuacion_obj = form.save(commit=False)
                ecuacion_obj.profesor = request.user
                ecuacion_obj.save()
                mensaje = "Ecuación resuelta y guardada exitosamente!"
                form = EcuacionForm()
            except Exception as e:
                mensaje = f"No se pudo resolver la ecuación. Error: {str(e)}"
    else:
        form = EcuacionForm()
        mensaje = None
    return render(request, 'ingresar_ecuacion.html', {'form': form, 'mensaje': mensaje, 'salon': salon})

@login_required
@teacher_required
def crear_ecuacion(request):
    return render(request, 'ingresar_ecuacion.html')

@login_required
@teacher_required
def crear_salon(request):
    if request.method == "POST":
        form = SalonForm(request.POST)
        if form.is_valid():
            salon = form.save(commit=False)
            salon.profesor = request.user
            salon.save()
            return redirect('agregar_estudiante', salon_id=salon.id)
    else:
        form = SalonForm()
    return render(request, 'class.html', {'form': form})

def agregar_estudiante(request, salon_id):
    salon = Salon.objects.get(id=salon_id)
    if request.method == "POST":
        form = AgregarEstudianteForm(request.POST)
        if form.is_valid():
            estudiantes = form.cleaned_data['estudiantes']
            for estudiante in estudiantes:
                salon.estudiantes.add(estudiante)
            return redirect('mis_salones')
    else:
        form = AgregarEstudianteForm()
    return render(request, 'agregar_estudiante.html', {'form': form, 'salon': salon})

@login_required
def mis_salones(request):
    salones = Salon.objects.filter(profesor=request.user)
    return render(request, 'mis_clases.html', {'salones': salones})

@login_required
def detalle_salon(request, salon_id):
    try:
        salon = Salon.objects.get(id=salon_id, profesor=request.user)
    except Salon.DoesNotExist:
        return HttpResponseNotFound("Salón no encontrado.")
    estudiantes = salon.estudiantes.all()
    actividades = Actividad.objects.filter(salon=salon)
    return render(request, 'detalle_salon.html', {'salon': salon, 'estudiantes': estudiantes, 'actividades': actividades})

def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'profile.html', {'form': form})

@login_required
@teacher_required
def listar_ecuaciones(request):
    ecuaciones = Ecuacion.objects.filter(profesor=request.user)
    return render(request, 'lista_ecuaciones.html', {'ecuaciones': ecuaciones})

def generar_ecuacion():
    a = random.randint(1, 999)
    b = random.randint(1, 999)
    operacion = random.choice(['+', '-', '*', '//'])
    if operacion == '//':  # Asegurar que 'b' no sea cero en caso de división
        b = random.randint(1, 999)

    # Generar la ecuación en formato de texto
    if operacion == '*':
        ecuacion_str = f"{a}x {operacion} {b} = 0"
    elif operacion == '//':
        # Asegurar resultado entero para la división
        ecuacion_str = f"{a * b}x // {b} = 0"
    else:
        ecuacion_str = f"{a}x {operacion} {b} = 0"

    return ecuacion_str

@login_required
@teacher_required
def crear_actividad(request, salon_id):
    salon = Salon.objects.get(pk=salon_id)
    if request.method == "POST":
        form = ActividadForm(request.POST)
        if form.is_valid():
            numero_ecuaciones = form.cleaned_data['numero_ecuaciones']
            actividad = Actividad.objects.create(salon=salon)
            
            for _ in range(numero_ecuaciones):
                ecuacion_str = generar_ecuacion()
                ecuacion = Ecuacion.objects.create(ecuacion=ecuacion_str, profesor=request.user)
                actividad.ecuaciones.add(ecuacion)

            return redirect('detalle_salon', salon_id=salon.id)
    else:
        form = ActividadForm()
    return render(request, 'crear_actividad.html', {'form': form, 'salon': salon})


def actividades_estudiante(request):
    estudiante = request.user
    salones = estudiante.clases_asignadas.all()
    actividades = Actividad.objects.filter(salon__in=salones)
    return render(request, 'actividades_estudiante.html', {'actividades': actividades})
