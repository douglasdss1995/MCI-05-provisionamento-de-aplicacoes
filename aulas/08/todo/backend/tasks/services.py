"""Services da aplicação de tarefas — lógica de negócio."""

import structlog

from tasks.exceptions import TaskNotFound
from tasks.models import Task
from tasks.selectors import get_task_by_id

logger = structlog.get_logger(__name__)


def create_task(title: str) -> Task:
    """Cria uma nova tarefa.

    Args:
        title: Descrição da tarefa.

    Returns:
        Instância da tarefa criada.
    """
    task = Task.objects.create(title=title)
    logger.info("task_created", task_id=task.pk, title=task.title)
    return task


def mark_task_done(task_id: int, done: bool) -> Task:
    """Atualiza o status de conclusão de uma tarefa.

    Args:
        task_id: ID da tarefa.
        done: True para marcar como concluída, False para desfazer.

    Returns:
        Instância da tarefa atualizada.

    Raises:
        TaskNotFound: Se a tarefa não existir.
    """
    try:
        task = get_task_by_id(task_id)
    except Task.DoesNotExist:
        raise TaskNotFound()

    task.done = done
    task.save(update_fields=["done"])

    logger.info("task_updated", task_id=task.pk, done=done)
    return task


def delete_task(task_id: int) -> None:
    """Remove uma tarefa do banco de dados.

    Args:
        task_id: ID da tarefa.

    Raises:
        TaskNotFound: Se a tarefa não existir.
    """
    try:
        task = get_task_by_id(task_id)
    except Task.DoesNotExist:
        raise TaskNotFound()

    logger.info("task_deleted", task_id=task.pk, title=task.title)
    task.delete()
