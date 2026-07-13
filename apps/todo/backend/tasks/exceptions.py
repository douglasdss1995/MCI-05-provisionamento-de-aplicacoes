"""Exceções customizadas da aplicação de tarefas."""

from rest_framework import status
from rest_framework.exceptions import APIException


class TaskNotFound(APIException):
    """Lançada quando uma tarefa com o ID solicitado não existe."""

    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Tarefa não encontrada."
    default_code = "task_not_found"
