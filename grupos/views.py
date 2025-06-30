from django.shortcuts import render, redirect, get_object_or_404
from .forms import GruposForm
from .models import Grupos
from masters.models import Profesores
from accounts.models import Estudiante
from trayectos.models import Trayectos_all
from etapas.models import EtapasEstudiantes
from django.db import DatabaseError
from django.http import JsonResponse
from django.contrib import messages
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.http import HttpResponse
from django.conf import settings
import os


def grupos_main(request):
    return render(request, 'grupos_main.html')

def registrar_grupo(request):
    # Filtrar profesores por roles, incluyendo 'completo' en ambas listas
    profesores_metodologicos = Profesores.objects.filter(role__in=['metodologico', 'completo'])
    profesores_academicos = Profesores.objects.filter(role__in=['academico', 'completo'])

    # Construir las opciones para el formulario
    metodologicos_opciones = [(profesor.id, f"{profesor.nombre} {profesor.apellido}") for profesor in profesores_metodologicos]
    academicos_opciones = [(profesor.id, f"{profesor.nombre} {profesor.apellido}") for profesor in profesores_academicos]

    # Obtener todos los grupos y generar lista de estudiantes ya asignados
    grupos_data = Grupos.objects.all()
    ids_estudiantes_grupos = []

    for grupo in grupos_data:
        estudiantes_ids = grupo.get_estudiantes()
        ids_estudiantes_grupos.extend(estudiantes_ids)

    ids_estudiantes_grupos = list(set(ids_estudiantes_grupos))  # Eliminar duplicados


    # Obtener todos los estudiantes *excluyendo* los que ya están en un grupo
    estudiantes = Trayectos_all.objects.exclude(ref_cedula_id__in=ids_estudiantes_grupos)

    if request.method == 'POST':
        form = GruposForm(request.POST, metodologicos_opciones=metodologicos_opciones, academicos_opciones=academicos_opciones)

        if form.is_valid():
            grupo = form.save(commit=False)
            estudiantes_ids = request.POST.getlist('estudiantes')
            grupo.estudiantes = ','.join(estudiantes_ids)
            grupo.save()
            return redirect('grupos_list')
    else:
        form = GruposForm(metodologicos_opciones=metodologicos_opciones, academicos_opciones=academicos_opciones)

    return render(request, 'registrar_grupo.html', {
        'form': form,
        'estudiantes': estudiantes,  # Pasar la lista filtrada de estudiantes al template
        'ids_estudiantes_grupos': ids_estudiantes_grupos  # Todavía lo pasamos por si en el futuro necesitas esta información en el template
    })

def grupos_ya_registrados(request):
    # Obtener todos los grupos y generar la lista de IDs de estudiantes ya asignados
    grupos_data = Grupos.objects.all()
    ids_estudiantes_grupos = []
    for grupo in grupos_data:
        estudiantes_ids = grupo.get_estudiantes()
        ids_estudiantes_grupos.extend(estudiantes_ids)
    ids_estudiantes_grupos = list(set(ids_estudiantes_grupos))  # Eliminar duplicados

    # Obtener los estudiantes que *YA ESTÁN* en algún grupo
    estudiantes = Estudiante.objects.filter(id__in=ids_estudiantes_grupos)

    return render(request, 'grupos_ya_registrados.html', {
        'estudiantes': estudiantes, # Nueva lista de estudiantes registrados
        'ids_estudiantes_grupos': ids_estudiantes_grupos  # Aún disponible si lo necesitas
    })


def listar_grupos(request):
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

    return render(request, 'listar_grupos.html', {
        'grupos': grupos_data,
        'roles':request.session["staff_role"]
    })

def eliminar_grupo(request, grupo_id):
    grupo = get_object_or_404(Grupos, id=grupo_id)

    #borrado logico, si se borra grupo, tambien sus etapas
    etapa = get_object_or_404(EtapasEstudiantes, grupo_id=grupo_id)
    #print(etapa)
    
    if request.method == 'POST':
        grupo.delete()
        etapa.delete()
        
        messages.success(request, 'El grupo ha sido eliminado exitosamente.')
        return redirect('grupos_list')  # Redirige a la lista de grupos
    
    return render(request, 'confirmar_eliminar_grupo.html', {'grupo': grupo})


####
def agregar_estudiantes_grupo(request, grupo_id):
    grupo = get_object_or_404(Grupos, id=grupo_id)
    estudiantes_ids = grupo.estudiantes.split(',') if grupo.estudiantes else []
    estudiantes_ids = [int(id) for id in estudiantes_ids if id.strip().isdigit()]
    max_estudiantes = 4

    estudiante_encontrado = None
    grupo_estudiante = None
    companeros = []
    docente_metodologico = None
    docente_academico = None
    puede_agregar = len(estudiantes_ids) < max_estudiantes

    if request.method == 'POST':
        cedula = request.POST.get('cedula', '').strip()

        try:
            estudiante_encontrado = Estudiante.objects.get(cedula=cedula)
            estudiante_id = estudiante_encontrado.id

            # Verificar si ya está en un grupo
            todos_grupos = Grupos.objects.all()
            for g in todos_grupos:
                ids = [int(i.strip()) for i in g.estudiantes.split(',') if i.strip().isdigit()]
                if estudiante_id in ids:
                    grupo_estudiante = g
                    # Obtener compañeros (excluyendo al estudiante mismo)
                    companeros = Estudiante.objects.filter(id__in=ids).exclude(id=estudiante_id)
                    # Obtener docentes
                    try:
                        docente_metodologico = Profesores.objects.get(id=g.docente_metodologico)
                        docente_academico = Profesores.objects.get(id=g.docente_academico)
                    except Profesores.DoesNotExist:
                        docente_metodologico = docente_academico = None
                    break

            # Agregar si es válido
            if 'agregar_estudiante' in request.POST and not grupo_estudiante and puede_agregar:
                estudiantes_ids.append(estudiante_id)
                grupo.estudiantes = ','.join(map(str, estudiantes_ids))
                grupo.save()
                messages.success(request, 'Estudiante agregado al grupo exitosamente.')
                return redirect('editar_grupo', grupo.id)

        except Estudiante.DoesNotExist:
            estudiante_encontrado = None

    return render(request, 'agregar_estudiantes_grupo.html', {
        'grupo': grupo,
        'estudiante_encontrado': estudiante_encontrado,
        'grupo_estudiante': grupo_estudiante,
        'puede_agregar': puede_agregar,
        'companeros': companeros,
        'docente_metodologico': f"{docente_metodologico.nombre} {docente_metodologico.apellido}" if docente_metodologico else "No disponible",
        'docente_academico': f"{docente_academico.nombre} {docente_academico.apellido}" if docente_academico else "No disponible",
    })


##########
def eliminar_estudiante_grupo(request, grupo_id, estudiante_id):
    grupo = get_object_or_404(Grupos, id=grupo_id)
    estudiantes_ids = grupo.estudiantes.split(',')

    # Remover el estudiante
    estudiantes_ids = [eid for eid in estudiantes_ids if eid != str(estudiante_id)]
    grupo.estudiantes = ','.join(estudiantes_ids)
    grupo.save()
    return redirect('editar_grupo', grupo_id=grupo_id)

#####

def editar_grupo(request, grupo_id):
    # Obtener el grupo que se va a editar
    grupo = get_object_or_404(Grupos, id=grupo_id)
    
    # Filtrar profesores metodológicos y académicos por rol
    profesores_metodologicos = Profesores.objects.filter(role='metodologico')
    profesores_academicos = Profesores.objects.filter(role='academico')

    metodologicos_opciones = [(profesor.id, f"{profesor.nombre} {profesor.apellido}") for profesor in profesores_metodologicos]
    academicos_opciones = [(profesor.id, f"{profesor.nombre} {profesor.apellido}") for profesor in profesores_academicos]

    # Obtener todos los estudiantes
    estudiantes = Estudiante.objects.all()

    # Separar los estudiantes guardados en el grupo
    estudiantes_seleccionados_ids = grupo.estudiantes.split(',')
    #print(estudiantes_seleccionados_ids)

    if request.method == 'POST':
        form = GruposForm(request.POST, instance=grupo, metodologicos_opciones=metodologicos_opciones, academicos_opciones=academicos_opciones)

        if form.is_valid():
            grupo = form.save(commit=False)
            estudiantes = estudiantes_seleccionados_ids
            
            # Obtener la lista de estudiantes seleccionados de los checkboxes
            #estudiantes_ids = request.POST.getlist('estudiantes')
            
            # Convertir la lista de IDs a una cadena separada por comas
            #grupo.estudiantes = ','.join(estudiantes_ids)
            
            grupo.save()
            return redirect('grupos_list')
    else:
        form = GruposForm(instance=grupo, metodologicos_opciones=metodologicos_opciones, academicos_opciones=academicos_opciones)

    return render(request, 'editar_grupo.html', {
        'form': form,
        'estudiantes': estudiantes,
        'estudiantes_seleccionados': estudiantes_seleccionados_ids,
        "roles":request.session["staff_role"]
        # Para preseleccionar los estudiantes
    })

def buscar_estudiante_por_cedula(request):
    estudiante_encontrado = None
    grupo_data = None  # Esta variable contendrá todos los datos del grupo

    if request.method == 'POST':
        cedula = request.POST.get('cedula')

        try:
            # 1. Buscar el estudiante por cédula
            estudiante_encontrado = Estudiante.objects.get(cedula=cedula)
            estudiante_id = estudiante_encontrado.id

            # 2. Buscar si está en algún grupo
            grupos = Grupos.objects.all()
            for grupo in grupos:
                # Obtener lista limpia de IDs
                estudiantes_ids = [est_id.strip() for est_id in grupo.get_estudiantes() if est_id.strip()]
                estudiantes_ids = [int(est_id) for est_id in estudiantes_ids if est_id.isdigit()]

                if estudiante_id in estudiantes_ids:
                    # 3. Obtener los docentes como objetos
                    docente_metodologico = Profesores.objects.get(id=grupo.docente_metodologico)
                    docente_academico = Profesores.objects.get(id=grupo.docente_academico)

                    # 4. Obtener los estudiantes del grupo como queryset
                    estudiantes = Estudiante.objects.filter(id__in=estudiantes_ids)

                    # 5. Preparar el diccionario con la info del grupo
                    grupo_data = {
                        'id': grupo.id,
                        'trayecto_cursante': grupo.trayecto_cursante,
                        'docente_metodologico': docente_metodologico,
                        'docente_academico': docente_academico,
                        'estudiantes_lista': estudiantes,
                    }
                    break  # Salir del bucle una vez encontrado el grupo

        except Estudiante.DoesNotExist:
            estudiante_encontrado = None

    return render(request, 'buscar_estudiante_g.html', {
        'estudiante_encontrado': estudiante_encontrado,
        "roles":request.session["staff_role"],
        'grupo_encontrado': grupo_data  # Este contiene toda la info que tu HTML necesita
    })


###

# Para mantener temporalmente estudiantes seleccionados
def registrar_grupo_individual(request):
    # Inicializa la sesión para almacenar estudiantes temporalmente
    if 'temp_estudiantes' not in request.session:
        request.session['temp_estudiantes'] = []

    temp_estudiantes_ids = request.session.get('temp_estudiantes', [])

    # Evita duplicados y limita a 4
    if len(temp_estudiantes_ids) > 4:
        temp_estudiantes_ids = temp_estudiantes_ids[:4]

    estudiantes_temp = Estudiante.objects.filter(id__in=temp_estudiantes_ids)

    # Buscar estudiante por cédula
    cedula = request.GET.get('cedula')
    estudiante_encontrado = None
    mensaje_grupo = None
    if cedula:
        try:
            estudiante_encontrado = Estudiante.objects.get(cedula=cedula)
            # Verifica si ya está en un grupo
            grupo = Grupos.objects.filter(estudiantes__contains=str(estudiante_encontrado.id)).first()
            if grupo:
                compañeros_ids = grupo.get_estudiantes()
                compañeros = Estudiante.objects.filter(id__in=compañeros_ids).exclude(id=estudiante_encontrado.id)
                mensaje_grupo = {
                    "trayecto": grupo.trayecto_cursante,
                    "docente_m": grupo.docente_metodologico,
                    "docente_a": grupo.docente_academico,
                    "compañeros": compañeros
                }
                estudiante_encontrado = None  # No permitir agregar
        except Estudiante.DoesNotExist:
            estudiante_encontrado = None
            messages.warning(request, "No se encontró un estudiante con esa cédula.")

    return render(request, 'registrar_grupo_individual.html', {
        'estudiantes_temp': estudiantes_temp,
        'estudiante_encontrado': estudiante_encontrado,
        'mensaje_grupo': mensaje_grupo,
    })

# Añadir estudiante a sesión
def agregar_estudiante_temp(request, estudiante_id):
    temp = request.session.get('temp_estudiantes', [])
    if estudiante_id not in temp and len(temp) < 4:
        temp.append(estudiante_id)
        request.session['temp_estudiantes'] = temp
    return redirect('registrar_grupo_individual')

# Limpiar sesión
def limpiar_estudiantes_temp(request):
    request.session['temp_estudiantes'] = []
    return redirect('registrar_grupo_individual')

# Registrar el grupo final
def guardar_grupo_individual(request):
    temp_estudiantes_ids = request.session.get('temp_estudiantes', [])
    if not temp_estudiantes_ids:
        messages.warning(request, "Debes agregar al menos un estudiante.")
        return redirect('registrar_grupo_individual')

    # Filtrar profesores por rol
    profesores_metodologicos = Profesores.objects.filter(role__in=['metodologico', 'completo'])
    profesores_academicos = Profesores.objects.filter(role__in=['academico', 'completo'])

    metodologicos_opciones = [(p.id, f"{p.nombre} {p.apellido}") for p in profesores_metodologicos]
    academicos_opciones = [(p.id, f"{p.nombre} {p.apellido}") for p in profesores_academicos]

    if request.method == 'POST':
        form = GruposForm(request.POST, metodologicos_opciones=metodologicos_opciones, academicos_opciones=academicos_opciones)
        if form.is_valid():
            grupo = form.save(commit=False)
            grupo.estudiantes = ','.join(str(id) for id in temp_estudiantes_ids)
            grupo.save()
            request.session['temp_estudiantes'] = []  # Limpiar luego de guardar
            return redirect('grupos_list')
    else:
        form = GruposForm(metodologicos_opciones=metodologicos_opciones, academicos_opciones=academicos_opciones)

    return render(request, 'guardar_grupo_individual.html', {
        'form': form,
        'estudiantes_temp': Estudiante.objects.filter(id__in=temp_estudiantes_ids)
    })



##########################################################################
def generar_pdf_grupos(request):
    # Crear un objeto HttpResponse con el tipo de contenido PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="grupos.pdf"'

    # Crear un objeto canvas de ReportLab
    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Ruta de la imagen del membrete
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo_iut_largo.jpg')

    # Dibujar el membrete en la parte superior
    pdf.drawImage(logo_path, 50, height - 100, width=500, height=80, preserveAspectRatio=True)

    # Agregar márgenes y estilos
    margin_x = 50
    margin_y = 50
    y_position = height - 150  # Ajustar para evitar superposición con el membrete

    # Título del documento
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(width / 2, y_position, "Reporte de Grupos")
    y_position -= 30  # Espacio después del título

    # Obtener todos los datos de los grupos
    grupos = Grupos.objects.all()

    # Iterar sobre los grupos y agregar los detalles al PDF
    for grupo in grupos:
        pdf.setFont("Helvetica", 12)

        # Información del trayecto y profesores
        docente_metodologico = Profesores.objects.get(id=grupo.docente_metodologico)
        docente_academico = Profesores.objects.get(id=grupo.docente_academico)

        pdf.drawString(margin_x, y_position, f"Trayecto: {grupo.trayecto_cursante}")
        y_position -= 15
        pdf.drawString(margin_x, y_position, f"Docente Metodológico: {docente_metodologico.nombre} {docente_metodologico.apellido}")
        y_position -= 15
        pdf.drawString(margin_x, y_position, f"Docente Académico: {docente_academico.nombre} {docente_academico.apellido}")
        y_position -= 15

        # Listar estudiantes
        pdf.drawString(margin_x, y_position, "Estudiantes:")
        y_position -= 15
        estudiantes = grupo.get_estudiantes()

        for estudiante_id in estudiantes:
            pdf.drawString(margin_x + 20, y_position, f"- {estudiante_id}")  # Indentar lista
            y_position -= 15

        y_position -= 20  # Espacio entre grupos

        # Saltar a la siguiente página si el espacio se acaba
        if y_position < margin_y:
            pdf.showPage()
            # Dibujar el membrete en la nueva página
            pdf.drawImage(logo_path, 50, height - 100, width=500, height=80, preserveAspectRatio=True)
            y_position = height - 150

    # Finalizar el PDF
    pdf.save()

    return response