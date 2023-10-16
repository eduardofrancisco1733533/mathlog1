from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("El campo Email es necesario")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

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
    role = models.CharField(max_length=7, choices=ROLES, null=True, blank=True)  # campo de rol

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username
    
class Ecuacion(models.Model):
    ecuacion = models.TextField()

class Salon(models.Model):
    nombre = models.CharField(max_length=200)
    profesor = models.ForeignKey(CustomUser, related_name='clases_creadas', on_delete=models.CASCADE)
    estudiantes = models.ManyToManyField(CustomUser, related_name='clases_asignadas')