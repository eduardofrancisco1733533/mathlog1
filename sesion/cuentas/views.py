from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import CustomUserCreationForm
from django.contrib import messages
from sympy import symbols, Eq, solve, sympify
from .forms import EcuacionForm

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
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            return redirect('bienvenido')
        else:
            messages.error(request, 'Email o contraseña inválidos')
    return render(request, 'login.html')

def bienvenido_view(request):
    return render(request, 'bienvenido.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def drag_drop_view(request):
    return render(request, 'drag_and_drop.html')

def resolver_ecuacion(request):
    if request.method == "POST":
        form = EcuacionForm(request.POST)
        if form.is_valid():
            ecuacion_str = form.cleaned_data['expresion']
            x = symbols('x')
            
            # Si no hay un signo igual en la ecuación, asumimos que es igual a 0
            if "=" not in ecuacion_str:
                ecuacion_str += "=0"
            
            # Dividir la ecuación en dos partes basado en el signo igual
            print(ecuacion_str)
            lado_izquierdo_str, lado_derecho_str = ecuacion_str.split("=")
            print(lado_derecho_str+'.derecho'+lado_izquierdo_str+':izquierdo')
            
            # Convertir las cadenas en expresiones SymPy
            try:
                lado_izquierdo = sympify(lado_izquierdo_str)
                lado_derecho = sympify(lado_derecho_str)

                # Resolver la ecuación
                solutions = solve(Eq(lado_izquierdo, lado_derecho), x)
                es_resoluble = all(sol.is_real for sol in solutions) if solutions else False
            except:
                print('morí')
                solutions = []
                es_resoluble = False

            return render(request, 'resultados.html', {'es_resoluble': es_resoluble, 'solutions': solutions})

    else:
        form = EcuacionForm()

    return render(request, 'ingresar_ecuacion.html', {'form': form})

