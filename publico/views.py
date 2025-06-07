from django.shortcuts import render, get_object_or_404
from documentos.models import Documento
from django.utils import timezone

def documento_publico(request, enlace):
    documento = get_object_or_404(Documento, enlace_publico=enlace)
    if documento.fecha_expiracion and timezone.now() > documento.fecha_expiracion:
        return render(request, 'publico/enlace_expirado.html', status=403)
    return render(request, 'publico/documento_publico.html', {'documento': documento})
