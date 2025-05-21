from django import forms
from .models import Documento
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['nombre', 'archivo', 'etiquetas']

def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        if archivo:
            # Validación de tamaño (5 MB max)
            max_tamaño = 5 * 1024 * 1024  # 5 MB
            if archivo.size > max_tamaño:
                raise forms.ValidationError("El archivo supera el tamaño máximo de 5 MB.")

            # Validación de tipo
            tipos_permitidos = ['application/pdf', 'image/jpeg', 'image/png', 'application/msword',
                                'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
            if archivo.content_type not in tipos_permitidos:
                raise forms.ValidationError("Tipo de archivo no permitido.")
        return archivo



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
