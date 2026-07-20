"""Selectors da aplicação de tarefas — encapsula as queries ao banco."""

from django.db.models import QuerySet
from tasks.models import Task


def get_all_tasks() -> QuerySet[Task]:
    """Retorna todas as tarefas, ordenadas da mais recente para a mais antiga."""
    return Task.objects.all()


def get_task_by_id(task_id: int) -> Task:
    """Busca uma tarefa pelo ID.

    Args:
        task_id: ID da tarefa.

    Returns:
        Instância da tarefa encontrada.

    Raises:
        Task.DoesNotExist: Se nenhuma tarefa com este ID existir.
    """
    return Task.objects.get(pk=task_id)
