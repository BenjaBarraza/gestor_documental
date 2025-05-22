import mimetypes
import os
import uuid
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from documentos.models import Documento
from .forms import DocumentoForm 
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden, JsonResponse
from .forms import RegistroUsuarioForm
from django.db.models import Q
from .forms import EnlacePublicoForm
from django.utils import timezone
from django.utils.timezone import now
from django.contrib import messages
from django.core.mail import send_mail
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.contrib import messages





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

            # ✅ Enviar correo de bienvenida
            try:
                html_bienvenida = render_to_string("emails/bienvenida.html", {
                    'usuario': user,
                    'request': request,
                })

                email = EmailMultiAlternatives(
                    subject='🎉 ¡Bienvenido a Gestor Docs!',
                    body='Tu cliente de correo no admite HTML.',
                    from_email=None,
                    to=[user.email],
                )
                email.attach_alternative(html_bienvenida, "text/html")
                email.send()
                print(f"✅ Correo de bienvenida enviado a {user.email}")
            except Exception as e:
                print("❌ Error al enviar correo de bienvenida:", e)

            # ✅ Mensaje de éxito
            messages.success(request, '🎉 ¡Registro exitoso! Te hemos enviado un correo de bienvenida.')

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
            documento.usuario = request.user
            documento.save()

            # Mensaje si el archivo fue .heic y se convirtió a .jpg
            if (
                form.cleaned_data['archivo'].name.lower().endswith('.jpg') and
                request.FILES['archivo'].name.lower().endswith('.heic')
            ):
                messages.info(
                    request,
                    "El archivo .HEIC fue convertido automáticamente a .JPG para que puedas visualizarlo en tu navegador."
                )

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
    documento = get_object_or_404(Documento, id=documento_id)

    if not request.user.is_superuser and documento.usuario != request.user:
        return render(request, 'documentos/403.html', status=403)

    mimetype, _ = mimetypes.guess_type(documento.archivo.url)
    es_pdf = mimetype == 'application/pdf'
    es_imagen = mimetype and mimetype.startswith('image/')
    es_video = mimetype and mimetype.startswith('video/')

    return render(request, 'documentos/previsualizar.html', {
        'documento': documento,
        'es_pdf': es_pdf,
        'es_imagen': es_imagen,
        'es_video': es_video,
    })



@require_POST
@login_required
def eliminar_documento(request, documento_id):
    documento = get_object_or_404(Documento, id=documento_id)

    # Verificación de permisos
    if not request.user.is_superuser and documento.usuario != request.user:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Acceso denegado'}, status=403)
        else:
            return render(request, 'documentos/prohibido.html', status=403)

    try:
        documento.archivo.delete()
        documento.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    


@login_required
def generar_enlace(request, doc_id):
    documento = get_object_or_404(Documento, id=doc_id)

    # Verificación de permisos
    if not request.user.is_superuser and documento.usuario != request.user:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Acceso denegado'}, status=403)
        else:
            return render(request, 'documentos/prohibido.html', status=403)

    if request.method == 'POST':
        form = EnlacePublicoForm(request.POST)
        if form.is_valid():
            # Guardar expiración y enlace único
            documento.fecha_expiracion = form.cleaned_data['fecha_expiracion']
            documento.enlace_publico = str(uuid.uuid4())
            documento.save()

            # Construir enlace absoluto
            enlace_url = request.build_absolute_uri(f"/publico/{documento.enlace_publico}")

            # Guardar en sesión para mostrar tras redirect
            request.session['enlace_generado'] = enlace_url

            # ✉️ Enviar correo al usuario
            try:
                html_content = render_to_string("emails/enlace_generado.html", {
                    'usuario': request.user,
                    'documento': documento,
                    'enlace_url': enlace_url,
                })

                email = EmailMultiAlternatives(
                    subject='🔗 Enlace público generado',
                    body='Tu cliente de correo no admite HTML.',
                    from_email=None,  # usa DEFAULT_FROM_EMAIL
                    to=[request.user.email],
                )
                email.attach_alternative(html_content, "text/html")
                email.send()
                print(f"✅ Correo enviado a: {request.user.email}")
            except Exception as e:
                print("❌ ERROR al enviar correo:", e)

            return redirect('documentos:generar_enlace', doc_id=doc_id)
    else:
        form = EnlacePublicoForm(initial={'fecha_expiracion': documento.fecha_expiracion})

    enlace_generado = request.session.pop('enlace_generado', None)

    return render(request, 'documentos/generar_enlace.html', {
        'documento': documento,
        'form': form,
        'enlace_generado': enlace_generado,
    })




def documento_publico(request, enlace):
    documento = get_object_or_404(Documento, enlace_publico=enlace)

    # Validar expiración del enlace
    if documento.fecha_expiracion and timezone.now() > documento.fecha_expiracion:
        return render(request, 'documentos/enlace_expirado.html', status=403)

    # (Futuro) Validar si requiere contraseña y no se ha ingresado

    return render(request, 'documentos/compartido.html', {'documento': documento})



@login_required
def mis_enlaces(request):
    documentos = Documento.objects.filter(usuario=request.user).exclude(enlace_publico__isnull=True)
    return render(request, 'documentos/mis_enlaces.html', {
        'documentos': documentos,
        'ahora': now()
    })

from django.http import JsonResponse

@require_POST
@login_required
def eliminar_enlace_publico(request, doc_id):
    documento = get_object_or_404(Documento, id=doc_id, usuario=request.user)
    documento.enlace_publico = None
    documento.fecha_expiracion = None
    documento.save()

    # Respuesta AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    # Respuesta clásica
    return JsonResponse({'success': True})

    

@login_required
def prueba_email(request):
    send_mail(
        subject='📧 Prueba de correo desde Gestor Documental',
        message='¡Hola! Este es un correo de prueba enviado desde tu aplicación Django con Gmail.',
        from_email=None,
        recipient_list=[request.user.email],
        fail_silently=False,
    )
    return HttpResponse("Correo de prueba enviado a: " + request.user.email)




#@login_required
#def ver_correo_generado(request):
 #   from django.template.loader import render_to_string

  #  html = render_to_string("emails/enlace_generado.html", {
   #     'usuario': request.user,
    #    'documento': Documento.objects.filter(usuario=request.user).last(),
     #   'enlace_url': 'http://localhost:8000/publico/fake-enlace-prueba'
    #})

    #return HttpResponse(html)

    