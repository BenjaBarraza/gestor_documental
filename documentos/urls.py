from django.urls import path
from . import views
from .views import DocumentosUsuarioView


app_name = 'documentos'

urlpatterns = [
    path('', views.home, name='home'),
    path('subir/', views.subir_documento, name='subir'),
    path('lista/', views.listar_documentos, name='lista'),
    path('buscar/', views.buscar_documentos, name='buscar'),
    path('previsualizar/<int:documento_id>/', views.previsualizar_documento, name='previsualizar'),
    path('eliminar/<int:documento_id>/', views.eliminar_documento, name='eliminar_documento'),
    path('mis-enlaces/', views.mis_enlaces, name='mis_enlaces'),
    path('eliminar-enlace/<int:doc_id>/', views.eliminar_enlace_publico, name='eliminar_enlace_publico'),
    path('generar-enlace/<int:doc_id>/', views.generar_enlace, name='generar_enlace'),


    # API endpoints
    path('api/documentos/', DocumentosUsuarioView.as_view(), name='documentos_usuario'),

    
]
