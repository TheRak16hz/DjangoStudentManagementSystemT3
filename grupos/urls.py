from django.urls import path
from . import views

urlpatterns = [
    path('registrar/', views.registrar_grupo, name='registrar_grupo'),
    path('listar_grupos', views.listar_grupos, name='grupos_list'),  
    path('eliminar/<int:grupo_id>/', views.eliminar_grupo, name='eliminar_grupo'),
    path('editar/<int:grupo_id>/', views.editar_grupo, name='editar_grupo'),
    path('buscar-estudiante/', views.buscar_estudiante_por_cedula, name='buscar_estudiante_por_cedula'),
    path('generar-pdf-grupos/', views.generar_pdf_grupos, name='generar_pdf_grupos'),
]
