"""Configuração do Django Admin para o modelo Task."""

from django.contrib import admin

from tasks.models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Configuração da tela de tarefas no Admin."""

    list_display = ["title", "done", "created_at"]
    list_filter = ["done"]
    search_fields = ["title"]
    ordering = ["-created_at"]
