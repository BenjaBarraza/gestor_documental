import mimetypes
import os
import uuid
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from documentos.models import Documento, Recordatorio
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
from .forms import PerfilUsuarioForm
from .utils import calcular_estadisticas_profesional
from django.contrib.auth.models import User
from .forms import FormularioContactoForm
from django.shortcuts import render, redirect
from .forms import RecordatorioForm
from django.core.mail import EmailMultiAlternatives
from .forms import RegistroUsuarioForm
from .models import PerfilProfesional, PerfilEmpresarial  # Importa los nuevos perfiles si los tienes







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

            # ✅ Capturar los campos adicionales
            if tipo == 'Profesional':
                profesion = request.POST.get('profesion')
                licencia = request.POST.get('licencia')
                telefono = request.POST.get('telefono')
                web_profesional = request.POST.get('web_profesional')

                PerfilProfesional.objects.create(
                    usuario=user,
                    profesion=profesion,
                    licencia=licencia,
                    telefono=telefono,
                    web_profesional=web_profesional
                )

            elif tipo == 'Empresarial':
                empresa = request.POST.get('empresa')
                rut_empresa = request.POST.get('rut_empresa')
                giro = request.POST.get('giro')
                telefono_empresa = request.POST.get('telefono_empresa')
                direccion_empresa = request.POST.get('direccion_empresa')
                web_empresa = request.POST.get('web_empresa')

                PerfilEmpresarial.objects.create(
                    usuario=user,
                    empresa=empresa,
                    rut_empresa=rut_empresa,
                    giro=giro,
                    telefono=telefono_empresa,
                    direccion=direccion_empresa,
                    web_empresa=web_empresa
                )

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
            # 👇 Agrega este return
            return render(request, 'documentos/registro.html', {'form': form})

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
def perfil_usuario(request):
    perfil = request.user.perfilusuario  # Usa el modelo extendido
    return render(request, 'documentos/perfil.html', {
        'usuario': request.user,
        'perfil': perfil
    })



from django.contrib import messages
from django.contrib.auth.models import User

@login_required
def editar_perfil(request):
    user = request.user
    perfil = user.perfilusuario

    if request.method == 'POST':
        nuevo_username = request.POST.get('username')
        nuevo_email = request.POST.get('email')

        # ⚡ Validar que el username no esté en uso por otro usuario
        if User.objects.exclude(pk=user.pk).filter(username=nuevo_username).exists():
            messages.error(request, 'El nombre de usuario ya está en uso. Por favor elige otro.')
            return redirect('documentos:editar_perfil')

        # ⚡ Validar que el email no esté en uso por otro usuario (opcional)
        if User.objects.exclude(pk=user.pk).filter(email=nuevo_email).exists():
            messages.error(request, 'El correo electrónico ya está en uso. Por favor elige otro.')
            return redirect('documentos:editar_perfil')

        # Actualizar datos
        user.first_name = request.POST.get('nombre')
        user.username = nuevo_username
        user.email = nuevo_email
        perfil.telefono = request.POST.get('telefono')
        perfil.sitio_web = request.POST.get('sitio_web')

        if request.FILES.get('foto_perfil'):
            perfil.foto_perfil = request.FILES['foto_perfil']

        user.save()
        perfil.save()

        messages.success(request, 'Perfil actualizado exitosamente.')
        return redirect('documentos:perfil')

    return render(request, 'documentos/editar_perfil.html', {
        'usuario': user,
        'perfil': perfil,
    })


    

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


def vista_profesional(request):
    stats = calcular_estadisticas_profesional(request.user)
    documentos_recientes = Documento.objects.filter(usuario=request.user).order_by('-fecha_subida')[:6]
    return render(request, 'documentos/profesional_home.html', {
        'documentos_recientes': documentos_recientes,
        'stats': stats
    })

def vista_personal(request):
    return render(request, 'documentos/personal_home.html', {
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
    from .models import Recordatorio
    from .forms import RecordatorioForm
    recordatorios = Recordatorio.objects.filter(usuario=request.user).order_by('fecha_recordatorio')
    form = RecordatorioForm()

    return render(request, 'documentos/empresarial_home.html', {
        'stats': stats,
        'actividad': actividad_logs,
        'recordatorios': recordatorios,
        'form': form,
    })



def redireccion_dashboard(request):
    tipo = request.user.perfilusuario.tipo_cuenta
    if tipo == 'profesional':
        return redirect('documentos:vista_profesional')
    elif tipo == 'empresarial':
        return redirect('documentos:vista_empresarial')  # la crearemos más adelante
    elif tipo == 'personal':
        return redirect('documentos:vista_personal')
    else:
            # Puedes redirigir a una página de inicio, mostrar mensaje o bloquear
            return render(request, 'documentos/dashboard_no_disponible.html')
    



# Vista de ayuda y tutoriales
def tutorial_view(request):
    return render(request, 'documentos/tutorial.html')

def explorar_funciones_view(request):
    return render(request, 'documentos/explorar_funciones.html')  # Asegúrate de crear este HTML


@login_required
def configurar_perfil_view(request):
    perfil = request.user.perfilusuario
    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST, instance=perfil, user=request.user)
        if form.is_valid():
            request.user.email = form.cleaned_data['email']
            request.user.save()
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect('documentos:perfil')
    else:
        form = PerfilUsuarioForm(instance=perfil, user=request.user)
    return render(request, 'documentos/editar_perfil.html', {'form': form})





def ayuda_view(request):
    if request.method == 'POST':
        form = FormularioContactoForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            email = form.cleaned_data['email']
            mensaje = form.cleaned_data['mensaje']

            # 💡 Contenido HTML personalizado
            html_content = f"""
            <div style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                <div style="max-width: 600px; margin: auto; background: #ffffff; border-radius: 10px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); overflow: hidden;">
                    <div style="background: linear-gradient(90deg, #667eea, #764ba2); color: white; padding: 20px; text-align: center;">
                        <h2 style="margin: 0;">📩 Nuevo mensaje de contacto</h2>
                    </div>
                    <div style="padding: 30px;">
                        <p><strong>👤 Nombre:</strong> {nombre}</p>
                        <p><strong>✉️ Email:</strong> <a href="mailto:{email}" style="color: #667eea;">{email}</a></p>
                        <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
                        <p style="font-size: 16px; color: #555;"><strong>📝 Mensaje:</strong></p>
                        <p style="font-size: 16px; color: #333;">{mensaje}</p>
                        <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
                        <p style="font-size: 12px; color: #999; text-align: center;">Gestor Documental - {request.get_host()}</p>
                    </div>
                </div>
            </div>
            """

            # 💌 Email con HTML
            email_message = EmailMultiAlternatives(
                subject='📩 Nuevo mensaje de contacto - Gestor Documental',
                body='Este correo necesita soporte de HTML para verse correctamente.',
                from_email=None,  # Usa DEFAULT_FROM_EMAIL
                to=['antoniobarraza1133@gmail.com'],  # <-- Cambia a tu correo real
            )
            email_message.attach_alternative(html_content, "text/html")
            email_message.send()

            messages.success(request, '¡Tu mensaje fue enviado exitosamente! 📬')
            return redirect('documentos:obtener_ayuda')
    else:
        form = FormularioContactoForm()

    return render(request, 'documentos/ayuda.html', {'form': form})





# Vista para crear recordatorio (solo para usuarios logueados)
@login_required
def crear_recordatorio(request):
    if request.method == 'POST':
        form = RecordatorioForm(request.POST)
        if form.is_valid():
            recordatorio = form.save(commit=False)
            recordatorio.usuario = request.user
            recordatorio.save()
            return redirect('documentos:vista_empresarial')  # <--- ESTA ES LA URL QUE MUESTRA 'empresarial_home'
    else:
        form = RecordatorioForm()
    
    return redirect('documentos:vista_empresarial')

## Vista para eliminar recordatorio (solo para usuarios logueados)
@login_required
def eliminar_recordatorio(request, recordatorio_id):
    recordatorio = get_object_or_404(Recordatorio, id=recordatorio_id, usuario=request.user)
    recordatorio.delete()
    return redirect('documentos:vista_empresarial')
