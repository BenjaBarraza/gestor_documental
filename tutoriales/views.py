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
