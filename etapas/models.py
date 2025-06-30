from django.db import models

class EtapasEstudiantes(models.Model):
    grupo_id = models.CharField(max_length=50, unique=True)  # Simula ForeignKey
    etapa_actual = models.IntegerField(default=1)  # Controlador de etapa activa

    etapa1 = models.CharField(max_length=16, default="Pendiente")  # ("Pendiente", "Aprobado", "Reprobado")
    etapa2 = models.CharField(max_length=16, default="N/A")
    etapa3 = models.CharField(max_length=16, default="N/A")

    fecha_actualizacion = models.DateField(auto_now=True)

    def __str__(self):
        return f"Grupo {self.grupo_id} - Etapa {self.etapa_actual} - {self.etapa1}, {self.etapa2}, {self.etapa3}"
