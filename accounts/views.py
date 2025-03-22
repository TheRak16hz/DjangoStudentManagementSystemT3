from rest_framework.decorators import api_view
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from .models import Estudiante, CustomUser
from .serializers import EstudianteSerializer
from .forms import *
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from django.conf import settings
from trayectos.models import Trayectos_all
from grupos.models import Grupos
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors

@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def estudiantesApi(request, id=0):
    if request.method == 'GET':
        estudiantes = Estudiante.objects.all()
        estudiantes_serializer = EstudianteSerializer(estudiantes, many=True)
        return Response(estudiantes_serializer.data)

    elif request.method == 'POST':
        estudiantes_serializer = EstudianteSerializer(data=request.data)
        if estudiantes_serializer.is_valid():
            estudiantes_serializer.save()
            return Response('Estudiante agregado', status=status.HTTP_201_CREATED)
        return Response(estudiantes_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PUT':
        estudiante = Estudiante.objects.get(pk=id)
        estudiantes_serializer = EstudianteSerializer(estudiante, data=request.data)
        if estudiantes_serializer.is_valid():
            estudiantes_serializer.save()
            return Response('Estudiante actualizado')
        return Response(estudiantes_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        estudiante = Estudiante.objects.get(pk=id)
        estudiante.delete()
        return Response('Estudiante eliminado')


########################FUNCIONES CRUD##############################
def estudiantes_view(request):
    return render(request, 'estudiantes_main.html')


def estudiantes_view_all(request):
    estudiantes = Estudiante.objects.all()
    estudiantes_eliminados = Estudiante.objects.filter(status__in=[False, False, 0])
    return render(request, 'estudiantes_ver_todos.html', {"estudiantes": estudiantes, "estudiantes_eliminados":estudiantes_eliminados, 'roles':request.session["staff_role"]})




def editar_estudiante(request, id):
    if request.method == "GET":
        estudiante = get_object_or_404(Estudiante, pk=id)
        form = EstudianteForm(instance=estudiante)
        #print(f"{estudiante.cedula}")
        #persuser = get_object_or_404(CustomUser, cedula=estudiante.cedula)
        #print(f"{persuser.email}")
        return render(request, "editar_estudiante.html", {"estudiante": estudiante, "form": form})
    elif request.method == "POST":
        try:
            estudiante = get_object_or_404(Estudiante, pk=id)
            form = EstudianteForm(request.POST, instance=estudiante)
            form.save()
            #print(f"{estudiante.cedula}") ###
            messages.success(request, 'Estudiante actualizado exitosamente.')
            return redirect("estudiantes_main")
        except ValueError:
            return render(request, "editar_estudiante.html", {"estudiante": estudiante, "form": form, "error": "Error updating estudiante"})
###
def activar_estudiante(request, id):
    if request.method == "POST":
        estudiante = get_object_or_404(Estudiante, pk=id)
        #print(estudiante.nombre)
        estudiante.status = True
        estudiante.save()
        
        messages.success(request, 'Estudiante activado exitosamente.')
        return redirect('estudiantes_main')
###

def eliminar_estudiante(request, id):
    if request.method == "GET":
        estudiante = get_object_or_404(Estudiante, pk=id)
        print(estudiante)
        return render(request, 'eliminar_estudiante.html', {"estudiante": estudiante})
    elif request.method == "POST":
        # Obtener al estudiante
        estudiante = get_object_or_404(Estudiante, pk=id)

        # Cambiar el estado a inactivo
        estudiante.status = False
        estudiante.save()

        # Eliminar el ID del estudiante de todos los grupos
        grupos = Grupos.objects.filter(estudiantes__icontains=str(estudiante.id))
        for grupo in grupos:
            estudiantes_ids = grupo.estudiantes.split(",")  # Convertir a lista
            estudiantes_ids = [e.strip() for e in estudiantes_ids if e.strip() != str(estudiante.id)]  # Remover el ID
            grupo.estudiantes = ", ".join(estudiantes_ids)  # Volver a unir la lista
            grupo.save()

        # Eliminar el registro de trayectos del estudiante
        try:
            last_year = Trayectos_all.objects.get(ref_cedula_id=estudiante.id).trayecto_año
            estudiante.ultimo_año_cursado = last_year
            estudiante.save()
        except:
            print("estudiante no estaba en trayectos")
        Trayectos_all.objects.filter(ref_cedula_id=estudiante.id).delete()
        
        #print(last_year)
        
        
        # Mensaje de éxito y redirección
        messages.success(request, 'Estudiante eliminado exitosamente.')
        return redirect('estudiantes_main')

def estudiantes_eliminados(request):
    # Filtrar profesores que tienen status=False (inactivos)
    estudiantes_inactivos = Estudiante.objects.all()
    # Renderizar el template y pasar los profesores inactivos al contexto
    return render(request, 'estudiantes_eliminados.html', {'estudiantes_inactivos': estudiantes_inactivos})

def generar_pdf_estudiantes(request):
    # Crear un objeto HttpResponse con el tipo de contenido adecuado para PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="estudiantes.pdf"'

    # Crear el objeto Canvas
    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    pdf.setTitle("Listado de Estudiantes")

    # Ruta de la imagen del encabezado
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo_iut_largo.jpg')
    logo_path = logo_path.replace('\\', '/')

    # Añadir el logotipo en el encabezado
    pdf.drawImage(ImageReader(logo_path), 40, height - 100, width=550, height=60)

    # Margen superior (después del logotipo)
    y = height - 150

    # Estilizar el título principal
    pdf.setFont("Helvetica-Bold", 16)
    pdf.setFillColor(colors.darkblue)
    pdf.drawString(220, y, "Listado de Estudiantes")
    y -= 30

    # Configuración de estilo general
    pdf.setFont("Helvetica", 12)
    pdf.setFillColor(colors.black)

    # Dibujar una línea divisoria después del encabezado
    pdf.setStrokeColor(colors.grey)
    pdf.setLineWidth(1)
    pdf.line(40, y, width - 40, y)
    y -= 20

    # Iterar sobre los estudiantes y generar contenido
    estudiantes = Estudiante.objects.all()
    for estudiante in estudiantes:
        # Verificar si hay espacio suficiente para contenido; si no, crear nueva página
        if y < 100:
            pdf.showPage()
            pdf.drawImage(ImageReader(logo_path), 40, height - 100, width=550, height=60)
            y = height - 150
            pdf.setFont("Helvetica-Bold", 16)
            pdf.setFillColor(colors.darkblue)
            pdf.drawString(220, y, "Listado de Estudiantes")
            y -= 30
            pdf.setFont("Helvetica", 12)
            pdf.setFillColor(colors.black)

        # Información del estudiante con separación y formato
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(100, y, f"Nombre Completo: {estudiante.nombre} {estudiante.apellido}")
        y -= 20

        pdf.setFont("Helvetica", 11)
        pdf.drawString(100, y, f"Cédula: {estudiante.cedula} | Email: {estudiante.email}")
        y -= 15
        pdf.drawString(100, y, f"Sección: {estudiante.seccion} | Fecha de Nacimiento: {estudiante.fecha_nacimiento}")
        y -= 15
        pdf.drawString(100, y, f"Teléfono: {estudiante.numero_telefono} | Dirección: {estudiante.direccion}")
        y -= 15
        pdf.drawString(100, y, f"Sexo: {estudiante.sexo} | Status: {'Activo' if estudiante.status else 'Inactivo'}")
        y -= 20

        # Dibujar línea divisoria entre estudiantes
        pdf.setStrokeColor(colors.lightgrey)
        pdf.setLineWidth(0.5)
        pdf.line(40, y, width - 40, y)
        y -= 20

    # Finalizar el PDF
    pdf.showPage()
    pdf.save()

    return response

def buscar_estudiante(request):
    estudiante = None
    form = BuscarEstudianteForm()

    if request.method == 'POST':
        form = BuscarEstudianteForm(request.POST)
        if form.is_valid():
            cedula = form.cleaned_data['cedula']
            try:
                # Realiza la búsqueda de estudiante por cédula
                estudiante = get_object_or_404(Estudiante, cedula=cedula)
            except Exception as e:
                # Manejar cualquier otra excepción que pueda ocurrir
                messages.error(request, f'Ocurrió un error: No se encontró un estudiante con esa cédula.')
                

    return render(request, 'buscar_estudiante.html', {'form': form, 'estudiante': estudiante})

def dashboard(request):
    estudiantes = Estudiante.objects.all()  # Obtener todos los estudiantes
    return render(request, 'dashboard.html', {'estudiantes': estudiantes})

