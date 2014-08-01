import django

from .menu import Menu, MenuItem
from .discover import autodiscover

__version__ = '1.1.0'
__url__ = 'https://github.com/fatbox/django-simple-menu'
__all__ = ['Menu', 'MenuItem']

default_app_config = 'menu.apps.MenuConfig'
if django.VERSION < (1, 7):
    autodiscover()
