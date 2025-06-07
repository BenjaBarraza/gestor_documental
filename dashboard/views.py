from django.shortcuts import render, redirect
from documentos.models import Documento
from recordatorios.forms import RecordatorioForm
from recordatorios.models import Recordatorio
from documentos.utils import calcular_estadisticas_profesional
from usuarios.models import PerfilUsuario
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required



@login_required
def vista_profesional(request):
    stats = calcular_estadisticas_profesional(request.user)
    documentos_recientes = Documento.objects.filter(usuario=request.user).order_by('-fecha_subida')[:6]
    return render(request, 'dashboard/profesional_home.html', {
        'documentos_recientes': documentos_recientes,
        'stats': stats
    })

@login_required
def vista_personal(request):
    return render(request, 'dashboard/personal_home.html', {
        'nombre': request.user.get_full_name(),
        'correo': request.user.email,
        'tipo': request.user.perfilusuario.tipo_cuenta
    })

@login_required
def vista_empresarial(request):
    equipo = User.objects.filter(perfilusuario__tipo_cuenta='empresarial')
    documentos_equipo = Documento.objects.filter(usuario__in=equipo)

    total_documentos = documentos_equipo.count()
    espacio_total_gb = round(sum(doc.size or 0 for doc in documentos_equipo) / (1024 * 1024), 2)
    inicio_semana = timezone.now() - timedelta(days=7)
    miembros_activos = documentos_equipo.filter(fecha_subida__gte=inicio_semana).values('usuario').distinct().count()
    documentos_compartidos = documentos_equipo.filter(enlace_publico__isnull=False).count()


    actividad = documentos_equipo.order_by('-fecha_subida')[:10]
    actividad_logs = [
        f"{doc.usuario.username} subió «{doc.nombre}» el {doc.fecha_subida.strftime('%d-%m-%Y %H:%M')}"
        for doc in actividad
    ]

    stats = {
        'total_documentos': total_documentos,
        'espacio_usado': espacio_total_gb,
        'miembros_activos': miembros_activos,
        'documentos_compartidos': documentos_compartidos,
    }

    # 💡 Agrega recordatorios
    recordatorios = Recordatorio.objects.filter(usuario=request.user).order_by('fecha_recordatorio')
    form = RecordatorioForm()

    return render(request, 'dashboard/empresarial_home.html', {
        'stats': stats,
        'actividad': actividad_logs,
        'recordatorios': recordatorios,
        'form': form,
    })

@login_required
def redireccion_dashboard(request):
    tipo = request.user.perfilusuario.tipo_cuenta
    if tipo == 'profesional':
        return redirect('dashboard:vista_profesional')
    elif tipo == 'empresarial':
        return redirect('dashboard:vista_empresarial')
    elif tipo == 'personal':
        return redirect('dashboard:vista_personal')
    else:
        return render(request, 'dashboard/dashboard_no_disponible.html')
