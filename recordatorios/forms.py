from django import forms
from .models import Recordatorio

class RecordatorioForm(forms.ModelForm):
    class Meta:
        model = Recordatorio
        fields = ['titulo', 'fecha_recordatorio']
        widgets = {
            'fecha_recordatorio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
        }
