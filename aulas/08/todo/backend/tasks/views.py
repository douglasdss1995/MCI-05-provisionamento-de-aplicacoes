"""Views da aplicação de tarefas — orquestradores finos."""

import structlog
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from tasks.selectors import get_all_tasks
from tasks.serializers import TaskDoneSerializer, TaskSerializer
from tasks.services import create_task, delete_task, mark_task_done

logger = structlog.get_logger(__name__)


class TaskListView(APIView):
    """Listagem e criação de tarefas.

    GET  /api/tasks/ → lista todas as tarefas
    POST /api/tasks/ → cria uma nova tarefa
    """

    def get(self, request: Request) -> Response:
        """Lista todas as tarefas."""
        tasks = get_all_tasks()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        """Cria uma nova tarefa."""
        serializer = TaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task = create_task(title=serializer.validated_data["title"])
        return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)


class TaskDetailView(APIView):
    """Operações sobre uma tarefa específica.

    DELETE /api/tasks/<id>/ → remove a tarefa
    """

    def delete(self, request: Request, pk: int) -> Response:
        """Remove uma tarefa."""
        delete_task(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskDoneView(APIView):
    """Atualização do status de conclusão de uma tarefa.

    PATCH /api/tasks/<id>/done/ → marca ou desmarca como concluída
    """

    def patch(self, request: Request, pk: int) -> Response:
        """Atualiza o campo 'done' de uma tarefa."""
        serializer = TaskDoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task = mark_task_done(pk, serializer.validated_data["done"])
        return Response(TaskSerializer(task).data)
