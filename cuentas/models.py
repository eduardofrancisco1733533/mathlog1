from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("El campo Email es necesario")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        
        # Asigna el rol por defecto si no se provee uno.
        user.role = extra_fields.get('role', 'STUDENT')

        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        # Asegúrate de que el superusuario tiene un rol; puedes decidir qué rol es adecuado para un superusuario.
        extra_fields.setdefault('role', 'TEACHER')

        return self.create_user(email, username, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLES = (
        ('STUDENT', 'Estudiante'),
        ('TEACHER', 'Profesor'),
    )
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    role = models.CharField(max_length=7, choices=ROLES,null=True)  # Asegúrate de que no haya 'null=True' aquí
    profile_icon = models.ImageField(upload_to='media/', null=True, blank=True)
    points = models.IntegerField(default=0, verbose_name='Puntos')
    user_class = models.CharField(max_length=50, default='', blank=True, verbose_name='Clase de usuario')

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username
# Your other models remain unchanged

class Ecuacion(models.Model):
    ecuacion = models.TextField()
    profesor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='ecuaciones_creadas', null=True)
    def __str__(self):
        return self.ecuacion[:50] + "..." if len(self.ecuacion) > 50 else self.ecuacion

class Salon(models.Model):
    nombre = models.CharField(max_length=200)
    profesor = models.ForeignKey(CustomUser, related_name='clases_creadas', on_delete=models.CASCADE)
    estudiantes = models.ManyToManyField(CustomUser, related_name='clases_asignadas')

class Actividad(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE)
    ecuaciones = models.ManyToManyField(Ecuacion)
