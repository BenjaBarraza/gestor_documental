from django.contrib.auth.models import User
from rest_framework import serializers
from usuarios.models import PerfilUsuario
from documentos.models import Documento

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    tipo_cuenta = serializers.ChoiceField(choices=[('personal', 'Personal'), ('profesional', 'Profesional'), ('empresarial', 'Empresarial')])

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'tipo_cuenta']

    def create(self, validated_data):
        tipo_cuenta = validated_data.pop('tipo_cuenta')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        perfil = user.perfilusuario
        perfil.tipo_cuenta = tipo_cuenta
        perfil.save()
        return user



## Serializers for user profile and document management
class PerfilSerializer(serializers.ModelSerializer):
    tipo_cuenta = serializers.SerializerMethodField()
    documentos = serializers.SerializerMethodField()
    carpetas = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'email', 'tipo_cuenta', 'documentos', 'carpetas']

    def get_tipo_cuenta(self, obj):
        return getattr(obj.perfilusuario, 'tipo_cuenta', 'Personal')

    def get_documentos(self, obj):
        return Documento.objects.filter(usuario=obj).count()

    def get_carpetas(self, obj):
        return 0  # Si implementas carpetas en el futuro, lo actualizas aquí