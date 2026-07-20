/**
 * Componente de listagem de tarefas.
 * Exibe todas as tarefas, permite marcar como concluída e remover.
 */

import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Task } from '../task.model';
import { TaskService } from '../task.service';
import { TaskFormComponent } from '../task-form/task-form.component';

@Component({
  selector: 'app-task-list',
  standalone: true,
  imports: [CommonModule, TaskFormComponent],
  templateUrl: './task-list.component.html',
})
export class TaskListComponent implements OnInit {
  tasks: Task[] = [];
  errorMessage: string = '';

  constructor(private taskService: TaskService) {}

  ngOnInit(): void {
    this.loadTasks();
  }

  loadTasks(): void {
    this.errorMessage = '';
    this.taskService.getTasks().subscribe({
      next: (tasks) => (this.tasks = tasks),
      error: () => {
        this.errorMessage = 'Erro ao carregar tarefas. Verifique se o servidor está rodando.';
      },
    });
  }

  toggleDone(task: Task): void {
    this.taskService.toggleDone(task.id, !task.done).subscribe({
      next: (updated) => {
        // Atualiza apenas a tarefa alterada na lista local
        this.tasks = this.tasks.map((t) => (t.id === updated.id ? updated : t));
      },
      error: () => {
        this.errorMessage = 'Erro ao atualizar a tarefa.';
      },
    });
  }

  deleteTask(task: Task): void {
    if (!confirm(`Remover "${task.title}"?`)) return;

    this.taskService.deleteTask(task.id).subscribe({
      next: () => {
        this.tasks = this.tasks.filter((t) => t.id !== task.id);
      },
      error: () => {
        this.errorMessage = 'Erro ao remover a tarefa.';
      },
    });
  }

  onTaskCreated(): void {
    this.loadTasks();
  }
}
