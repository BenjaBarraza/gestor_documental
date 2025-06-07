from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.redireccion_dashboard, name='dashboard'),
    path('personal/', views.vista_personal, name='vista_personal'),
    path('profesional/', views.vista_profesional, name='vista_profesional'),
    path('empresarial/', views.vista_empresarial, name='vista_empresarial'),
]
