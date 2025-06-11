from django.core.mail import send_mail
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

@login_required
def prueba_email(request):
    send_mail(
        subject='📧 Prueba de correo desde Gestor Documental',
        message='¡Hola! Este es un correo de prueba.',
        from_email=None,
        recipient_list=[request.user.email],
        fail_silently=False,
    )
    return HttpResponse(f"Correo de prueba enviado a: {request.user.email}")