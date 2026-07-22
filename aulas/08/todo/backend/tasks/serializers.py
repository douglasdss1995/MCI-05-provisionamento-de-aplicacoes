"""Serializers da aplicação de tarefas."""

from rest_framework import serializers

from tasks.models import Task


class TaskSerializer(serializers.ModelSerializer):
    """Serializer completo da tarefa — usado para listagem e criação."""

    class Meta:
        model = Task
        fields = ["id", "title", "done", "created_at"]
        read_only_fields = ["id", "created_at"]


class TaskDoneSerializer(serializers.Serializer):
    """Serializer para marcar uma tarefa como concluída ou não concluída."""

    done = serializers.BooleanField()
