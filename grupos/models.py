from djongo import models
from masters.models import Profesores

class Grupos(models.Model):
    TRAYECTO_CHOICES = [
        ('Trayecto 1', 'Trayecto 1'),
        ('Trayecto 2', 'Trayecto 2'),
        ('Trayecto 3', 'Trayecto 3'),
        ('Trayecto 4', 'Trayecto 4'),
    ]
    
    trayecto_cursante = models.CharField(max_length=255, choices=TRAYECTO_CHOICES)
    docente_metodologico = models.CharField(max_length=255)
    docente_academico = models.CharField(max_length=255)
    estudiantes = models.CharField(max_length=500)

    def __str__(self):
        return self.trayecto_cursante

    def get_estudiantes(self):
        """
        Retorna una lista de estudiantes a partir del campo 'estudiantes'.
        """
        return self.estudiantes.split(',')