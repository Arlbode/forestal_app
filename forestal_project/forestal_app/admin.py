from django.contrib import admin
from django.apps import apps
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

# Personalizar la vista de usuarios en el admin
class CustomUserAdmin(UserAdmin):
    # Campos a mostrar en la lista de usuarios
    list_display = ('username', 'first_name', 'last_name', 'email', 'date_joined')
    
    # Campos que pueden ser buscados
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    # Filtros para el panel de administración
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    
    # Campos que se pueden editar
    fieldsets = (
        (None, {'fields': ('username', 'password')}), 
        ('Información personal', {'fields': ('first_name', 'last_name', 'email')}), 
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser')}), 
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}), 
    )

# Desregistrar el modelo User antes de registrarlo con CustomUserAdmin
admin.site.unregister(User)

# Registrar el modelo User con la clase personalizada
admin.site.register(User, CustomUserAdmin)

# Obtener todos los modelos de la aplicación actual
app = apps.get_app_config('forestal_app')  # Reemplaza 'mi_aplicacion' con el nombre de tu aplicación

# Registrar todos los modelos en el panel de administración
for model in app.get_models():
    # Verificar si el modelo ya está registrado antes de registrarlo
    if not admin.site.is_registered(model):
        admin.site.register(model)
