"""
Configurações do Django para o projeto Catálogo de Filmes.

As variáveis sensíveis (senhas, chaves, hosts) são lidas do arquivo .env
via pydantic-settings. Nunca coloque valores reais diretamente neste arquivo.
"""

import logging
from pathlib import Path

import structlog
from pydantic_settings import BaseSettings, SettingsConfigDict

# Diretório raiz do projeto (onde está o manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Variáveis de ambiente
# Lidas do arquivo .env na raiz do backend.
# Se o arquivo não existir, o pydantic-settings tentará ler das variáveis
# de ambiente do sistema operacional.
# ---------------------------------------------------------------------------
class Env(BaseSettings):
    """Define e valida todas as variáveis de ambiente do projeto."""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",  # ignora variáveis extras no .env que não estão aqui
    )

    # Banco de dados PostgreSQL
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    # Django
    SECRET_KEY: str
    DEBUG: bool = False
    # Aceita uma string separada por vírgulas: "localhost,127.0.0.1"
    ALLOWED_HOSTS: str = "localhost,127.0.0.1"


# Instância global das configurações — usada abaixo e pode ser importada por outros módulos
env = Env()


# ---------------------------------------------------------------------------
# Configurações básicas do Django
# ---------------------------------------------------------------------------
SECRET_KEY = env.SECRET_KEY
DEBUG = env.DEBUG

# Converte a string "localhost,127.0.0.1" para lista ["localhost", "127.0.0.1"]
ALLOWED_HOSTS = [host.strip() for host in env.ALLOWED_HOSTS.split(",")]

# ---------------------------------------------------------------------------
# Aplicações instaladas
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Bibliotecas de terceiros
    "rest_framework",
    "django_filters",
    # Aplicações do projeto
    "movies",
]

# ---------------------------------------------------------------------------
# Middlewares
# ---------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

# ---------------------------------------------------------------------------
# Templates — necessário para o Django Admin
# ---------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# ---------------------------------------------------------------------------
# Banco de dados PostgreSQL
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env.POSTGRES_DB,
        "USER": env.POSTGRES_USER,
        "PASSWORD": env.POSTGRES_PASSWORD,
        "HOST": env.POSTGRES_HOST,
        "PORT": env.POSTGRES_PORT,
    }
}

# ---------------------------------------------------------------------------
# Validação de senhas
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# Internacionalização
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Arquivos estáticos
# O collectstatic copia todos os estáticos para STATIC_ROOT.
# O Nginx serve esse diretório em produção.
# ---------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    # Habilita o filtro por campos em todos os viewsets
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    # Retorna erros em JSON, não em HTML
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
}

# ---------------------------------------------------------------------------
# Logging com structlog
# Formato JSON em produção (DEBUG=False), texto legível em desenvolvimento (DEBUG=True)
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

structlog.configure(
    processors=[
        # Adiciona variáveis de contexto (útil para rastrear requisições)
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.ExceptionRenderer(),
        # Desenvolvimento: texto colorido; Produção: JSON para ferramentas de log
        structlog.dev.ConsoleRenderer() if DEBUG else structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)
