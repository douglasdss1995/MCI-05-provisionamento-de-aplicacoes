import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  template: `
    <header>
      <h1>Lista de Tarefas</h1>
    </header>
    <main class="container">
      <router-outlet />
    </main>
  `,
})
export class AppComponent {}
