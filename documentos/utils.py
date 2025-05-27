from datetime import datetime
from django.utils import timezone
from .models import Documento

def calcular_estadisticas_profesional(usuario):
    ahora = timezone.now()
    inicio_mes = ahora.replace(day=1)

    # Documentos subidos este mes
    subidos_mes = Documento.objects.filter(
        usuario=usuario,
        fecha_subida__gte=inicio_mes
    ).count()

    # Documentos compartidos (si usas un campo tipo booleano o fecha de compartido)
    compartidos = Documento.objects.filter(
        usuario=usuario,
        enlace_publico__isnull=False  # o usa tu propio campo de "compartido"
    ).count()

    # Espacio total utilizado (asumiendo campo `archivo`)
    documentos_usuario = Documento.objects.filter(usuario=usuario)
    espacio_total = sum(doc.archivo.size for doc in documentos_usuario) / (1024 * 1024)  # en MB

    return {
        'subidos_mes': subidos_mes,
        'compartidos': compartidos,
        'espacio_usado': round(espacio_total, 2)
    }
