/**
 * Componente de listagem de filmes.
 *
 * Este componente é responsável por:
 * - Carregar a lista de filmes do backend ao inicializar
 * - Exibir os filmes em cards
 * - Permitir filtro por gênero
 * - Exibir o formulário de cadastro
 * - Remover filmes da lista
 */

import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Movie } from '../movie.model';
import { MovieService } from '../movie.service';
import { MovieFormComponent } from '../movie-form/movie-form.component';

@Component({
  selector: 'app-movie-list',
  standalone: true,
  // Importações necessárias para este componente funcionar:
  // - CommonModule: diretivas *ngIf, *ngFor, etc.
  // - FormsModule: ligação bidirecional com [(ngModel)]
  // - MovieFormComponent: formulário de cadastro
  imports: [CommonModule, FormsModule, MovieFormComponent],
  templateUrl: './movie-list.component.html',
})
export class MovieListComponent implements OnInit {
  // Lista de filmes retornada pela API
  movies: Movie[] = [];

  // Texto digitado no campo de filtro
  genreFilter: string = '';

  // Controla se o formulário de cadastro está visível
  showForm: boolean = false;

  // Mensagem de erro caso a chamada à API falhe
  errorMessage: string = '';

  constructor(private movieService: MovieService) {}

  // ngOnInit é chamado automaticamente pelo Angular quando o componente é criado
  ngOnInit(): void {
    this.loadMovies();
  }

  /**
   * Carrega a lista de filmes do backend.
   * Aplica o filtro de gênero se o campo estiver preenchido.
   */
  loadMovies(): void {
    this.errorMessage = '';
    const genre = this.genreFilter.trim() || undefined;

    this.movieService.getMovies(genre).subscribe({
      next: (movies) => {
        this.movies = movies;
      },
      error: () => {
        this.errorMessage = 'Erro ao carregar filmes. Verifique se o servidor está rodando.';
      },
    });
  }

  /**
   * Remove um filme da lista após confirmação do usuário.
   *
   * @param movie - Filme a ser removido
   */
  deleteMovie(movie: Movie): void {
    if (!confirm(`Remover "${movie.title}" do catálogo?`)) {
      return;
    }

    this.movieService.deleteMovie(movie.id).subscribe({
      next: () => {
        // Remove o filme da lista local sem precisar recarregar tudo da API
        this.movies = this.movies.filter((m) => m.id !== movie.id);
      },
      error: () => {
        this.errorMessage = 'Erro ao remover o filme.';
      },
    });
  }

  /**
   * Chamado pelo formulário quando um novo filme é criado com sucesso.
   * Recarrega a lista para exibir o novo filme.
   */
  onMovieCreated(): void {
    this.showForm = false;
    this.loadMovies();
  }
}
