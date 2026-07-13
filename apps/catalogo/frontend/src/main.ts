/**
 * Ponto de entrada da aplicação Angular.
 *
 * O bootstrapApplication inicializa o Angular com o componente raiz (AppComponent)
 * e a configuração definida em app.config.ts.
 */

import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { AppComponent } from './app/app.component';

bootstrapApplication(AppComponent, appConfig).catch((err) =>
  console.error('Erro ao inicializar a aplicação:', err)
);
