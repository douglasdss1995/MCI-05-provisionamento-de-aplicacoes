# Aula Extra — Publicando com SSL (Certificado Local Autoassinado)

> **Conteúdo bônus, fora da grade avaliada.** A Aula 06 montou o gateway Nginx da stack, mas ficou só em HTTP (`listen 80`) — nunca chegou a configurar HTTPS de verdade, apesar do nome da aula mencionar isso. Esta aula fecha essa lacuna, adicionando um certificado autoassinado, útil para desenvolvimento local. Parte do estado da Lista de Tarefas ao final da Aula 08 (`aulas/08/todo/`).

## Antes de começar

Confirme que a stack sobe normalmente:

```bash
docker compose up -d
```

Acesse `http://localhost/` e confirme que a aplicação responde antes de mexer em HTTPS.

---

## Parte 1 — Por que HTTPS também em Ambiente Local

Em produção, HTTPS é obrigatório. Mas existem boas razões para querer HTTPS **já no ambiente local de desenvolvimento**:

- Cookies marcados como `Secure` (comuns em autenticação) só são enviados pelo navegador em conexões HTTPS — sem HTTPS local, esse comportamento não pode ser testado antes de ir para produção.
- Service Workers e várias APIs modernas do navegador (geolocalização, clipboard, notificações) só funcionam em um "contexto seguro" (HTTPS ou `localhost` puro, sem passar por um proxy).
- Testar localmente com HTTPS evita surpresas de comportamento que só aparecem em produção.

Um certificado **autoassinado** (self-signed) resolve isso para desenvolvimento: você mesmo gera o certificado, sem depender de nenhuma autoridade externa. A desvantagem é que nenhum navegador confia nele por padrão — você vai ver um aviso de "conexão não segura" ao acessar, mesmo com tudo configurado corretamente. Para um domínio público de verdade, veja a aula seguinte (`aula-extra-ssl-lets-encrypt.md`).

---

## Parte 2 — Gerando o Certificado

Crie a pasta onde os certificados vão morar:

```bash
mkdir -p nginx/certs
```

**Nunca versione o certificado nem a chave privada.** Adicione a pasta ao `.gitignore`:

```
# .gitignore
nginx/certs/
```

Gere um certificado autoassinado válido por 1 ano, para `localhost`:

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/certs/localhost.key \
  -out nginx/certs/localhost.crt \
  -subj "/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
```

- `-x509`: gera direto um certificado autoassinado, sem passar por um pedido de assinatura (CSR) separado.
- `-nodes`: não criptografa a chave privada com senha (mais simples para uso local; nunca faça isso em produção).
- `-newkey rsa:2048`: gera também uma chave privada RSA de 2048 bits.
- `-subj "/CN=localhost"`: define o *Common Name* do certificado como `localhost`.
- `-addext "subjectAltName=..."`: adiciona o **SAN (Subject Alternative Name)**. Isso não é opcional — navegadores modernos (Chrome, Firefox) rejeitam um certificado que só tem `CN` e não tem SAN, mostrando um erro de "certificado inválido" mesmo antes do aviso normal de "autoassinado".

O comando gera dois arquivos: `nginx/certs/localhost.crt` (o certificado, público) e `nginx/certs/localhost.key` (a chave privada, nunca deve sair da sua máquina).

---

## Parte 3 — Montando os Certificados no Container do Gateway

Atualize o `docker-compose.yml`, no serviço `nginx`, adicionando o volume dos certificados e a porta 443:

```yaml
  nginx:
    image: nginx:alpine
    depends_on:
      - backend
      - frontend
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf
      - ./nginx/certs:/etc/nginx/certs:ro
      - static_volume:/app/staticfiles
```

O volume dos certificados é montado como somente leitura (`:ro`) — o container nunca precisa escrever nele.

---

## Parte 4 — Adicionando o Bloco HTTPS ao `nginx/nginx.conf`

Atualize o arquivo `nginx/nginx.conf`, adicionando um segundo `server`, escutando na porta 443, com as mesmas rotas do gateway original:

```nginx
# nginx/nginx.conf
# Gateway unico da aplicacao: roteia para o frontend e para a API do backend

upstream backend_upstream {
    server backend:8000;
}

server {
    listen 443 ssl;

    ssl_certificate /etc/nginx/certs/localhost.crt;
    ssl_certificate_key /etc/nginx/certs/localhost.key;

    # Arquivos estaticos do Django (admin, bibliotecas)
    location /static/ {
        alias /app/staticfiles/;
    }

    # Todas as chamadas de API vao para o backend Django
    location /api/ {
        proxy_pass http://backend_upstream/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # O Django Admin tambem precisa ser encaminhado ao backend
    location /admin/ {
        proxy_pass http://backend_upstream/admin/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Tudo o mais vai para o frontend Angular
    location / {
        proxy_pass http://frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Repare que este bloco `server` é praticamente idêntico ao original em `listen 80` (mesmas `location`) — a única diferença de fato são as duas linhas `ssl_certificate`/`ssl_certificate_key` e o `listen 443 ssl` no lugar de `listen 80`. Ainda falta o bloco original de `listen 80` no arquivo — ele vai ser reaproveitado na próxima parte, mas com uma finalidade diferente.

---

## Parte 5 — Redirecionando HTTP para HTTPS

Agora que a porta 443 está funcionando de verdade, o bloco `listen 80` original deixa de servir a aplicação diretamente — sua única função passa a ser redirecionar qualquer requisição HTTP para a versão HTTPS. Adicione este bloco **antes** do `server { listen 443 ssl; ... }` da Parte 4:

```nginx
server {
    listen 80;
    return 301 https://$host$request_uri;
}
```

O arquivo final tem, nesta ordem: o `upstream`, o `server { listen 80; }` (só redirecionamento) e o `server { listen 443 ssl; }` (com todas as `location` da aplicação).

---

## Parte 6 — Subindo e Testando

```bash
docker compose down
docker compose up -d --build
```

Acesse:

```
https://localhost/
```

O navegador vai mostrar um aviso de conexão não segura ("Sua conexão não é particular", "NET::ERR_CERT_AUTHORITY_INVALID" ou similar) — **isso é esperado**: é exatamente o comportamento que um certificado autoassinado tem, porque nenhuma autoridade certificadora confiável o assinou. Para desenvolvimento local, prossiga mesmo assim ("Avançado" → "Prosseguir para localhost").

Confirme também que o redirecionamento funciona, acessando via HTTP:

```
http://localhost/
```

Você deve acabar em `https://localhost/` automaticamente.

---

## Parte 7 — Indo Além (Opcional)

Se o aviso do navegador incomodar durante o desenvolvimento do dia a dia, existe uma ferramenta chamada [`mkcert`](https://github.com/FiloSottile/mkcert) que gera certificados locais e os registra automaticamente como confiáveis no sistema operacional — o resultado é um HTTPS local sem nenhum aviso. Ela não substitui o entendimento de como o `openssl` e o Nginx lidam com certificados (por isso não é o caminho principal desta aula), mas vale conhecer como atalho de produtividade.

---

## Checklist final

- [ ] Pasta `nginx/certs/` criada e adicionada ao `.gitignore`
- [ ] Certificado gerado com `openssl`, incluindo `subjectAltName` (SAN)
- [ ] `docker-compose.yml` publicando a porta `443` e montando `nginx/certs` no serviço `nginx`
- [ ] `nginx/nginx.conf` com um `server { listen 443 ssl; ... }` completo
- [ ] `server { listen 80; }` reduzido a um redirecionamento (`return 301 https://...`)
- [ ] `https://localhost/` acessível (mesmo com o aviso de certificado não confiável)
- [ ] `http://localhost/` redireciona para `https://localhost/`

---

## Material de apoio

- OpenSSL — comando `req`: https://docs.openssl.org/master/man1/openssl-req/
- Nginx — módulo `ngx_http_ssl_module`: https://nginx.org/en/docs/http/ngx_http_ssl_module.html
- Mozilla SSL Configuration Generator: https://ssl-config.mozilla.org/
- mkcert — certificados locais confiáveis: https://github.com/FiloSottile/mkcert
