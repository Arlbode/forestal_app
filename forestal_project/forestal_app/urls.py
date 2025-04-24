from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Autenticación y Dashboard
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('login/',    views.login_view,    name='login'),
    path('logout/',   views.logout_view,   name='logout'),

    # CRUD de Posturas
    path('posturas/',                 views.listar_posturas,   name='listar_posturas'),
    path('posturas/<int:id>/',        views.detalle_postura,   name='detalle_postura'),
    # Cambiado a "editar/" para URLs más RESTful
    path('posturas/<int:id>/editar/', views.editar_postura,    name='editar_postura'),
    path('registrar-postura/',        views.registro_postura,  name='registro_postura'),

    # Especies
    path('registrar-especie/',        views.registrar_especie, name='registrar_especie'),

    # Mapa
    path('mapa-posturas/',            views.mapa_posturas,     name='mapa_posturas'),

    # Escaneo QR
    path('escanear/',                 views.escanear_postura_view, name='escanear_postura'),
    path('registrar-escaneo/',        views.registrar_escaneo,      name='registrar_escaneo'),

    # API interna para traer datos de la postura tras el escaneo
    path('api/postura/<int:postura_id>/', views.api_postura_info, name='api_postura_info'),

    #Exporar a PDF
    path('posturas/exportar-pdf/', views.exportar_posturas_pdf, name='exportar_posturas_pdf'),
]

# Para servir los archivos multimedia (QR, etc.) en desarrollo
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
