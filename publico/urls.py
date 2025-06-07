from django.urls import path
from . import views

app_name = 'publico'

urlpatterns = [
    path('<uuid:enlace>/', views.documento_publico, name='documento_publico'),
]
