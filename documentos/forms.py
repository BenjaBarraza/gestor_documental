from django import forms
from .models import Documento
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['nombre', 'archivo', 'etiquetas']



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
