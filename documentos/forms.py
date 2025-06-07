from django import forms
from .models import Documento
from pillow_heif import register_heif_opener
from PIL import Image
import os
import io

from django.core.files.uploadedfile import InMemoryUploadedFile

register_heif_opener()


class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['nombre', 'archivo', 'etiquetas']

    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        if archivo:
            max_tamaño = 100 * 1024 * 1024  # 100 MB
            if archivo.size > max_tamaño:
                raise forms.ValidationError("El archivo supera el tamaño máximo de 100 MB.")

            content_type = archivo.content_type


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
                tipos_permitidos = [
                    'application/pdf',
                    'image/jpeg', 'image/png', 'image/webp',
                    'application/msword',
                    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'application/vnd.ms-excel',
                    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    'video/mp4', 'video/webm', 'video/ogg',
                ]
                if content_type not in tipos_permitidos:
                    raise forms.ValidationError(f"Tipo de archivo no permitido: {content_type}")

        return self.cleaned_data['archivo']

class EnlacePublicoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['fecha_expiracion']
        widgets = {
            'fecha_expiracion': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'},
                format='%Y-%m-%dT%H:%M'
            )
        }
        labels = {
            'fecha_expiracion': 'Fecha y hora de expiración del enlace'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha_expiracion'].input_formats = ['%Y-%m-%dT%H:%M']
