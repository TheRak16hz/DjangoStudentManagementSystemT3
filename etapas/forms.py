from django import forms
from .models import EtapasEstudiantes

ESTADO_OPCIONES = [
    ("N/A", "N/A"),
    ("Pendiente", "Pendiente"),
    ("Aprobado", "Aprobado"),
    ("Reprobado", "Reprobado"),
]

class ModificarEtapaForm(forms.ModelForm):
    etapa1 = forms.ChoiceField(choices=ESTADO_OPCIONES, label="Etapa 1")
    etapa2 = forms.ChoiceField(choices=ESTADO_OPCIONES, label="Etapa 2")
    etapa3 = forms.ChoiceField(choices=ESTADO_OPCIONES, label="Etapa 3")

    class Meta:
        model = EtapasEstudiantes
        fields = ['etapa_actual', 'etapa1', 'etapa2', 'etapa3']
        widgets = {
            'etapa_actual': forms.Select(choices=[("1", "Etapa 1"), ("2", "Etapa 2"), ("3", "Etapa 3")]),
        }

    def clean(self):
        cleaned_data = super().clean()
        for key in ['etapa1', 'etapa2', 'etapa3']:
            if cleaned_data.get(key) not in dict(ESTADO_OPCIONES):
                raise forms.ValidationError(f"Estado inválido para {key}.")
        return cleaned_data
