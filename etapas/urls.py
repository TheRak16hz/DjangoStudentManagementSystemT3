from django.urls import path
from . import views

urlpatterns = [
    path('', views.etapas_main, name='etapas_main'),
    path('home/', views.home_etapas, name="home_etapas"),
    path('gestionar-etapa/<int:grupo_id>/', views.gestionar_etapa, name='gestionar_etapa'),
    path('eliminar/<str:grupo_id>/', views.eliminar_etapa, name='eliminar_etapa'),
    path('asignar/<str:grupo_id>/', views.asignar_etapa, name='asignar_etapa'),
    path('buscar_etapas/', views.buscar_etapas, name='buscar_etapas'),
]