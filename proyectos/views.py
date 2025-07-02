from django.shortcuts import render, get_object_or_404, redirect
from .models import ArchivosEstudiantes
from grupos.models import Grupos
from .forms import ArchivoEstudianteForm
from django.contrib import messages
from accounts.models import Estudiante

# Create your views here.
def proyectos_home(request):
    return render(request, 'home_proyectos.html')

def subir_archivo(request):
    user_id = request.session.get('user_id')  # ID del estudiante logueado
    #print(user_id)
    if not user_id:
        messages.error(request, "No estás autenticado.")
        return redirect('login')

    estudiante = Estudiante.objects.filter(cedula=request.session['user_cedula']).first()
    estudiante_id = estudiante.id
    print(estudiante_id)
    grupos = Grupos.objects.all()  # Obtener todos los grupos

    # Filtrar grupos a los que pertenece el estudiante
    grupos_usuario = [
        grupo for grupo in grupos if str(estudiante_id) in grupo.get_estudiantes()
    ]
    print(grupos_usuario)

    if not grupos_usuario:
        messages.error(request, "No estás asociado a ningún grupo.")
        return redirect('listar_archivos')

    # Verificar si el estudiante ya subió un archivo para alguno de sus grupos
    archivos_existentes = ArchivosEstudiantes.objects.filter(Grupo_est_id__in=[grupo.id for grupo in grupos_usuario])
    if archivos_existentes:
        messages.error(request, "Ya has subido un archivo para tu grupo.")
        return redirect('listar_archivos')

    if request.method == 'POST':
        form = ArchivoEstudianteForm(request.POST, request.FILES, grupos_disponibles=grupos_usuario)
        if form.is_valid():
            archivo = form.save(commit=False)
            archivo.Grupo_est_id = form.cleaned_data['Grupo_est_id']  # Asignar grupo seleccionado
            archivo.save()
            messages.success(request, "Archivo subido exitosamente.")
            return redirect('listar_archivos')
    else:
        form = ArchivoEstudianteForm(grupos_disponibles=grupos_usuario)

    return render(request, 'archivos/subir_archivo.html', {'form': form})


def listar_archivos(request):
    estudiante = Estudiante.objects.filter(cedula=request.session['user_cedula']).first()
    estudiante_id = estudiante.id
    print(estudiante_id)
    
    grupo = Grupos.objects.filter(estudiantes__icontains=str(estudiante_id)).first()
    archivos = ArchivosEstudiantes.objects.filter(Grupo_est_id=grupo.id) if grupo else []

    return render(request, 'archivos/listar_archivos.html', {'archivos': archivos, 'grupo': grupo, 'estudiante_id': estudiante_id})

def listar_archivos_all(request):
    # Obtener todos los archivos
    archivos = ArchivosEstudiantes.objects.all()

    # Diccionario para mapear los grupos con estudiantes
    archivos_con_grupos = []

    for archivo in archivos:
        # Obtener el grupo relacionado por el campo Grupo_est_id
        grupo = Grupos.objects.filter(id=archivo.Grupo_est_id).first()

        if grupo and grupo.estudiantes:  # Si el grupo existe y tiene estudiantes
            estudiantes_ids = [int(id.strip()) for id in grupo.estudiantes.split(',') if id.strip().isdigit()]
            estudiantes = Estudiante.objects.filter(id__in=estudiantes_ids)

            # Agregar el archivo con su grupo y estudiantes al contexto
            archivos_con_grupos.append({
                'archivo': archivo,
                'grupo': {
                    'id_grupo': grupo.id,
                    'estudiantes': [
                        {'nombre': estudiante.nombre, 'cedula': estudiante.cedula}
                        for estudiante in estudiantes
                    ]
                }
            })
    return render(request, 'archivos/listar_archivos_staff.html', {
        'archivos_con_grupos': archivos_con_grupos,
    })


def editar_archivo(request, archivo_id):
    archivo = get_object_or_404(ArchivosEstudiantes, id=archivo_id)
    if request.method == 'POST':
        form = ArchivoEstudianteForm(request.POST, request.FILES, instance=archivo)
        if form.is_valid():
            form.save()
            messages.success(request, "Archivo actualizado exitosamente.")
            return redirect('listar_archivos')
    else:
        form = ArchivoEstudianteForm(instance=archivo)
    return render(request, 'archivos/editar_archivo.html', {'form': form})

def eliminar_archivo(request, archivo_id):
    archivo = get_object_or_404(ArchivosEstudiantes, id=archivo_id)
    if request.method == 'POST':
        archivo.delete()
        messages.success(request, "Archivo eliminado exitosamente.")
        return redirect('listar_archivos')
    return render(request, 'archivos/eliminar_archivo.html', {'archivo': archivo})
