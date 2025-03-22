from django import forms
from .models import Profesores

class ProfesoresForm(forms.ModelForm):

    
    class Meta:
        model = Profesores
        fields = ["cedula", "nombre", "correo", "apellido", "role"]
        widgets = {
            "cedula" : forms.TextInput(attrs={"placeholder": "insert CI", "class":"form-control"}),
            "nombre" : forms.TextInput(attrs={"placeholder": "insert name", "class":"form-control"}),
            "apellido" : forms.TextInput(attrs={"placeholder": "insert last name", "class":"form-control"}),
            "correo" : forms.TextInput(attrs={"placeholder": "insert email", "class":"form-control"}),
            'role': forms.Select(choices=[('academico', 'Académico'), ('metodologico', 'Metodológico'), ('completo', 'Académico-Metodológico')], attrs={"placeholder": "insert a role", "class":"form-control"})
        }

class BuscarProfesorForm(forms.Form):
    cedula = forms.CharField(max_length=10, label="Buscar por Cédula")