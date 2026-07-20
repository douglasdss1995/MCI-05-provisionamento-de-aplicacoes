/**
 * Ponto de entrada da aplicação Angular — Lista de Tarefas.
 */

import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { AppComponent } from './app/app.component';

bootstrapApplication(AppComponent, appConfig).catch((err) =>
  console.error('Erro ao inicializar a aplicação:', err)
);
