from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

class Documento(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documentos')  # este se mantiene
    archivo = models.FileField(upload_to='documentos/')
    nombre = models.CharField(max_length=200)
    etiquetas = models.CharField(max_length=100, blank=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre
    
TIPO_CUENTA_CHOICES = [
    ('personal', 'Personal'),
    ('profesional', 'Profesional'),
    ('empresarial', 'Empresarial'),
]

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo_cuenta = models.CharField(max_length=20, choices=TIPO_CUENTA_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.tipo_cuenta}"
    
    @receiver(post_save, sender=User)
    def crear_perfil_usuario(sender, instance, created, **kwargs):
        if created:
            PerfilUsuario.objects.create(user=instance)