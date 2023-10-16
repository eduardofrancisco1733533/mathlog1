from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from cuentas.models import CustomUser, Ecuacion, Salon

admin.site.register(User, UserAdmin)
admin.site.register(CustomUser)
admin.site.register(Ecuacion)
admin.site.register(Salon)
