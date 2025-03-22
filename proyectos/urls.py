from django.urls import path, include
from . import views
from masters import urls

urlpatterns = [
    path('', views.proyectos_home, name='home_pp'),
    path('subir/', views.subir_archivo, name='subir_archivo'),
    path('listar_all/', views.listar_archivos_all, name='listar_archivos_all'),
    path('listar/', views.listar_archivos, name='listar_archivos'),
    path('editar/<int:archivo_id>/', views.editar_archivo, name='editar_archivo'),
    path('eliminar/<int:archivo_id>/', views.eliminar_archivo, name='eliminar_archivo'),
]
