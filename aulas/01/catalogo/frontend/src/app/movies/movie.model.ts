/**
 * Interface que define o formato de um filme na aplicação Angular.
 *
 * A interface garante que qualquer objeto do tipo Movie tenha
 * exatamente estes campos com estes tipos. O TypeScript avisa
 * se você tentar usar um campo que não existe ou com tipo errado.
 *
 * Estes campos devem corresponder ao que a API do backend retorna.
 */

export interface Movie {
  id: number;
  title: string;
  genre: string;
  year: number;
  rating: string; // string porque vem como "8.8" do DRF (DecimalField)
  created_at: string;
}

/**
 * Interface para os dados do formulário de criação de filme.
 * Não tem `id` nem `created_at` — esses são gerados pelo backend.
 */
export interface MovieFormData {
  title: string;
  genre: string;
  year: number;
  rating: number;
}
