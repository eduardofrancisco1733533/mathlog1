from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from cuentas.models import Salon
from .forms import AgregarEstudianteForm, CustomUserCreationForm, EcuacionForm, SalonForm
from .forms import CustomUserCreationForm, EcuacionForm, UserProfileForm
from django.contrib import messages
from sympy import symbols, Eq, solve, sympify
import re

def agregar_multiplicacion_implicita(expr):
    # Encuentra patrones donde un número está seguido de una letra, como '3x' y reemplaza con '3*x'
    return re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expr)

def some_view(request):
    messages.success(request, "Esto es una prueba")
    return render(request, 'some_template.html')

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "¡Usuario registrado con éxito! Por favor, inicie sesión.")
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registro.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Si el usuario elige "Continuar como invitado"
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
    context = {}
    if not request.user.is_authenticated:
        context['username'] = "invitado"
    else:
        context['username'] = request.user.username
    return render(request, 'bienvenido.html', context)

def bienvenido_invitado_view(request):
    return render(request, 'bienvenido_invitado.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def drag_drop_view(request):
    return render(request, 'drag_and_drop.html')

def ingresar_ecuacion(request):
    if request.method == "POST":
        form = EcuacionForm(request.POST)
        if form.is_valid():
            ecuacion_str = form.cleaned_data['ecuacion']

            x = symbols('x')

            # Modifica la ecuación para agregar multiplicaciones implícitas
            ecuacion_str = agregar_multiplicacion_implicita(ecuacion_str)

            try:
                # Convertir la ecuación string a una ecuación SymPy usando sympify
                ecuacion_expr = sympify(ecuacion_str)
                
                # Intentar resolver la ecuación
                sol = solve(Eq(ecuacion_expr, 0), x)
                mensaje = "Ecuación resuelta exitosamente!"
            except Exception as e:
                mensaje = f"No se pudo resolver la ecuación. Error: {str(e)}"

            return render(request, 'resultado.html', {'mensaje': mensaje})

    else:
        form = EcuacionForm()

    return render(request, 'ingresar_ecuacion.html', {'form': form})

@login_required
def crear_ecuacion(request):
    if request.user.role != "TEACHER":
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")
    return render(request, 'ingresar_ecuacion.html')

@login_required
def crear_salon(request):
    if request.user.role != "TEACHER":
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    if request.method == "POST":
        form = SalonForm(request.POST)
        if form.is_valid():
            salon = form.save(commit=False)
            salon.profesor = request.user
            salon.save()
            return redirect('agregar_estudiante', salon_id=salon.id)  # Pasar el ID del salón como argumento
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
    # Filtramos los salones donde el profesor es el usuario actual
    salones = Salon.objects.filter(profesor=request.user)

    context = {
        'salones': salones,
    }

    return render(request, 'mis_clases.html', context)

@login_required
def detalle_salon(request, salon_id): 
    try:
        salon = Salon.objects.get(id=salon_id, profesor=request.user)
    except Salon.DoesNotExist:
        return HttpResponseNotFound("Salón no encontrado.")

    context = {
        'salon': salon,
        'estudiantes': salon.estudiantes.all()
    }

    return render(request, 'detalle_salon.html', context)



def profile_view(request):
    user = request.user

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user.profile_icon = form.cleaned_data.get('profile_icon')
            user.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user)

    return render(request, 'profile.html', {'form': form})
