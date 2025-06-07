from django.db import models
from django.contrib.auth.models import User

class Recordatorio(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_recordatorio = models.DateTimeField()

    def __str__(self):
        return self.titulo
