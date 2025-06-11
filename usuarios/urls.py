from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views

app_name = 'usuarios'

urlpatterns = [
    # Registro y perfil
    path('registro/', views.registrar_usuario, name='registro'),
    path('perfil/', views.perfil_usuario, name='perfil'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('perfil/configurar/', views.configurar_perfil_view, name='configurar_perfil'),

    # Autenticación
    path('login/', auth_views.LoginView.as_view(template_name='usuarios/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='usuarios:login'), name='logout'),

    # ✅ Restablecimiento de contraseña 
    path(
        'reset-password/',
        auth_views.PasswordResetView.as_view(
            template_name='usuarios/password_reset.html',
            email_template_name='usuarios/password_reset_email.html',
            html_email_template_name='usuarios/password_reset_email.html',  
            subject_template_name='usuarios/password_reset_subject.txt',
            success_url=reverse_lazy('usuarios:password_reset_done'),
            extra_context={'site_name': 'GestorDocs'}
        ),
        name='password_reset'
    ),

    path(
        'reset-password/enviado/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='usuarios/password_reset_done.html'
        ),
        name='password_reset_done',
    ),
    path(
        'reset-password/confirmar/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='usuarios/password_reset_confirm.html',
            success_url=reverse_lazy('usuarios:password_reset_complete'),
        ),
        name='password_reset_confirm',
    ),
    path(
        'reset-password/completado/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='usuarios/password_reset_complete.html'
        ),
        name='password_reset_complete',
    ),
]
