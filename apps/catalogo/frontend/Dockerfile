FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine AS runner

# Remove a configuracao padrao do Nginx (nao tem fallback de SPA)
RUN rm /etc/nginx/conf.d/default.conf

# Config minima so com try_files — o roteamento de /api/, /admin/ e /static/
# agora e responsabilidade do Nginx da stack (nginx/nginx.conf), nao deste
COPY nginx-spa.conf /etc/nginx/conf.d/default.conf

COPY --from=builder /app/dist/catalogo-frontend/browser /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
