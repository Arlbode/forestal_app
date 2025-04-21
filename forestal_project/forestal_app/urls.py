from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('registro/', views.registro_postura, name='registro_postura'),
    path('mapa/', views.ver_mapa, name='ver_mapa'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register_user/', views.register_view, name='register'),
    path('registro_especie', views.registrar_especie, name='registro_especie'),
    path('posturas/', views.listar_posturas, name='listar_posturas'),
]