from django.urls import path
from . import views

app_name = 'emails'

urlpatterns = [
    path('prueba-email/', views.prueba_email, name='prueba_email'),
]
