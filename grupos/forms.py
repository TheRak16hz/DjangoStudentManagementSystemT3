from django import forms
from .models import Grupos
from django_select2.forms import Select2Widget
# from masters.models import Profesores
from accounts.models import Estudiante

class GruposForm(forms.ModelForm):
    class Meta:
        model = Grupos
        fields = ['trayecto_cursante', 'docente_metodologico', 'docente_academico']

        widgets = {
            'trayecto_cursante': forms.Select(choices=Grupos.TRAYECTO_CHOICES),
            'docente_metodologico': forms.Select(),  # Se cargará dinámicamente
            'docente_academico': forms.Select()
        }

    def __init__(self, *args, **kwargs):
        metodologicos_opciones = kwargs.pop('metodologicos_opciones', [])
        academicos_opciones = kwargs.pop('academicos_opciones', [])

        super().__init__(*args, **kwargs)
        self.fields['docente_metodologico'].widget = forms.Select(choices=metodologicos_opciones)
        self.fields['docente_academico'].widget = forms.Select(choices=academicos_opciones)

