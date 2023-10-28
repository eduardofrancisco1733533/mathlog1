from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Actividad, CustomUser, Ecuacion, Salon
import re

class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=CustomUser.ROLES, required=True, label='Rol', widget=forms.RadioSelect)

    class Meta:
        model = CustomUser
        fields = ('email', 'username')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        allowed_domains = ['outlook.com', 'gmail.com', 'hotmail.com']
        domain = email.split('@')[-1]
        if domain not in allowed_domains:
            raise forms.ValidationError("Solo se permiten emails con dominio outlook.com, gmail.com o hotmail.com.")
        return email

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        
        if len(password) < 6:
            raise forms.ValidationError("La contraseña debe tener al menos 6 caracteres.")
        
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError("La contraseña debe contener al menos una letra mayúscula.")
        
        if len(re.findall(r'[0-9]', password)) < 2:
            raise forms.ValidationError("La contraseña debe contener al menos dos números.")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise forms.ValidationError("La contraseña debe contener al menos un carácter especial.")
        
        return password

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username')

class EcuacionForm(forms.ModelForm):
    class Meta:
        model = Ecuacion
        fields = ['ecuacion']

class SalonForm(forms.ModelForm):
    class Meta:
        model = Salon
        fields = ['nombre']

class AgregarEstudianteForm(forms.Form):
    estudiantes = forms.ModelMultipleChoiceField(queryset=CustomUser.objects.all(), widget=forms.CheckboxSelectMultiple)



class UserProfileForm(forms.ModelForm):
    ICON_CHOICES = [
        ('1.png', 'Icono 1'),
        ('2.png', 'Icono 2'),
        ('3.png', 'Icono 3'),
        # Agrega más opciones para los iconos predefinidos aquí
    ]
    
    profile_icon = forms.ChoiceField(choices=ICON_CHOICES, required=True, label="Selecciona un ícono")

    class Meta:
        model = CustomUser
        fields = ['profile_icon']

class ActividadForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ActividadForm, self).__init__(*args, **kwargs)
        if self.user:
            self.fields['ecuaciones'].queryset = Ecuacion.objects.filter(profesor=self.user)

    ecuaciones = forms.ModelMultipleChoiceField(
        queryset=Ecuacion.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label="Ecuaciones a resolver"
    )

    class Meta:
        model = Actividad
        fields = ['ecuaciones']
