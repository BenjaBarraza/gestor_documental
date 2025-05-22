from django.urls import path
from . import views


app_name = 'documentos'

urlpatterns = [
    path('', views.home, name='home'),
    path('subir/', views.subir_documento, name='subir'),
    path('lista/', views.listar_documentos, name='lista'),
    path('buscar/', views.buscar_documentos, name='buscar'),
    path('previsualizar/<int:documento_id>/', views.previsualizar_documento, name='previsualizar'),
    path('eliminar/<int:documento_id>/', views.eliminar_documento, name='eliminar_documento'),
    path('registro/', views.registrar_usuario, name='registrar'),
    path('compartir/<uuid:enlace>/', views.compartir_documento, name='compartir_documento'),
]