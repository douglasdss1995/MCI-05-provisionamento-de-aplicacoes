/**
 * Definição das rotas da aplicação.
 *
 * Cada rota mapeia um caminho da URL para um componente.
 * O Angular carrega o componente correto sem recarregar a página
 * (isso se chama Single Page Application — SPA).
 */

import { Routes } from '@angular/router';
import { MovieListComponent } from './movies/movie-list/movie-list.component';

export const routes: Routes = [
  // Rota padrão: redireciona a raiz "/" para a listagem de filmes
  { path: '', redirectTo: 'movies', pathMatch: 'full' },

  // Listagem de filmes
  { path: 'movies', component: MovieListComponent },

  // Rota curinga: qualquer URL desconhecida redireciona para a listagem
  { path: '**', redirectTo: 'movies' },
];
