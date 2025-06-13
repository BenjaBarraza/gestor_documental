from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import perfil_usuario
from .views import RegisterView

# api/urls.py
urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('register/', RegisterView.as_view(), name='register'),

    # Perfil del usuario
    path('perfil/', perfil_usuario, name='perfil_usuario'),
]
