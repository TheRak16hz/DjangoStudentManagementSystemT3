from django.db import models
from accounts.models import Estudiante  # Asegúrate de que esta importación no cause problemas circulares


class Trayectos_temp(models.Model):
    ref_cedula = models.ForeignKey(Estudiante, on_delete=models.CASCADE)  # Relación con estudiante
    ci_est = models.CharField(max_length=10)
    name_est = models.CharField(max_length=32)
    apellido_est = models.CharField(max_length=32)
    seccion = models.CharField(max_length=10)
    trayecto_año = models.CharField(max_length=10)
    codigo_año = models.CharField(max_length=10)

    def __str__(self):
        return self.ci_est + ' - ' + self.name_est


class Trayectos_all(models.Model):
    ref_cedula = models.ForeignKey(Estudiante, on_delete=models.CASCADE)  # Relación con estudiante
    ci_est = models.CharField(max_length=10)
    name_est = models.CharField(max_length=32)
    apellido_est = models.CharField(max_length=32)
    seccion = models.CharField(max_length=10)
    trayecto_año = models.CharField(max_length=10)
    codigo_año = models.CharField(max_length=10)

    def __str__(self):
        return self.ci_est + ' - ' + self.name_est + ' ' + self.apellido_est + ' - ' + self.seccion

    class Meta:
        db_table = 'trayectos_all'
        
##################################
class Trayecto_inicial(models.Model):
    ref_cedula = models.ForeignKey(Estudiante, on_delete=models.CASCADE)  # Relación con estudiante
    ci_est = models.CharField(max_length=10)
    name_est = models.CharField(max_length=32)
    seccion = models.CharField(max_length=10)
    codigo_año = models.CharField(max_length=10)

    def __str__(self):
        return self.ci_est + ' - ' + self.name_est + ' - ' + self.seccion

    class Meta:
        db_table = 'trayecto_inicial'

class Trayecto_egresados(models.Model):
    ref_cedula = models.ForeignKey(Estudiante, on_delete=models.CASCADE)  # Relación con estudiante
    ci_est = models.CharField(max_length=10)
    name_est = models.CharField(max_length=32)
    seccion = models.CharField(max_length=10)
    codigo_año = models.CharField(max_length=10)

    def __str__(self):
        return self.ci_est + ' - ' + self.name_est + ' - ' + self.seccion

    class Meta:
        db_table = 'egresados_trayecto'