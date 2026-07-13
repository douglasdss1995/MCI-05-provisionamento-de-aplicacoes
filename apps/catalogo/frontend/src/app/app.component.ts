/**
 * Componente raiz da aplicação.
 *
 * Este é o primeiro componente carregado pelo Angular.
 * Ele define o layout base (cabeçalho + área de conteúdo)
 * e o <router-outlet> onde os outros componentes são renderizados.
 */

import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  template: `
    <!-- Cabeçalho fixo presente em todas as páginas -->
    <header>
      <h1>Catálogo de Filmes</h1>
    </header>

    <!-- O router-outlet renderiza o componente correspondente à URL atual -->
    <main class="container">
      <router-outlet />
    </main>
  `,
})
export class AppComponent {}
