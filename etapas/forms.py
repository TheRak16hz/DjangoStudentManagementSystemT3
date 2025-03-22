from django import forms
from .models import EtapasEstudiantes

class ModificarEtapaForm(forms.ModelForm):
    class Meta:
        model = EtapasEstudiantes
        fields = ['Estatus']

    def clean_Estatus(self):
        nueva_etapa = self.cleaned_data.get('Estatus')
        if nueva_etapa not in ['Etapa 1', 'Etapa 2', 'Etapa 3', 'Etapa 4']:
            raise forms.ValidationError("La etapa seleccionada no es válida.")
        return nueva_etapa
