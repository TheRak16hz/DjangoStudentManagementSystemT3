from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Estudiante
from django.core.exceptions import ValidationError
import traceback

class CustomUserCreationForm(UserCreationForm):
    cedula = forms.CharField(
        max_length=10, 
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su cédula'
        })
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su correo electrónico'
        })
    )

    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su contraseña'
        })
    )

    password2 = forms.CharField(
        label="Confirme su contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme su contraseña'
        })
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('cedula', 'email', 'password1', 'password2')

    def clean_cedula(self):
        cedula = self.cleaned_data.get('cedula')

        # Verifica si la CI existe en la lista de estudiantes
        if not Estudiante.objects.filter(cedula=cedula):
            raise ValidationError('Error al verificar la cédula: no encontrada.')

        # Verifica si la CI ya fue registrada en algún usuario de CustomUser
        if CustomUser.objects.filter(cedula=cedula):
            raise ValidationError('Error al verificar la cédula: ya registrada.')

        return cedula

######################
    def clean_email(self):
        email = self.cleaned_data.get('email')
        #verifica si la CI existe en la lista de estudiantes
        if not Estudiante.objects.filter(email=email): ##########--
            print("email no encontrada")
            raise ValidationError('Error al verificar el correo: no encontrado')

        #verifica si la CI ya fue registrada en algun usuario de CustomUser
        if CustomUser.objects.filter(email=email): ############
            print(CustomUser.objects.filter(email=email))
            print('el email ya está registrado en el sistema.')
            raise ValidationError('Error al verificar el correo: ya registrado')

        return email
######################


class EstudianteForm(forms.ModelForm):
    class Meta:
        model = Estudiante
        fields = [
            'nombre', 'apellido', 'cedula', 'email', 'seccion',
            'fecha_nacimiento', 'numero_telefono', 'direccion', 'sexo'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Ingresa el nombre', 'class':'form-control'}),
            'apellido': forms.TextInput(attrs={'placeholder': 'Ingresa el apellido', 'class':'form-control'}),
            'cedula': forms.TextInput(attrs={'placeholder': 'Ingresa la cédula', 'class':'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Ingresa el correo', 'class':'form-control'}),
            'seccion': forms.TextInput(attrs={'placeholder': 'Ingresa la sección', 'class':'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class':'form-control'}),
            'numero_telefono': forms.TextInput(attrs={'placeholder': 'Ingresa el número de teléfono', 'class':'form-control'}),
            'direccion': forms.Textarea(attrs={'placeholder': 'Ingresa la dirección', 'rows': 3, 'class':'form-control'}),
            'sexo': forms.Select(choices=[('Masculino', 'Masculino'), ('Femenino', 'Femenino')], attrs={'class':'form-control'})
        }

class BuscarEstudianteForm(forms.Form):
    cedula = forms.CharField(max_length=10, label="Buscar por Cédula")