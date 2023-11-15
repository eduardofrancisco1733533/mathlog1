import random
from django.http import HttpResponseForbidden, HttpResponseNotFound, JsonResponse
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import CustomUser, ProgresoActividad
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
from fractions import Fraction
from sympy import Rational

def comparar_respuestas(respuesta_estudiante, solucion_sympy, tolerancia=0.01):
    try:
        # Intenta convertir la respuesta del estudiante a un número decimal
        respuesta_decimal = float(respuesta_estudiante)
        solucion_decimal = float(solucion_sympy.evalf())
        return abs(respuesta_decimal - solucion_decimal) < tolerancia
    except ValueError:
        # Si la conversión a decimal falla, intenta convertir la respuesta a una fracción
        try:
            respuesta_fraccion = Fraction(respuesta_estudiante)
            # Convierte la solución de SymPy a una fracción si es racional
            if isinstance(solucion_sympy, Rational):
                solucion_fraccion = Fraction(solucion_sympy.p, solucion_sympy.q)
                return respuesta_fraccion == solucion_fraccion
            return False
        except ValueError:
            # Si ambas conversiones fallan, la respuesta es incorrecta
            return False


def teacher_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != "TEACHER":
            return HttpResponseForbidden("No tienes permiso para acceder a esta página.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func

def transformar_ecuacion(ecuacion_str):
    # Asegúrate de que haya un espacio entre números y variables/operadores
    ecuacion_str = ecuacion_str.replace("x", " * x")
    ecuacion_str = ecuacion_str.replace("//", "/")
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

    # Obtener las clases asignadas al usuario
    clases_asignadas = Salon.objects.filter(estudiantes=request.user)

    context = {
        'form': form,
        'clases_asignadas': clases_asignadas
    }
    return render(request, 'profile.html', context)

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


@login_required
def actividades_estudiante(request):
    estudiante = request.user
    # Obtener solo las actividades que aún no han sido completadas por el estudiante
    actividades_no_completadas = Actividad.objects.filter(
        salon__estudiantes=estudiante
    ).exclude(
        progresos__estudiante=estudiante, progresos__completada=True
    )
    return render(request, 'actividades_estudiante.html', {'actividades': actividades_no_completadas})

@login_required
def enviar_respuestas(request, actividad_id):
    if request.method == "POST":
        actividad = get_object_or_404(Actividad, id=actividad_id)
        estudiante = request.user
        x = symbols('x')
        todas_correctas = True
        resultado_respuestas = {}

        for ecuacion in actividad.ecuaciones.all():
            respuesta = request.POST.get(f"respuesta_{ecuacion.id}")
            try:
                ecuacion_transformada = transformar_ecuacion(ecuacion.ecuacion.split('=')[0])
                solucion = solve(Eq(sympify(ecuacion_transformada), 0), x)[0]
                es_correcta = comparar_respuestas(respuesta, solucion)
            except SympifyError:
                es_correcta = False

            resultado_respuestas[f"respuesta_{ecuacion.id}"] = es_correcta
            if not es_correcta:
                todas_correctas = False

        # Actualiza el progreso del estudiante en la actividad si todas las respuestas son correctas
        if todas_correctas:
            ProgresoActividad.objects.update_or_create(
                estudiante=estudiante, 
                actividad=actividad, 
                defaults={'completada': True}
            )

        return JsonResponse({"respuestas": resultado_respuestas, "todas_correctas": todas_correctas})
    else:
        return redirect('actividades_estudiante')


def agregar_puntos(request, username):
    usuario = get_object_or_404(CustomUser, username=username)
    usuario.points += 50  
    usuario.save()

    return HttpResponse("Puntos añadidos correctamente.")


def quitar_puntos(request, username):
    usuario = get_object_or_404(CustomUser, username=username)
    usuario.points -= 50  
    usuario.save()

    return HttpResponse("Puntos restados correctamente.")
