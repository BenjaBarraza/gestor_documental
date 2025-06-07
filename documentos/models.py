from django.db import models
from django.contrib.auth.models import User
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
    size = models.PositiveIntegerField(blank=True, null=True)  # tamaño en KB
    is_shared = models.BooleanField(default=False)             # si el documento fue compartido



    def save(self, *args, **kwargs):
        if self.archivo and not self.size:
            self.size = self.archivo.size // 1024  # Guarda en KB
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

    def generar_enlace_publico(self, duracion_horas=24):
        self.enlace_publico = uuid.uuid4().hex
        self.expiracion_enlace = timezone.now() + timedelta(hours=duracion_horas)
        self.is_shared = True
        self.save()

    def enlace_expirado(self):
        return self.fecha_expiracion and timezone.now() > self.fecha_expiracion


