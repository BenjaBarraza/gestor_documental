from django.urls import path
from ... import views


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
    path('generar-enlace/<int:doc_id>/', views.generar_enlace, name='generar_enlace'),
    path('publico/<str:enlace>/', views.documento_publico, name='documento_publico'),
    path('compartido/<str:enlace>/', views.documento_publico, name='documento_publico'),
    path('publico/<uuid:enlace>/', views.documento_publico, name='documento_publico'),
    path('mis-enlaces/', views.mis_enlaces, name='mis_enlaces'),
    path('eliminar_enlace/<int:doc_id>/', views.eliminar_enlace_publico, name='documentos:eliminar_enlace_publico'),
    path('prueba-email/', views.prueba_email, name='prueba_email'),
    #path('ver-correo/', views.ver_correo_generado, name='ver_correo'),


]