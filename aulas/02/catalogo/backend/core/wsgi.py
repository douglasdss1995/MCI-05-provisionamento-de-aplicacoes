"""
Ponto de entrada WSGI para servidores de produção.

O Gunicorn usa este arquivo para iniciar a aplicação Django.
WSGI (Web Server Gateway Interface) é o protocolo padrão entre
servidores web e aplicações Python.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

application = get_wsgi_application()
