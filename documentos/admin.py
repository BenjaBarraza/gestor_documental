from django.contrib import admin
from .models import Documento

class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'usuario', 'fecha_subida')
    list_filter = ('usuario',)
    search_fields = ('nombre', 'etiquetas')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(usuario=request.user)

# ¡Evita registro duplicado!
if not admin.site.is_registered(Documento):
    admin.site.register(Documento, DocumentoAdmin)