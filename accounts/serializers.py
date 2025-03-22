from rest_framework import serializers
from .models import Estudiante

class EstudianteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estudiante
        fields = ['nombre', 'apellido', 'cedula', 'email', 'seccion', 'fecha_nacimiento', 'numero_telefono', 'direccion', 'sexo']
