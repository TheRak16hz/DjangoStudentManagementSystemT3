from django.db import models

# Create your models here.

class EtapasEstudiantes(models.Model):
    Fecha = models.DateField()
    Estatus = models.CharField(max_length=16)
    Grupo_est_id = models.CharField(max_length=50)  # Simulación de ForeignKey como CharField
    etapa = models.CharField(max_length=6, default="1")

    def __str__(self):
        return f"{self.Estatus} - {self.Grupo_est_id}"
