from django.contrib import admin
from .models import Documento
from .models import PerfilProfesional, PerfilEmpresarial

class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'usuario', 'fecha_subida')
    list_filter = ('usuario',)
    search_fields = ('nombre', 'etiquetas')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(usuario=request.user)
    

    @admin.register(PerfilProfesional)
    class PerfilProfesionalAdmin(admin.ModelAdmin):
        list_display = ('usuario', 'profesion', 'licencia', 'telefono', 'web_profesional')
        search_fields = ('usuario__username', 'profesion', 'licencia')

    @admin.register(PerfilEmpresarial)
    class PerfilEmpresarialAdmin(admin.ModelAdmin):
        list_display = ('usuario', 'empresa', 'rut_empresa', 'giro', 'telefono', 'direccion', 'web_empresa')
        search_fields = ('usuario__username', 'empresa', 'rut_empresa')


# ¡Evita registro duplicado!
if not admin.site.is_registered(Documento):
    admin.site.register(Documento, DocumentoAdmin)