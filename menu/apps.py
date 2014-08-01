from django.apps import AppConfig


class MenuConfig(AppConfig):
    name = 'menu'

    def ready(self):
        from .discover import autodiscover
        autodiscover()
