from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

TIPO_CUENTA_CHOICES = [
    ('personal', 'Personal'),
    ('profesional', 'Profesional'),
    ('empresarial', 'Empresarial'),
]

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo_cuenta = models.CharField(max_length=20, choices=TIPO_CUENTA_CHOICES)
    foto_perfil = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.tipo_cuenta}"

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.create(user=instance)

class PerfilProfesional(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    profesion = models.CharField(max_length=100)
    licencia = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True)
    web_profesional = models.URLField(blank=True)

class PerfilEmpresarial(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    empresa = models.CharField(max_length=150)
    rut_empresa = models.CharField(max_length=50)
    giro = models.CharField(max_length=100, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.TextField(blank=True)
    web_empresa = models.URLField(blank=True)
