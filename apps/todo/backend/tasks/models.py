"""
Model da Lista de Tarefas.

Este é o modelo que os alunos vão provisionar durante os exercícios E1 a E8.
"""

from django.db import models


class Task(models.Model):
    """Representa uma tarefa na lista de afazeres.

    Attributes:
        title: Descrição da tarefa.
        done: Indica se a tarefa foi concluída.
        created_at: Data e hora de criação, preenchida automaticamente.
    """

    title = models.CharField(max_length=200, verbose_name="Tarefa")
    done = models.BooleanField(default=False, verbose_name="Concluída")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criada em")

    class Meta:
        db_table = "tasks"
        ordering = ["-created_at"]
        verbose_name = "Tarefa"
        verbose_name_plural = "Tarefas"

    def __str__(self) -> str:
        status = "✓" if self.done else "○"
        return f"{status} {self.title}"
