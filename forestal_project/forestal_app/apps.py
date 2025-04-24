from django.apps import AppConfig

class ForestalAppConfig(AppConfig):
    name = 'forestal_app'

    def ready(self):
        import forestal_app.signals  # Importa las señales al iniciar
