from django.shortcuts import render, get_object_or_404, redirect
from .models import EtapasEstudiantes
from grupos.models import Grupos
from .forms import ModificarEtapaForm
from django.contrib import messages
# Create your views here.

def verificar_aprobacion(estudiante_id, etapa_actual):
    # Lógica para verificar si un estudiante está aprobado en la etapa actual
    # Por ejemplo:
    # 1. Consultar un modelo de notas
    # 2. Validar si la nota para esta etapa es >= a la nota mínima
    # Simulación:
    notas_simuladas = {
        '1': {'Etapa 1': True, 'Etapa 2': True, 'Etapa 3': False},
        '2': {'Etapa 1': True, 'Etapa 2': False, 'Etapa 3': False},
    }
    return notas_simuladas.get(estudiante_id, {}).get(etapa_actual, False)


def home_etapas(request):
    grupos = Grupos.objects.all()
    etapas = {etapa.Grupo_est_id: etapa for etapa in EtapasEstudiantes.objects.all()}  # Diccionario para referencias rápidas
    print(etapas)
    return render(request, 'home_etapas.html', {'grupos': grupos, 'etapas': etapas})

def editar_etapa(request, grupo_id):
    grupo = get_object_or_404(Grupos, id=grupo_id)
    
    # Buscar si ya existe una etapa asociada
    etapa, created = EtapasEstudiantes.objects.get_or_create(Grupo_est_id=str(grupo_id), defaults={'Estatus': 'Pendiente', 'Fecha': '2025-02-24'})
    
    if request.method == 'POST':
        etapa.Estatus = request.POST.get('estatus')
        etapa.save()
        return redirect('home_etapas')

    return render(request, 'gestionar_etapa.html', {'grupo': grupo, 'etapa': etapa})

# def gestionar_etapa(request, grupo_id):
#     # Obtener el grupo y la etapa asociada
#     grupo = get_object_or_404(Grupos, id=grupo_id)
#     etapa = EtapasEstudiantes.objects.filter(Grupo_est_id=grupo_id).first()

#     if request.method == 'POST':
#         form = ModificarEtapaForm(request.POST, instance=etapa)
#         if form.is_valid():
#             nueva_etapa = form.cleaned_data.get('Estatus')
            
#             # Validar si todos los estudiantes están aprobados para la etapa actual
#             estudiantes_ids = grupo.get_estudiantes()
#             aprobados = True  # Aquí iría la lógica para validar las notas
            
#             # Simulación: Cambiar `aprobados` basado en validaciones reales
#             for estudiante_id in estudiantes_ids:
#                 # Lógica para verificar si el estudiante tiene la nota aprobada
#                 if not verificar_aprobacion(estudiante_id, etapa.Estatus):
#                     aprobados = False
#                     break
            
#             if aprobados:
#                 form.save()
#                 messages.success(request, "Etapa modificada exitosamente.")
#                 return redirect('listar_grupos')  # Ajusta esta URL según tu proyecto
#             else:
#                 messages.error(request, "No se puede cambiar la etapa. Algunos estudiantes no están aprobados.")
#         else:
#             messages.error(request, "Formulario inválido.")
#     else:
#         form = ModificarEtapaForm(instance=etapa)

#     return render(request, 'gestionar_etapa.html', {'grupo': grupo, 'etapa': etapa, 'form': form})

