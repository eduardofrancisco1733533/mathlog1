import random
from django.http import HttpResponseForbidden, HttpResponseNotFound, JsonResponse
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
from sympy import SympifyError, symbols, Eq, solve, sympify
import re

def teacher_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != "TEACHER":
            return HttpResponseForbidden("No tienes permiso para acceder a esta página.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func

def transformar_ecuacion(ecuacion_str):
    # Asegúrate de que haya un espacio entre números y variables/operadores
    ecuacion_str = ecuacion_str.replace("x", " * x")
    # Añadir más transformaciones si es necesario
    return ecuacion_str


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
@login_required
def enviar_respuestas(request, actividad_id):
    if request.method == "POST":
        actividad = Actividad.objects.get(id=actividad_id)
        x = symbols('x')
        resultado_respuestas = {}
        for ecuacion in actividad.ecuaciones.all():
            respuesta = request.POST.get(f"respuesta_{ecuacion.id}")
            try:
                ecuacion_transformada = transformar_ecuacion(ecuacion.ecuacion.split('=')[0])
                solucion = solve(Eq(sympify(ecuacion_transformada), 0), x)
                solucion_decimal = solucion[0].evalf()
                print(solucion_decimal)
                # Asegúrate de que la comparación resulte en un valor booleano de Python
                es_correcta = abs(float(respuesta) - solucion_decimal) < 0.01
            except (SympifyError, ValueError, TypeError):
                es_correcta = False

            # Convierte es_correcta a un booleano de Python si no lo es
            resultado_respuestas[f"respuesta_{ecuacion.id}"] = bool(es_correcta)

        return JsonResponse({"respuestas": resultado_respuestas})
    else:
        return redirect('actividades_estudiante')
