from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views

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
    path('eliminar_enlace/<int:doc_id>/', views.eliminar_enlace_publico, name='eliminar_enlace_publico'),
    path('prueba-email/', views.prueba_email, name='prueba_email'),

    # URLs de autenticación
    path('login/', auth_views.LoginView.as_view(template_name='documentos/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='documentos:login'), name='logout'),

    # URLs de password reset (versión definitiva)
    path('reset-password/', auth_views.PasswordResetView.as_view(template_name='documentos/password_reset.html',email_template_name='documentos/password_reset_email.html',html_email_template_name='documentos/password_reset_email.html',subject_template_name='documentos/password_reset_subject.txt',success_url=reverse_lazy('documentos:password_reset_done')), name='password_reset'),
    path('reset-password/enviado/', auth_views.PasswordResetDoneView.as_view(template_name='documentos/password_reset_done.html'), name='password_reset_done'),
    path('reset-password/confirmar/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='documentos/password_reset_confirm.html',success_url=reverse_lazy('documentos:password_reset_complete')), name='password_reset_confirm'),
    path('reset-password/completado/', auth_views.PasswordResetCompleteView.as_view(template_name='documentos/password_reset_complete.html'), name='password_reset_complete'),

    #URLs perfil de usuario 
    path('perfil/', views.perfil_usuario, name='perfil'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),


    # URLs del dashboard
    path('dashboard/empresarial/', views.vista_empresarial, name='vista_empresarial'),
    path('dashboard/profesional/', views.vista_profesional, name='vista_profesional'),
    path('dashboard/', views.redireccion_dashboard, name='dashboard'),
    path('dashboard/personal/', views.vista_personal, name='vista_personal'),

    # URLs de ayuda y tutoriales
    path('tutorial/', views.tutorial_view, name='tutorial'),
    path('explorar-funciones/', views.explorar_funciones_view, name='explorar_funciones'),
    path('ayuda/', views.ayuda_view, name='obtener_ayuda'),
    path('perfil/', views.configurar_perfil_view, name='configurar_perfil'),




]
