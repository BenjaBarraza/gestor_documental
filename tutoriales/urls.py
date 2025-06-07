from django.urls import path
from . import views

app_name = 'tutoriales'

urlpatterns = [
    path('tutorial/', views.tutorial_view, name='tutorial'),
    path('explorar-funciones/', views.explorar_funciones_view, name='explorar_funciones'),
    path('ayuda/', views.ayuda_view, name='ayuda'),
]
