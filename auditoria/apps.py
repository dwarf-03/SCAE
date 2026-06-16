from django.apps import AppConfig


class AuditoriaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auditoria'

    def ready(self):
        # Conecta los signals al iniciar la app
        import auditoria.signals