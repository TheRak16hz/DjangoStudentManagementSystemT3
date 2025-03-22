from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from .models import Staff

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['cedula', 'nombre', 'apellido', 'correo', 'status', 'user', 'password', 'role']

    # Validación para el campo cédula
    def clean_cedula(self):
        cedula = self.cleaned_data.get('cedula')
        if Staff.objects.filter(cedula=cedula):
            raise ValidationError('La cédula ya está registrada en el sistema.')
        return cedula

    # Validación para el campo correo
    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        if Staff.objects.filter(correo=correo):
            raise ValidationError('El correo electrónico ya está registrado en el sistema.')
        return correo

    # Validación para el campo user
    def clean_user(self):
        user = self.cleaned_data.get('user')
        if Staff.objects.filter(user=user):
            raise ValidationError('El nombre de usuario ya está registrado en el sistema.')
        return user

    # Sobrescribir el método save para encriptar la contraseña
    def save(self, commit=True):
        staff = super().save(commit=False)
        staff.password = make_password(self.cleaned_data['password'])
        if commit:
            staff.save()
        return staff
