from django.shortcuts import render, get_object_or_404, redirect
from .models import EtapasEstudiantes
from grupos.models import Grupos
from .forms import ModificarEtapaForm
from django.contrib import messages
from accounts.models import Estudiante
from masters.models import Profesores


def etapas_main(request):
    return render(request, 'etapas_main.html')

def buscar_etapas(request):
    estudiante_encontrado = None
    grupo_data = None

    if request.method == 'POST':
        cedula = request.POST.get('cedula')

        try:
            estudiante_encontrado = Estudiante.objects.get(cedula=cedula)
            estudiante_id = estudiante_encontrado.id

            grupos = Grupos.objects.all()
            for grupo in grupos:
                estudiantes_ids = [est_id.strip() for est_id in grupo.get_estudiantes() if est_id.strip()]
                estudiantes_ids = [int(est_id) for est_id in estudiantes_ids if est_id.isdigit()]

                if estudiante_id in estudiantes_ids:
                    docente_metodologico = Profesores.objects.get(id=grupo.docente_metodologico)
                    docente_academico = Profesores.objects.get(id=grupo.docente_academico)
                    estudiantes = Estudiante.objects.filter(id__in=estudiantes_ids)
                    #g_id = grupo.id
                    #print(g_id)

                    # Obtener etapas del grupo
                    etapas_dict = {etapa.grupo_id: etapa for etapa in EtapasEstudiantes.objects.all()}

                    etapa = EtapasEstudiantes.objects.filter(grupo_id=grupo.id).first()
                    #print(etapa)




                    grupo_data = {
                        'id': grupo.id,
                        'trayecto_cursante': grupo.trayecto_cursante,
                        'docente_metodologico': docente_metodologico,
                        'docente_academico': docente_academico,
                        'estudiantes_lista': estudiantes,
                        'etapa': etapa,
                        
                    }
                    break

        except Estudiante.DoesNotExist:
            estudiante_encontrado = None
        
    return render(request, 'buscar_etapas.html', {
        'estudiante_encontrado': estudiante_encontrado,
        'grupo_encontrado': grupo_data,
        'roles': request.session["staff_role"],
    })

def home_etapas(request):
    etapas = EtapasEstudiantes.objects.all()  # Aquí obtenemos todas las etapas
    # Crear un diccionario para acceder rápidamente a las etapas por el id
    etapas_dict = {etapa.grupo_id: etapa for etapa in etapas}

    grupos = Grupos.objects.all()
    grupos_data = []

    for grupo in grupos:
        # Obtener los docentes a partir de sus IDs
        docente_metodologico = Profesores.objects.get(id=grupo.docente_metodologico)
        docente_academico = Profesores.objects.get(id=grupo.docente_academico)

        # Asegurarse de que el campo de estudiantes sea válido
        estudiantes_ids = grupo.estudiantes.split(',') if grupo.estudiantes else []

        try:
            # Convertir a enteros y filtrar los estudiantes
            estudiantes_ids = [int(est_id.strip()) for est_id in estudiantes_ids]
            estudiantes = Estudiante.objects.filter(id__in=estudiantes_ids)
        except ValueError:
            # Si hay algún valor que no se pueda convertir a entero, manejamos el error
            estudiantes = []

        # Añadir los datos al contexto
        grupos_data.append({
            'id' : grupo.id,
            'trayecto_cursante': grupo.trayecto_cursante,
            'docente_metodologico': f"{docente_metodologico.nombre} {docente_metodologico.apellido}",
            'docente_academico': f"{docente_academico.nombre} {docente_academico.apellido}",
            'estudiantes_lista': estudiantes,
        })
    
    
    return render(request, 'home_etapas.html', {
        'grupos': grupos_data,
        'etapas_dict': etapas_dict  # Pasamos el diccionario de etapas a la plantilla
    })

def gestionar_etapa(request, grupo_id):
    grupo = get_object_or_404(Grupos, id=grupo_id)
    etapa_obj, created = EtapasEstudiantes.objects.get_or_create(grupo_id=str(grupo.id))

    if request.method == 'POST':
        form = ModificarEtapaForm(request.POST, instance=etapa_obj)
        if form.is_valid():
            etapa_data = form.save(commit=False)
            
            if etapa_data.etapa_actual == 1:
                if etapa_data.etapa1 == 'Aprobado' and etapa_data.etapa2 == 'N/A':
                    etapa_data.etapa2 = 'Pendiente'
                    etapa_data.etapa_actual = 2
                elif etapa_data.etapa1 == 'Reprobado' and etapa_data.etapa2 == 'N/A':
                    etapa_data.etapa1 = 'Reprobado'
                else:
                    etapa_data.etapa1 = 'Pendiente'
                    etapa_data.etapa2 = 'N/A'
                    etapa_data.etapa3 = 'N/A'

            elif etapa_data.etapa_actual == 2:
                if etapa_data.etapa2 == 'Aprobado':
                    etapa_data.etapa3 = 'No Aplica'  # no se activa si aprueban etapa 2
                elif etapa_data.etapa2 == 'Reprobado' and etapa_data.etapa3 == 'N/A':
                    etapa_data.etapa3 = 'Pendiente'
                    etapa_data.etapa_actual = 3
                else:
                    etapa_data.etapa1 = 'Aprobado'
                    etapa_data.etapa2 = 'Pendiente'
                    etapa_data.etapa3 = 'N/A'

            elif etapa_data.etapa_actual == 3:
                if etapa_data.etapa3 == 'Aprobado':
                    etapa_data.etapa3 == 'Aprobado'
                elif etapa_data.etapa3 == 'Reprobado':
                    etapa_data.etapa3 = 'Reprobado'
                else:
                    etapa_data.etapa1 = 'Aprobado'
                    etapa_data.etapa2 = 'Reprobado'
                    etapa_data.etapa3 = 'Pendiente'

            form.save()
            messages.success(request, "Etapa actualizada correctamente.")
            return redirect('home_etapas')
    else:
        form = ModificarEtapaForm(instance=etapa_obj)

    return render(request, 'gestionar_etapa.html', {'grupo': grupo, 'form': form})

def eliminar_etapa(request, grupo_id):
    etapa = get_object_or_404(EtapasEstudiantes, grupo_id=grupo_id)
    etapa.delete()
    messages.success(request, "Etapas eliminadas correctamente.")
    return redirect('home_etapas')

def asignar_etapa(request, grupo_id):
    grupo = get_object_or_404(Grupos, id=grupo_id)
    
    # Evitar crear duplicados si ya existen
    if not EtapasEstudiantes.objects.filter(grupo_id=grupo_id).exists():
        EtapasEstudiantes.objects.create(
            grupo_id=grupo_id,
            etapa_actual=1,
            etapa1='Pendiente',
            etapa2='N/A',
            etapa3='N/A'
        )
        messages.success(request, "Etapas asignadas correctamente.")
    else:
        messages.warning(request, "Este grupo ya tiene etapas asignadas.")

    return redirect('home_etapas')
