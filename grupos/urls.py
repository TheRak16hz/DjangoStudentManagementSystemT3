from django.urls import path
from . import views

urlpatterns = [
    path('grupos_main/', views.grupos_main, name='grupos_main'),
    path('registrar/', views.registrar_grupo, name='registrar_grupo'),
    path('grupos_ya_registrados/', views.grupos_ya_registrados, name='grupos_ya_registrados'),
    path('listar_grupos', views.listar_grupos, name='grupos_list'),
    path('eliminar/<int:grupo_id>/', views.eliminar_grupo, name='eliminar_grupo'),
    path('editar/<int:grupo_id>/', views.editar_grupo, name='editar_grupo'),
    path('buscar-estudiante/', views.buscar_estudiante_por_cedula, name='buscar_estudiante_por_cedula'),
    path('generar-pdf-grupos/', views.generar_pdf_grupos, name='generar_pdf_grupos'),
    path('grupos/<int:grupo_id>/eliminar_estudiante/<int:estudiante_id>/', views.eliminar_estudiante_grupo, name='eliminar_estudiante_grupo'),
    path('grupos/<int:grupo_id>/agregar_estudiantes/', views.agregar_estudiantes_grupo, name='agregar_estudiantes_grupo'),
    path('grupos/registrar_individual/', views.registrar_grupo_individual, name='registrar_grupo_individual'),
path('grupos/guardar_individual/', views.guardar_grupo_individual, name='guardar_grupo_individual'),
path('grupos/limpiar_temp/', views.limpiar_estudiantes_temp, name='limpiar_estudiantes_temp'),
path('grupos/agregar_temp/<int:estudiante_id>/', views.agregar_estudiante_temp, name='agregar_estudiante_temp'),



]
