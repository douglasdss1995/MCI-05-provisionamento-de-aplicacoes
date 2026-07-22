/**
 * Configuração central da aplicação Angular.
 *
 * Aqui registramos os providers globais:
 * - provideHttpClient: habilita o serviço HTTP para chamadas à API
 * - provideRouter: habilita o roteamento com rotas definidas em app.routes.ts
 */

import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideHttpClient } from '@angular/common/http';
import { provideRouter } from '@angular/router';
import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    // Otimização de detecção de mudanças — recomendado pelo Angular 18
    provideZoneChangeDetection({ eventCoalescing: true }),
    // Habilita chamadas HTTP para a API do backend
    provideHttpClient(),
    // Habilita o sistema de rotas
    provideRouter(routes),
  ],
};
