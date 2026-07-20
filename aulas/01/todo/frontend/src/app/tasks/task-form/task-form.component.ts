/**
 * Formulário de criação de tarefa.
 * Emite o evento taskCreated quando uma tarefa é cadastrada com sucesso.
 */

import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TaskService } from '../task.service';

@Component({
  selector: 'app-task-form',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './task-form.component.html',
})
export class TaskFormComponent {
  @Output() taskCreated = new EventEmitter<void>();

  title: string = '';
  isSubmitting: boolean = false;
  errorMessage: string = '';

  constructor(private taskService: TaskService) {}

  onSubmit(): void {
    if (!this.title.trim()) return;

    this.isSubmitting = true;
    this.errorMessage = '';

    this.taskService.createTask({ title: this.title.trim() }).subscribe({
      next: () => {
        this.taskCreated.emit();
        this.title = '';
        this.isSubmitting = false;
      },
      error: () => {
        this.errorMessage = 'Erro ao criar a tarefa.';
        this.isSubmitting = false;
      },
    });
  }
}
