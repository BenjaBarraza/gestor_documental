import os
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from documentos.models import Documento
from .forms import DocumentoForm 
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .forms import RegistroUsuarioForm
from django.db.models import Q

# Vista de subida (solo para logueados)


def home(request):
    return render(request, 'documentos/home.html')



def registrar_usuario(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            tipo = form.cleaned_data['tipo_cuenta']
            user.perfilusuario.tipo_cuenta = tipo
            user.perfilusuario.save()
            return redirect('login')
        else:
            print("❌ Formulario inválido:", form.errors)
    else:
        form = RegistroUsuarioForm()
    
    return render(request, 'documentos/registro.html', {'form': form})


@login_required
def subir_documento(request):
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            nuevo_doc = form.save(commit=False)
            nuevo_doc.usuario = request.user  # Asigna el usuario actual
            nuevo_doc.save()
            return redirect('documentos:home')
    else:
        form = DocumentoForm()
    return render(request, 'documentos/subir.html', {'form': form})

# Vista de listado (solo documentos del usuario)
@login_required
def listar_documentos(request):
    documentos = Documento.objects.filter(usuario=request.user)  # ¡Filtro clave!
    return render(request, 'documentos/lista.html', {'documentos': documentos})


@login_required
def buscar_documentos(request):
    query = request.GET.get('q', '')
    documentos = Documento.objects.filter(
        Q(nombre__icontains=query) | 
        Q(etiquetas__icontains=query),
        usuario=request.user  # Filtra solo documentos del usuario
    )
    return render(request, 'documentos/resultados_busqueda.html', {
        'documentos': documentos,
        'query': query
    })


@login_required
def previsualizar_documento(request, documento_id):
    documento = get_object_or_404(Documento, id=documento_id, usuario=request.user)  # Solo dueño puede ver
    extension = documento.archivo.name.split('.')[-1].lower()  # Obtener extensión (.pdf, .png, etc.)
    
    return render(request, 'documentos/previsualizar.html', {
        'documento': documento,
        'es_pdf': extension == 'pdf',
        'es_imagen': extension in ['jpg', 'jpeg', 'png', 'gif'],
    })


@require_POST
@login_required
def eliminar_documento(request, documento_id):
    try:
        documento = Documento.objects.get(id=documento_id, usuario=request.user)
        documento.archivo.delete()  # Elimina el archivo físico
        documento.delete()         # Elimina el registro de la BD
        return JsonResponse({'status': 'success'})
    except Documento.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Documento no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    


    