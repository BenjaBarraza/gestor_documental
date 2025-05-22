from django import forms
from .models import Documento
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# === NUEVO ===
from pillow_heif import register_heif_opener
from PIL import Image
import os
import io
import sys
from django.core.files.uploadedfile import InMemoryUploadedFile

register_heif_opener()

# ------------------------------
# Formulario para subir documentos
# ------------------------------
class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['nombre', 'archivo', 'etiquetas']

    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        if archivo:
            # Validación de tamaño (100 MB máx)
            max_tamaño = 100 * 1024 * 1024
            if archivo.size > max_tamaño:
                raise forms.ValidationError("El archivo supera el tamaño máximo de 100 MB.")

            content_type = archivo.content_type

            # Conversión de .heic/.heif a .jpg
            if content_type in ['image/heic', 'image/heif'] or archivo.name.lower().endswith(('.heic', '.heif')):
                try:
                    imagen = Image.open(archivo)
                    output_io = io.BytesIO()
                    imagen.save(output_io, format="JPEG")

                    nuevo_archivo = InMemoryUploadedFile(
                        output_io,
                        'archivo',
                        os.path.splitext(archivo.name)[0] + ".jpg",
                        'image/jpeg',
                        output_io.getbuffer().nbytes,
                        None
                    )
                    self.cleaned_data['archivo'] = nuevo_archivo

                except Exception as e:
                    raise forms.ValidationError(f"Error al convertir HEIC: {str(e)}")

            else:
                # Tipos MIME permitidos
                tipos_permitidos = [
                    'application/pdf',
                    'image/jpeg', 'image/png', 'image/webp',
                    'application/msword',
                    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'video/mp4', 'video/webm', 'video/ogg',
                    'application/octet-stream'
                ]
                if content_type not in tipos_permitidos:
                    raise forms.ValidationError(f"Tipo de archivo no permitido: {content_type}")

        return self.cleaned_data['archivo']

# ------------------------------
# Formulario de registro de usuarios
# ------------------------------
TIPO_CUENTA_CHOICES = [
    ('personal', 'Personal'),
    ('profesional', 'Profesional'),
    ('empresarial', 'Empresarial'),
]

class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Correo electrónico')
    first_name = forms.CharField(label='Nombre completo')
    tipo_cuenta = forms.ChoiceField(
        choices=TIPO_CUENTA_CHOICES,
        label='Tipo de cuenta',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'email', 'username', 'password1', 'password2']

# ------------------------------
# Formulario para generar enlace con fecha de expiración
# ------------------------------
class EnlacePublicoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['fecha_expiracion']
        widgets = {
            'fecha_expiracion': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            )
        }
        labels = {
            'fecha_expiracion': 'Fecha y hora de expiración del enlace'
        }
