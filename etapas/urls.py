from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_etapas, name="home_etapas"),
    path('gestionar-etapa/<int:grupo_id>/', views.editar_etapa, name='gestionar_etapa'),
]