from django.contrib import admin
from .models import Estudiante, CustomUser

# Register your models here.

admin.site.register(Estudiante)
admin.site.register(CustomUser)