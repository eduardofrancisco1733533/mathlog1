from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Ecuacion
import re

class CustomUserCreationForm(UserCreationForm):

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



class UserProfileForm(forms.ModelForm):
    ICON_CHOICES = [
        ('Icono1.jpg', 'Icono 1'),
        ('icono2.jpg', 'Icono 2'),
        ('icono3.jpg', 'Icono 3'),
        # Agrega más opciones para los iconos predefinidos aquí
    ]
    
    profile_icon = forms.ImageField(required=False)


    class Meta:
        model = CustomUser
        fields = ['profile_icon']