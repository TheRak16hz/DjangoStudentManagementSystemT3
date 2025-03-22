from django.urls import path
from .views import estudiantesApi
from . import views
urlpatterns = [
    path('estudiantes/', estudiantesApi),
    path('estudiantes/<int:id>/', estudiantesApi),
    path('estudiantes_main/', views.estudiantes_view, name="estudiantes_main"),
    path('editar_estudiante/<int:id>/', views.editar_estudiante, name="editar_estudiante"),
    path('eliminar_estudiante/<int:id>/', views.eliminar_estudiante, name="eliminar_estudiante"),
    path('activar_estudiante/<int:id>/', views.activar_estudiante, name='activar_estudiante'),
    path('estudiantes/inactivos/', views.estudiantes_eliminados, name="estudiantes_eliminados"),
    path('generar_pdf_estudiantes/', views.generar_pdf_estudiantes, name='generar_pdf_estudiantes'),
    path('buscar_estudiante_ci/', views.buscar_estudiante, name='buscar_estudiante_ci'),
    path('estudiantes_view_all/',views.estudiantes_view_all, name='estudiantes_ver_todos'),
]
