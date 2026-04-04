from django.apps import AppConfig


class ShgConfig(AppConfig):
    name = 'shg'

    def ready(self):
        import shg.signals
        return super().ready()
