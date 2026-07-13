/**
 * Serviço de comunicação com a API de tarefas.
 * Centraliza todas as chamadas HTTP — os componentes não chamam a API diretamente.
 */

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Task, TaskFormData } from './task.model';

const API_URL = '/api/tasks/';

@Injectable({ providedIn: 'root' })
export class TaskService {
  constructor(private http: HttpClient) {}

  /** Busca todas as tarefas. */
  getTasks(): Observable<Task[]> {
    return this.http.get<Task[]>(API_URL);
  }

  /** Cria uma nova tarefa. */
  createTask(data: TaskFormData): Observable<Task> {
    return this.http.post<Task>(API_URL, data);
  }

  /**
   * Marca ou desmarca uma tarefa como concluída.
   *
   * @param id - ID da tarefa
   * @param done - true = concluída, false = pendente
   */
  toggleDone(id: number, done: boolean): Observable<Task> {
    return this.http.patch<Task>(`${API_URL}${id}/done/`, { done });
  }

  /** Remove uma tarefa. */
  deleteTask(id: number): Observable<void> {
    return this.http.delete<void>(`${API_URL}${id}/`);
  }
}
