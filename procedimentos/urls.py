from django.urls import path
from . import views
from django.urls import path, include

app_name = 'procedimentos'

urlpatterns = [
    path('', views.buscar_procedimentos, name='buscar'),
    path('<int:procedimento_id>/', views.detalhe_procedimento, name='detalhe'),
    path('api/busca/', views.api_busca_rapida, name='api_busca'),
    path('home/', include('jobs.urls')),
    path('api/reportar-problema/', views.reportar_problema, name='reportar_problema'),
    

]