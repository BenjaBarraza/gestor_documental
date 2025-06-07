from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import RegistroUsuarioForm, PerfilUsuarioForm
from .models import PerfilProfesional, PerfilEmpresarial
import requests
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.decorators import login_required




def registrar_usuario(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)

        # Capturar la respuesta de reCAPTCHA
        recaptcha_response = request.POST.get('g-recaptcha-response')

        data = {
            'secret': settings.RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        if result.get('success'):
            # ✅ reCAPTCHA correcto
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
                return redirect('usuarios:login')

            else:
                print("❌ Formulario inválido:", form.errors)
                return render(request, 'usuarios/registro.html', {
                    'form': form,
                    'recaptcha_site_key': settings.RECAPTCHA_SITE_KEY
                })
        else:
            # ❌ reCAPTCHA inválido
            messages.error(request, 'Por favor verifica que no eres un robot.')
            return render(request, 'usuarios/registro.html', {
                'form': form,
                'recaptcha_site_key': settings.RECAPTCHA_SITE_KEY
            })

    else:
        form = RegistroUsuarioForm()
        return render(request, 'usuarios/registro.html', {
            'form': form,
            'recaptcha_site_key': settings.RECAPTCHA_SITE_KEY
        })
    
    
@login_required
def perfil_usuario(request):
    perfil = request.user.perfilusuario
    return render(request, 'usuarios/perfil.html', {'usuario': request.user, 'perfil': perfil})



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
            return redirect('usuarios:editar_perfil')

        # ⚡ Validar que el email no esté en uso por otro usuario (opcional)
        if User.objects.exclude(pk=user.pk).filter(email=nuevo_email).exists():
            messages.error(request, 'El correo electrónico ya está en uso. Por favor elige otro.')
            return redirect('usuarios:editar_perfil')

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
        return redirect('usuarios:perfil')

    return render(request, 'usuarios/editar_perfil.html', {
        'usuario': user,
        'perfil': perfil,
    })



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
            return redirect('usuarios:perfil')
    else:
        form = PerfilUsuarioForm(instance=perfil, user=request.user)
    return render(request, 'usuarios/editar_perfil.html', {'form': form})