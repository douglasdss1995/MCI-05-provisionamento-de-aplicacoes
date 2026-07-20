"""Testes de integração da API de tarefas."""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from tasks.models import Task


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def created_task() -> Task:
    return Task.objects.create(title="Estudar Docker")


@pytest.mark.django_db
class TestTaskList:
    """Testes do endpoint GET/POST /api/tasks/"""

    def test_list_empty(self, api_client: APIClient) -> None:
        response = api_client.get(reverse("task-list"))
        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

    def test_list_returns_tasks(self, api_client: APIClient, created_task: Task) -> None:
        response = api_client.get(reverse("task-list"))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_create_task_returns_201(self, api_client: APIClient) -> None:
        response = api_client.post(
            reverse("task-list"), {"title": "Aprender Docker"}, format="json"
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["done"] is False

    def test_create_task_without_title_returns_400(self, api_client: APIClient) -> None:
        response = api_client.post(reverse("task-list"), {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestTaskDone:
    """Testes do endpoint PATCH /api/tasks/<id>/done/"""

    def test_mark_task_as_done(self, api_client: APIClient, created_task: Task) -> None:
        url = reverse("task-done", kwargs={"pk": created_task.pk})
        response = api_client.patch(url, {"done": True}, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["done"] is True

    def test_unmark_task_as_done(self, api_client: APIClient) -> None:
        task = Task.objects.create(title="Tarefa concluída", done=True)
        url = reverse("task-done", kwargs={"pk": task.pk})
        response = api_client.patch(url, {"done": False}, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["done"] is False

    def test_mark_nonexistent_task_returns_404(self, api_client: APIClient) -> None:
        url = reverse("task-done", kwargs={"pk": 99999})
        response = api_client.patch(url, {"done": True}, format="json")
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestTaskDelete:
    """Testes do endpoint DELETE /api/tasks/<id>/"""

    def test_delete_task_returns_204(
        self, api_client: APIClient, created_task: Task
    ) -> None:
        url = reverse("task-detail", kwargs={"pk": created_task.pk})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Task.objects.count() == 0

    def test_delete_nonexistent_task_returns_404(self, api_client: APIClient) -> None:
        url = reverse("task-detail", kwargs={"pk": 99999})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
