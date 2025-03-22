from django.db import models

# Create your models here.

class Profesores(models.Model):
    cedula = models.IntegerField(unique=True)
    nombre = models.CharField(max_length=32)
    apellido = models.CharField(max_length=32)
    correo = models.EmailField(unique=True)
    status = models.BooleanField(default=True)
    role = models.CharField(max_length=18)

    def __str__(self):
        return self.nombre + '-' + self.apellido

    class Meta:
        db_table = 'profesores'