from django import forms
from .models import Documento
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

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
            # Validación de tamaño (ahora 100 MB máx)
            max_tamaño = 100 * 1024 * 1024  # 100 MB
            if archivo.size > max_tamaño:
                raise forms.ValidationError("El archivo supera el tamaño máximo de 100 MB.")

            # Validación de tipo: incluye videos
            tipos_permitidos = [
                'application/pdf',
                'image/jpeg', 'image/png',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'video/mp4', 'video/webm', 'video/ogg'
            ]
            if archivo.content_type not in tipos_permitidos:
                raise forms.ValidationError("Tipo de archivo no permitido.")
        return archivo


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
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )

    class Meta:
        model = User
        fields = ['first_name', 'email', 'username', 'password1', 'password2']

# ------------------------------
# NUEVO: Formulario para generar enlace con fecha de expiración
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
