from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, cedula, email, password=None):
        if not cedula:
            raise ValueError('El usuario debe tener una cédula')
        if not email:
            raise ValueError('El usuario debe tener un correo electrónico')
        user = self.model(cedula=cedula,email=self.normalize_email(email),)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, cedula, email, password=None):
        user = self.create_user(
            cedula=cedula,
            email=email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser):
    cedula = models.CharField(max_length=10, unique=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'cedula'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.cedula

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


class Estudiante(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    cedula = models.CharField(max_length=10, unique=True)
    email = models.EmailField(unique=True)
    seccion = models.CharField(max_length=10)
    fecha_nacimiento = models.DateField()
    numero_telefono = models.CharField(max_length=15)
    direccion = models.CharField(max_length=255)
    sexo = models.CharField(max_length=10)
    status = models.BooleanField(default=True)
    ultimo_año_cursado = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.cedula}"