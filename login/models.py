from django.db import models
from django.contrib.auth.hashers import make_password, check_password

# Create your models here.

class Staff(models.Model):
    cedula = models.CharField(max_length=9, unique=True)
    nombre = models.CharField(max_length=32)
    correo = models.EmailField(unique=True)
    apellido = models.CharField(max_length=32)
    status = models.BooleanField(default=True)
    user = models.CharField(max_length=64, unique=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=18)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return {self.nombre} + ' - ' + {self.apellido}

    class Meta:
        db_table = 'staff'

