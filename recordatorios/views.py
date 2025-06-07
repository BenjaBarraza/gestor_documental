from django.shortcuts import render, redirect, get_object_or_404
from .forms import RecordatorioForm
from .models import Recordatorio
from django.contrib.auth.decorators import login_required


# Vista para crear recordatorio (solo para usuarios logueados)
@login_required
def crear_recordatorio(request):
    if request.method == 'POST':
        form = RecordatorioForm(request.POST)
        if form.is_valid():
            recordatorio = form.save(commit=False)
            recordatorio.usuario = request.user
            recordatorio.save()
            return redirect('dashboard:vista_empresarial')  # <--- ESTA ES LA URL QUE MUESTRA 'empresarial_home'
    else:
        form = RecordatorioForm()
    
    return redirect('dashboard:vista_empresarial')

## Vista para eliminar recordatorio (solo para usuarios logueados)
@login_required
def eliminar_recordatorio(request, recordatorio_id):
    recordatorio = get_object_or_404(Recordatorio, id=recordatorio_id, usuario=request.user)
    recordatorio.delete()
    return redirect('dashboard:vista_empresarial')
