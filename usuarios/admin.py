from django.contrib import admin
from .models import PerfilUsuario, PerfilProfesional, PerfilEmpresarial

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'tipo_cuenta')
    search_fields = ('user__username',)

@admin.register(PerfilProfesional)
class PerfilProfesionalAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'profesion', 'licencia', 'telefono', 'web_profesional')
    search_fields = ('usuario__username', 'profesion', 'licencia')

@admin.register(PerfilEmpresarial)
class PerfilEmpresarialAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'empresa', 'rut_empresa', 'giro', 'telefono', 'direccion', 'web_empresa')
    search_fields = ('usuario__username', 'empresa', 'rut_empresa')
