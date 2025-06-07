from django.urls import path
from . import views

app_name = 'recordatorios'

urlpatterns = [
    path('crear/', views.crear_recordatorio, name='crear_recordatorio'),
    path('eliminar/<int:recordatorio_id>/', views.eliminar_recordatorio, name='eliminar_recordatorio'),
]
