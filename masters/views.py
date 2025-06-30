from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
#from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Profesores
from .forms import ProfesoresForm, BuscarProfesorForm
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from django.conf import settings
import os

# Create your views here.

def profesores_view(request):
    return render(request, 'profesores_main.html')

def profesores_view_all(request):
    profes = Profesores.objects.all()
    ### filtra si hay profesores con status False
    profes_eliminados = Profesores.objects.filter(status__in=[False, False, 0])
    #print(profes_eliminados)
    return render(request, 'profesores_ver_todos.html', {"profes": profes, "profes_eliminados":profes_eliminados, "roles":request.session["staff_role"]})

def profesores_search(request):
        profesor = None
        form = BuscarProfesorForm()
        if request.method == 'POST':
            form = BuscarProfesorForm(request.POST)
            if form.is_valid():
                cedula = form.cleaned_data['cedula']
                try:
                # Realiza la búsqueda de estudiante por cédula
                    profesor = get_object_or_404(Profesores, cedula=cedula)
                except Exception as e:
                # Manejar cualquier otra excepción que pueda ocurrir
                    messages.error(request, f'Ocurrió un error: No se encontró un estudiante con esa cédula.')
        return render(request, 'buscar_profe.html', {'form': form, 'profesor': profesor,  "roles":request.session["staff_role"]})

def crear_profe(request):
    if request.method == "GET":
        return render(request, 'crear_profe.html', {"form": ProfesoresForm()})
    else:
        try:
            form = ProfesoresForm(request.POST)
            if form.is_valid():
                profesor = form.save(commit=False)  # No guarda en la base aún
                profesor.save()  # Guarda el registro en la base de datos
                return redirect("profesores_view_all")
            else:
                # Renderiza la misma página si el formulario no es válido
                return render(request, 'crear_profe.html', {"form": form, "error": "Formulario inválido"})
        except Exception as e:
            # Captura cualquier error y lo muestra en el template
            return render(request, 'crear_profe.html', {"form": ProfesoresForm(), "error": str(e)})



def editar_profe(request, id):
    if request.method == "GET":
        profe = get_object_or_404(Profesores, pk=id)
        form = ProfesoresForm(instance=profe)
        return render(request, "editar_profe.html", {"profe": profe, "form": form})
    else:
        try:
            profe = get_object_or_404(Profesores, pk=id)
            form = ProfesoresForm(request.POST, instance=profe)
            form.save()
            messages.success(request, 'Profe actualizado exitosamente.')
            return redirect("profesores")
        except ValueError:
            return render(request, "editar_profe.html", {"profe": profe, "form": form, "error": "Error updating Prof"})

def activar_profe(request,id):
    if request.method == "POST":
        profe = get_object_or_404(Profesores, pk=id)
        print(profe.nombre)
        profe.status = True
        profe.save()
        messages.success(request, 'Profesor activado exitosamente.')
        return redirect('profesores_view_all')

def eliminar_profe(request, id):
    if request.method == "GET":
        profe = get_object_or_404(Profesores, pk=id)
        return render(request, 'eliminar_profe.html', {"profe": profe})
    if request.method == "POST":
        profe = get_object_or_404(Profesores, pk=id)
        profe.status = False
        profe.save()
        messages.success(request, 'Profesor eliminado exitosamente.')
        return redirect('profesores_view_all')
    


def profesores_eliminados(request):
    # Filtrar profesores que tienen status=False (inactivos)
    profes_inactivos = Profesores.objects.all()
    # Renderizar el template y pasar los profesores inactivos al contexto
    return render(request, 'profesores_eliminados.html', {'profes_inactivos': profes_inactivos})

def generar_pdf_profesores(request):
    # Crear un objeto HttpResponse con el tipo de contenido adecuado para PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="profesores.pdf"'

    # Crear el objeto Canvas
    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    pdf.setTitle("Listado de Profesores")

    # Ruta de la imagen del encabezado
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo_iut_largo.jpg')
    logo_path = logo_path.replace('\\', '/')

    # Añadir el logotipo en el encabezado
    pdf.drawImage(ImageReader(logo_path), 40, height - 100, width=550, height=60)

    # Margen superior después del logotipo
    y = height - 150

    # Estilizar el título principal
    pdf.setFont("Helvetica-Bold", 16)
    pdf.setFillColor(colors.darkblue)
    pdf.drawString(220, y, "Listado de Profesores")
    y -= 30

    # Dibujar línea divisoria después del título
    pdf.setStrokeColor(colors.grey)
    pdf.setLineWidth(1)
    pdf.line(40, y, width - 40, y)
    y -= 20

    # Configuración de estilo general
    pdf.setFont("Helvetica", 12)
    pdf.setFillColor(colors.black)

    # Iterar sobre los profesores y generar contenido
    profesores = Profesores.objects.all()
    for profesor in profesores:
        # Verificar si hay espacio suficiente; si no, crear nueva página
        if y < 100:
            pdf.showPage()
            pdf.drawImage(ImageReader(logo_path), 40, height - 100, width=550, height=60)
            y = height - 150
            pdf.setFont("Helvetica-Bold", 16)
            pdf.setFillColor(colors.darkblue)
            pdf.drawString(220, y, "Listado de Profesores")
            y -= 30
            pdf.setFont("Helvetica", 12)
            pdf.setFillColor(colors.black)
            pdf.setStrokeColor(colors.grey)
            pdf.line(40, y, width - 40, y)
            y -= 20

        # Información del profesor con separación y formato
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(100, y, f"Nombre Completo: {profesor.nombre} {profesor.apellido}")
        y -= 20

        pdf.setFont("Helvetica", 11)
        pdf.drawString(100, y, f"Cédula: {profesor.cedula} | Correo: {profesor.correo}")
        y -= 15
        pdf.drawString(100, y, f"Rol: {profesor.role} | Status: {'Activo' if profesor.status else 'Inactivo'}")
        y -= 20

        # Dibujar línea divisoria entre profesores
        pdf.setStrokeColor(colors.lightgrey)
        pdf.setLineWidth(0.5)
        pdf.line(40, y, width - 40, y)
        y -= 20

    # Finalizar el PDF
    pdf.showPage()
    pdf.save()

    return response