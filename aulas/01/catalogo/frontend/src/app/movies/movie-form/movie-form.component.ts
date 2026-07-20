/**
 * Componente de formulário para cadastro de filmes.
 *
 * Este componente é filho do MovieListComponent.
 * Quando o filme é criado com sucesso, ele emite um evento
 * para o componente pai, que então atualiza a lista.
 *
 * A comunicação pai → filho é feita via @Input().
 * A comunicação filho → pai é feita via @Output() + EventEmitter.
 */

import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MovieService } from '../movie.service';
import { MovieFormData } from '../movie.model';

@Component({
  selector: 'app-movie-form',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './movie-form.component.html',
})
export class MovieFormComponent {
  // Evento emitido para o componente pai quando o filme é criado
  @Output() movieCreated = new EventEmitter<void>();

  // Dados do formulário vinculados com [(ngModel)]
  formData: MovieFormData = {
    title: '',
    genre: '',
    year: new Date().getFullYear(),
    rating: 5.0,
  };

  // Controla o estado de envio para desabilitar o botão
  isSubmitting: boolean = false;

  // Mensagem de erro exibida se a criação falhar
  errorMessage: string = '';

  constructor(private movieService: MovieService) {}

  /**
   * Envia o formulário para a API.
   * Chamado quando o usuário clica no botão "Cadastrar".
   */
  onSubmit(): void {
    this.isSubmitting = true;
    this.errorMessage = '';

    this.movieService.createMovie(this.formData).subscribe({
      next: () => {
        // Avisa o componente pai que o filme foi criado
        this.movieCreated.emit();
        // Limpa o formulário
        this.resetForm();
      },
      error: () => {
        this.errorMessage = 'Erro ao cadastrar o filme. Verifique os dados e tente novamente.';
        this.isSubmitting = false;
      },
    });
  }

  /** Restaura o formulário ao estado inicial. */
  private resetForm(): void {
    this.formData = {
      title: '',
      genre: '',
      year: new Date().getFullYear(),
      rating: 5.0,
    };
    this.isSubmitting = false;
  }
}
