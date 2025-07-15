from django.contrib import admin
from django.urls import path, include



urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', include('jobs.urls')),
    path('', include('usuarios.urls')),
    path('procedimentos/', include('procedimentos.urls', namespace='procedimentos')),
    
]

