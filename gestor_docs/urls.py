from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from documentos.views import home



urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios.urls', namespace='usuarios')),
    path('documentos/', include('documentos.urls', namespace='documentos')),
    path('publico/', include('publico.urls', namespace='publico')),
    path('emails/', include('emails.urls', namespace='emails')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('tutoriales/', include('tutoriales.urls', namespace='tutoriales')),
    path('recordatorios/', include('recordatorios.urls', namespace='recordatorios')),

    # 🆕 Esta es la raíz
    path('', home, name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


