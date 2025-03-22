from django.db import models

# Create your models here.

class ArchivosEstudiantes(models.Model):
    id_archivos = models.CharField(max_length=10) #id
    Proyecto = models.FileField(upload_to='proyectos/')
    Capitulos = models.FileField(upload_to='capitulos/')
    Grupo_est_id = models.CharField(max_length=50)  # Simulación de ForeignKey como CharField

    def __str__(self):
        return f"Archivo {self.id} del grupo {self.Grupo_est_id}"