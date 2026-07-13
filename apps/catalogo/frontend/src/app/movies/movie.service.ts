/**
 * Serviço de comunicação com a API de filmes.
 *
 * O serviço centraliza todas as chamadas HTTP para o backend.
 * Os componentes não devem fazer chamadas HTTP diretamente —
 * eles chamam o serviço e recebem os dados prontos.
 *
 * Por que usar um serviço?
 * - A URL da API fica em um único lugar (fácil de mudar)
 * - O código de comunicação não se mistura com o código de tela
 * - Todos os componentes compartilham a mesma instância do serviço
 */

import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Movie, MovieFormData } from './movie.model';

// URL base da API — em produção, o Nginx redireciona /api/ para o backend
const API_URL = '/api/movies/';

@Injectable({
  // providedIn: 'root' significa que há uma única instância deste serviço
  // compartilhada por toda a aplicação (singleton)
  providedIn: 'root',
})
export class MovieService {
  constructor(private http: HttpClient) {}

  /**
   * Busca todos os filmes, com filtro opcional por gênero.
   *
   * @param genre - Se informado, filtra os filmes por este gênero
   * @returns Observable com a lista de filmes
   */
  getMovies(genre?: string): Observable<Movie[]> {
    // Monta os parâmetros de query string apenas se o gênero foi informado
    let params = new HttpParams();
    if (genre) {
      params = params.set('genre', genre);
    }
    return this.http.get<Movie[]>(API_URL, { params });
  }

  /**
   * Cria um novo filme no catálogo.
   *
   * @param data - Dados do filme a ser criado
   * @returns Observable com o filme criado (incluindo o ID gerado pelo backend)
   */
  createMovie(data: MovieFormData): Observable<Movie> {
    return this.http.post<Movie>(API_URL, data);
  }

  /**
   * Atualiza apenas a nota de um filme existente.
   *
   * @param id - ID do filme
   * @param rating - Nova nota (0.0 a 10.0)
   * @returns Observable com o filme atualizado
   */
  updateRating(id: number, rating: number): Observable<Movie> {
    return this.http.patch<Movie>(`${API_URL}${id}/rating/`, { rating });
  }

  /**
   * Remove um filme do catálogo.
   *
   * @param id - ID do filme a ser removido
   * @returns Observable vazio (o backend retorna 204 sem corpo)
   */
  deleteMovie(id: number): Observable<void> {
    return this.http.delete<void>(`${API_URL}${id}/`);
  }
}
