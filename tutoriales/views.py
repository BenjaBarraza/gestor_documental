from django.shortcuts import redirect, render
from .forms import FormularioContactoForm
from django.core.mail import EmailMultiAlternatives
from django.contrib import messages

def tutorial_view(request):
    return render(request, 'tutoriales/tutorial.html')

def explorar_funciones_view(request):
    return render(request, 'documentos/explorar_funciones.html')

def ayuda_view(request):
    if request.method == 'POST':
        form = FormularioContactoForm(request.POST)
        if form.is_valid():
            # Mandar correo al administrador
            messages.success(request, '¡Tu mensaje fue enviado exitosamente! 📬')
            return redirect('tutoriales:obtener_ayuda')
    else:
        form = FormularioContactoForm()
    return render(request, 'tutoriales/ayuda.html', {'form': form})
