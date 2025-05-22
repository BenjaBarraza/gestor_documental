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
from django.http import HttpResponseForbidden

# Vista de subida (solo para logueados)

def compartir_documento(request, enlace):
    documento = get_object_or_404(Documento, enlace_publico=enlace)

    es_pdf = documento.archivo.name.lower().endswith('.pdf')
    es_imagen = documento.archivo.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))

    return render(request, 'documentos/compartido.html', {
        'documento': documento,
        'es_pdf': es_pdf,
        'es_imagen': es_imagen,
    })


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
            documento = form.save(commit=False)
            documento.usuario = request.user  # 🔐 asociar con el usuario logueado
            documento.save()
            return redirect('documentos:lista')
    else:
        form = DocumentoForm()
    return render(request, 'documentos/subir.html', {'form': form})

# Vista de listado (solo documentos del usuario)
@login_required
def listar_documentos(request):
    if request.user.is_superuser:
        documentos = Documento.objects.all()
    else:
        documentos = Documento.objects.filter(usuario=request.user)

    # 👇 Agrega esta parte para dividir las etiquetas antes de enviar a la plantilla
    for doc in documentos:
        if doc.etiquetas:
            doc.etiquetas_lista = [e.strip() for e in doc.etiquetas.split(',')]
        else:
            doc.etiquetas_lista = []

    return render(request, 'documentos/lista.html', {'documentos': documentos})



@login_required
def buscar_documentos(request):
    query = request.GET.get("q", "").strip()
    documentos = Documento.objects.none()

    if query:
        documentos = Documento.objects.filter(
            Q(nombre__icontains=query) |
            Q(etiquetas__icontains=query) |
            Q(archivo__iendswith=query)  # ejemplo: "pdf" o ".pdf"
        )

        if not request.user.is_superuser:
            documentos = documentos.filter(usuario=request.user)

    return render(request, 'documentos/resultados_busqueda.html', {
        'documentos': documentos,
        'query': query,
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
    

    
    


    