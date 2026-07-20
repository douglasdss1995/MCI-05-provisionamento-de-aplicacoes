"""
Roteamento de URLs da aplicação de tarefas.

GET    /api/tasks/            → lista tarefas
POST   /api/tasks/            → cria tarefa
DELETE /api/tasks/<id>/       → remove tarefa
PATCH  /api/tasks/<id>/done/  → marca/desmarca como concluída
"""

from django.urls import path
from tasks.views import TaskDetailView, TaskDoneView, TaskListView

urlpatterns = [
    path("tasks/", TaskListView.as_view(), name="task-list"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path("tasks/<int:pk>/done/", TaskDoneView.as_view(), name="task-done"),
]
