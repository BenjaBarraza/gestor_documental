from django.contrib.auth.models import User
from rest_framework import serializers
from usuarios.models import PerfilUsuario

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
