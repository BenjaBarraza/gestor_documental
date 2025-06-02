from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
import uuid
from django.utils import timezone
from datetime import timedelta

class Documento(models.Model):
    nombre = models.CharField(max_length=200)
    archivo = models.FileField(upload_to='documentos/')
    etiquetas = models.CharField(max_length=100, blank=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    enlace_publico = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, null=True, blank=True)
    expiracion_enlace = models.DateTimeField(blank=True, null=True)
    fecha_expiracion = models.DateTimeField(null=True, blank=True)
    activo = models.BooleanField(default=True)


    # ➕ CAMPOS ADICIONALES: Perfiles de usuario Profesional y Empresarial
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




    # ➕ NUEVOS CAMPOS:
    size = models.PositiveIntegerField(blank=True, null=True)  # tamaño en KB
    is_shared = models.BooleanField(default=False)             # si el documento fue compartido

    def save(self, *args, **kwargs):
        # Asigna el tamaño del archivo automáticamente al guardar si no existe
        if self.archivo and not self.size:
            self.size = self.archivo.size // 1024  # Guarda en KB (kilobytes)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

    def generar_enlace_publico(self, duracion_horas=24):
        self.enlace_publico = uuid.uuid4().hex
        self.expiracion_enlace = timezone.now() + timedelta(hours=duracion_horas)
        self.is_shared = True  # Marca como compartido
        self.save()

    def enlace_expirado(self):
        return self.fecha_expiracion and timezone.now() > self.fecha_expiracion

TIPO_CUENTA_CHOICES = [
    ('personal', 'Personal'),
    ('profesional', 'Profesional'),
    ('empresarial', 'Empresarial'),
]

class Recordatorio(models.Model):
        usuario = models.ForeignKey(User, on_delete=models.CASCADE)
        titulo = models.CharField(max_length=200)
        descripcion = models.TextField()
        fecha_recordatorio = models.DateTimeField()

        def __str__(self):
            return self.titulo

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
    
