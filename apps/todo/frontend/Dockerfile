# Dockerfile multi-stage do frontend Angular - Lista de Tarefas

# Estagio 1: compila a aplicacao Angular
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# Estagio 2: imagem final, apenas com Nginx servindo os arquivos compilados
FROM nginx:alpine AS runner

# Ajuste o caminho abaixo conforme o outputPath do seu angular.json
# (o projeto do curso usa "todo-frontend" como nome do projeto Angular)
COPY --from=builder /app/dist/todo-frontend/browser /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]