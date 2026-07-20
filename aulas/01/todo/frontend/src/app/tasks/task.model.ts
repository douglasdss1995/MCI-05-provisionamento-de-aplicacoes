/**
 * Interface que define o formato de uma tarefa na aplicação Angular.
 * Os campos devem corresponder ao que a API do backend retorna.
 */

export interface Task {
  id: number;
  title: string;
  done: boolean;
  created_at: string;
}

/** Dados necessários para criar uma nova tarefa. */
export interface TaskFormData {
  title: string;
}
