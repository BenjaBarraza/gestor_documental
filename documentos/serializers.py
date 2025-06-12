from rest_framework import serializers
from .models import Documento

class DocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Documento
        fields = [
            'id',
            'nombre',
            'archivo',
            'etiquetas',
            'fecha_subida',
            'usuario',
            'enlace_publico',
            'expiracion_enlace',
            'fecha_expiracion',
            'activo',
            'size',
            'is_shared',
        ]
