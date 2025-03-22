from django.urls import path
from . import views

urlpatterns = [
    # Otras rutas
    path('asignar_estudiantes/', views.asignar_estudiantes, name='asignar_estudiantes'),
    path('asignar_estudiantes_busqueda/', views.asignar_estudiantes_busqueda, name='asignar_estudiantes_busqueda'),
    path('trayecto_main/', views.trayectos_main, name="trayectos_main"),
    path('trayectos_view/', views.trayectos_view, name="trayectos_view"),
    path('trayectos_edit/<str:tr>/<int:id>/', views.trayectos_edit, name="trayectos_edit"),
    path('trayectos_delete/<str:tr>/<int:id>/', views.trayectos_delete, name="trayectos_delete"),
    path('trayectos_ya_asignados/', views.trayectos_ya_asignados, name="trayectos_ya_asignados"),
    path('buscar_estudiante_trayecto/', views.buscar_estudiante_trayecto, name="buscar_estudiante_trayecto"),
    path('trayectos_pdf/', views.trayectos_pdf, name="trayectos_pdf"),

    path('generar_pdf1/', views.generar_pdf_trayecto1, name='generar_pdf_trayecto1'),
    path('generar_pdf2/', views.generar_pdf_trayecto2, name='generar_pdf_trayecto2'),
    path('generar_pdf3/', views.generar_pdf_trayecto3, name='generar_pdf_trayecto3'),
    path('generar_pdf4/', views.generar_pdf_trayecto4, name='generar_pdf_trayecto4'),
]