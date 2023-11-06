from django.test import TestCase
from django.urls import reverse
from cuentas.models import CustomUser, Ecuacion
from sympy import symbols, Eq, solve

class CustomUserTests(TestCase):
    def setUp(self):
        self.username = 'testuser'
        self.email = 'test@example.com'
        self.password = 'securepassword'
        self.register_url = reverse('registro')
        self.login_url = reverse('login') 

    def test_register_valid_user(self):
        response = self.client.post(self.register_url, {
            'username': self.username,
            'email': self.email,
            'password1': self.password,
            'password2': self.password,
        })

        # Verificar que la respuesta sea un redirect
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login')) 

        # Verificar que el usuario fue creado
        users_count = CustomUser.objects.filter(email=self.email).count()
        self.assertEqual(users_count, 1)

    def test_login_valid_user(self):
        # Primero, crearemos un usuario en la base de datos.
        CustomUser.objects.create_user(email=self.email, username=self.username, password=self.password)
        
        response = self.client.post(self.login_url, {
            'email': self.email,
            'password': self.password,
        })
        
        # Verificar que la respuesta sea un redirect
        self.assertEqual(response.status_code, 302)
        
        # Supongamos que, después de un inicio de sesión exitoso, redirigimos al usuario a la página de inicio o dashboard.
        self.assertRedirects(response, reverse('bienvenido'))

class EcuacionTests(TestCase):
    def setUp(self):
        self.ingresar_ecuacion_url = reverse('ingresar_ecuacion')  

    def test_agregar_multiplicacion_implicita(self):
        # Este test no está relacionado con una vista, pero es útil para garantizar que tu función de utilidad funcione
        from .views import agregar_multiplicacion_implicita  # Importa la función desde tu archivo de vistas
        self.assertEqual(agregar_multiplicacion_implicita("3x"), "3*x")
        self.assertEqual(agregar_multiplicacion_implicita("5y+3x"), "5*y+3*x")

    def test_ingresar_ecuacion_POST_valid(self):
        response = self.client.post(self.ingresar_ecuacion_url, {'ecuacion': 'x+1'})

        x = symbols('x')
        sol = solve(Eq(x+1, 0), x)
        expected_message = "Ecuación resuelta exitosamente!"

        self.assertContains(response, expected_message)

    def test_ingresar_ecuacion_POST_invalid(self):
        response = self.client.post(self.ingresar_ecuacion_url, {'ecuacion': 'x++1'})

        expected_error = "No se pudo resolver la ecuación."

        self.assertContains(response, expected_error)

    def test_ingresar_ecuacion_GET(self):
        response = self.client.get(self.ingresar_ecuacion_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ingresar_ecuacion.html')

        
        

    


    

