from django.shortcuts import render, redirect, get_object_or_404
from .forms import GruposForm
from .models import Grupos
from masters.models import Profesores
from accounts.models import Estudiante
from django.db import DatabaseError
from django.http import JsonResponse
from django.contrib import messages
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.http import HttpResponse
from django.conf import settings
import os

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

    # Obtener todos los estudiantes
    estudiantes = Estudiante.objects.all()

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
        'estudiantes': estudiantes,  # Pasar los estudiantes al template
        'ids_estudiantes_grupos': ids_estudiantes_grupos  # Pasar los IDs de estudiantes asignados
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
    
    if request.method == 'POST':
        grupo.delete()
        messages.success(request, 'El grupo ha sido eliminado exitosamente.')
        return redirect('grupos_list')  # Redirige a la lista de grupos
    
    return render(request, 'confirmar_eliminar_grupo.html', {'grupo': grupo})

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
        'estudiantes_seleccionados': estudiantes_seleccionados_ids  # Para preseleccionar los estudiantes
    })

def buscar_estudiante_por_cedula(request):
    estudiante_encontrado = None
    grupo_encontrado = None

    if request.method == 'POST':
        cedula = request.POST.get('cedula')

        try:
            # Verificar si el estudiante con la cédula existe
            estudiante_encontrado = Estudiante.objects.get(cedula=cedula)
            estudiante_id = estudiante_encontrado.id

            # Buscar grupos que contengan el ID del estudiante
            grupos = Grupos.objects.all()
            for grupo in grupos:
                # Limpiar la lista de IDs de estudiantes
                estudiantes_ids = [est_id.strip() for est_id in grupo.get_estudiantes() if est_id.strip()]
                
                # Convertir solo los valores válidos a enteros
                estudiantes_ids = [int(est_id) for est_id in estudiantes_ids if est_id.isdigit()]
                
                if estudiante_id in estudiantes_ids:
                    grupo_encontrado = grupo
                    break  # Detener la búsqueda una vez encontrado

        except Estudiante.DoesNotExist:
            estudiante_encontrado = None

    return render(request, 'buscar_estudiante_g.html', {
        'estudiante_encontrado': estudiante_encontrado,
        'grupo_encontrado': grupo_encontrado
    })

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