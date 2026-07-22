# Aula Extra — Publicando com SSL (Let's Encrypt)

> **Conteúdo bônus, fora da grade avaliada.** Continuação de `aula-extra-ssl-certificado-local.md`. Lá o certificado era autoassinado, útil só para desenvolvimento local. Aqui o objetivo é emitir um certificado assinado por uma autoridade certificadora pública e reconhecida — o [Let's Encrypt](https://letsencrypt.org/) — para publicar a aplicação de verdade, sem aviso de segurança no navegador de ninguém.

> **Atenção — pré-requisitos que esta aula pressupõe:** diferente do resto do curso, isto não roda dentro do WSL2 local. Você precisa de:
> - Um **domínio próprio** (comprado em um registrador, ex.: registro.br, Namecheap, GoDaddy).
> - Um **servidor com IP público** (uma VPS, por exemplo) rodando a stack da aplicação — a mesma imagem publicada em `ghcr.io` na Aula 07 pode ser usada aqui.
> - Um **registro DNS do tipo A** apontando esse domínio para o IP público do servidor.
> - As **portas 80 e 443 abertas** nesse servidor, acessíveis pela internet.
>
> Ao longo desta aula, `SEU-DOMINIO.com` e `SEU-SERVIDOR` são placeholders — substitua pelos valores reais do seu domínio e servidor, do mesmo jeito que `SEU-USUARIO` foi usado na Aula 07 para o GitHub.

## Antes de começar

Confirme que a stack está publicada e acessível em `http://SEU-DOMINIO.com/` (sem HTTPS ainda) antes de prosseguir — se a aplicação não responde nem por HTTP, o desafio do Let's Encrypt (Parte 1) também não vai funcionar, porque ele depende da porta 80 estar acessível pela internet.

---

## Parte 1 — Como Funciona o Let's Encrypt (ACME)

O [Let's Encrypt](https://letsencrypt.org/) é uma autoridade certificadora (CA) gratuita, automatizada e reconhecida por todos os navegadores modernos. Para provar que você realmente controla `SEU-DOMINIO.com` (e não está pedindo um certificado para um domínio de outra pessoa), ele usa o protocolo **ACME**: o cliente (neste caso, o **Certbot**) recebe um desafio, publica um arquivo específico em um caminho combinado do seu servidor, e o Let's Encrypt verifica esse arquivo acessando seu domínio pela porta 80. Esse método é chamado de **desafio HTTP (webroot)**.

Um detalhe importante: **certificados do Let's Encrypt são válidos por apenas 90 dias**. Isso é proposital (incentiva automação e reduz o risco de um certificado vazado continuar válido por anos) — por isso a Parte 7 desta aula automatiza a renovação.

---

## Parte 2 — Preparando o Webroot Compartilhado

O desafio do Certbot precisa que o Nginx sirva um arquivo em `/.well-known/acme-challenge/`. Esse arquivo é gerado pelo Certbot em um volume que o Nginx também enxerga. Atualize o `nginx/nginx.conf`, adicionando esse `location` **no bloco `listen 80`** (a validação acontece sempre por HTTP, mesmo depois de você já ter HTTPS funcionando — é assim que a renovação automática vai continuar funcionando):

```nginx
# nginx/nginx.conf
# Gateway unico da aplicacao: roteia para o frontend, para a API do backend
# e para o desafio HTTP do Let's Encrypt (renovacao de certificado)

upstream backend_upstream {
    server backend:8000;
}

server {
    listen 80;

    # Desafio do Certbot (Let's Encrypt) - precisa ficar acessivel por HTTP,
    # mesmo depois do HTTPS estar configurado, porque a renovacao automatica
    # do certificado reusa este mesmo caminho
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # Qualquer outra coisa em HTTP e redirecionada para HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}
```

O bloco `server { listen 443 ssl; ... }`, com as rotas da aplicação (`/api/`, `/admin/`, `/static/`, `/`), só vai ser adicionado na Parte 5, depois que o certificado existir — não dá para configurar `ssl_certificate` apontando para um arquivo que ainda não foi emitido.

---

## Parte 3 — Adicionando o Serviço `certbot` ao `docker-compose.yml`

Adicione dois volumes novos e o serviço `certbot`:

```yaml
services:
  # ... db, backend, frontend continuam iguais ...

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
      - static_volume:/app/staticfiles
      - certbot_www:/var/www/certbot
      - certbot_conf:/etc/letsencrypt

  certbot:
    image: certbot/certbot
    volumes:
      - certbot_www:/var/www/certbot
      - certbot_conf:/etc/letsencrypt

volumes:
  todo-db-data:
  static_volume:
  certbot_www:
  certbot_conf:
```

O `certbot_www` é o volume compartilhado com o Nginx que resolve o desafio (Parte 2). O `certbot_conf` guarda os certificados emitidos — também compartilhado com o Nginx, que vai precisar ler esses arquivos na Parte 5. O serviço `certbot` não expõe porta nenhuma: ele só roda comandos pontuais dentro do container, sob demanda.

---

## Parte 4 — Emitindo o Certificado

Suba (ou recarregue) a stack para o desafio funcionar:

```bash
docker compose up -d --build
```

Rode o Certbot pela primeira vez, pedindo a emissão do certificado:

```bash
docker compose run --rm certbot certonly \
  --webroot --webroot-path=/var/www/certbot \
  -d SEU-DOMINIO.com \
  --email SEU@EMAIL.com \
  --agree-tos --no-eff-email
```

- `certonly`: só emite/renova o certificado, não tenta configurar nenhum servidor web sozinho (quem serve o certificado é o nosso Nginx, configurado manualmente na Parte 5).
- `--webroot --webroot-path=/var/www/certbot`: usa o desafio HTTP da Parte 2, escrevendo o arquivo de verificação nesse caminho.
- `-d SEU-DOMINIO.com`: o domínio para o qual o certificado é emitido — precisa bater com o registro DNS apontado para o servidor.
- `--email` / `--agree-tos`: contato para avisos (ex.: certificado prestes a expirar sem renovação automática) e aceite dos termos de uso.

Se tudo der certo, o Certbot confirma a emissão e salva os arquivos em `/etc/letsencrypt/live/SEU-DOMINIO.com/` dentro do volume `certbot_conf`.

---

## Parte 5 — Configurando o Nginx com o Certificado Emitido

Atualize o `nginx/nginx.conf`, adicionando o bloco HTTPS completo (as mesmas rotas que a aplicação já tinha, mais os certificados emitidos pelo Certbot):

```nginx
# nginx/nginx.conf
# Gateway unico da aplicacao: roteia para o frontend, para a API do backend
# e para o desafio HTTP do Let's Encrypt (renovacao de certificado)

upstream backend_upstream {
    server backend:8000;
}

server {
    listen 80;

    # Desafio do Certbot (Let's Encrypt) - precisa continuar acessivel
    # por HTTP mesmo com o HTTPS configurado, para a renovacao automatica
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name SEU-DOMINIO.com;

    ssl_certificate /etc/letsencrypt/live/SEU-DOMINIO.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/SEU-DOMINIO.com/privkey.pem;

    location /static/ {
        alias /app/staticfiles/;
    }

    location /api/ {
        proxy_pass http://backend_upstream/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /admin/ {
        proxy_pass http://backend_upstream/admin/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass http://frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Parte 6 — Recarregando o Nginx

Não é preciso recriar o container — o Nginx sabe reler sua configuração sem derrubar conexões existentes:

```bash
docker compose exec nginx nginx -s reload
```

Acesse `https://SEU-DOMINIO.com/` e confirme o cadeado de conexão segura no navegador, sem nenhum aviso — diferente do certificado autoassinado da aula anterior, este é assinado por uma autoridade que o navegador já confia.

---

## Parte 7 — Automatizando a Renovação

Como o certificado expira em 90 dias, é preciso renovar automaticamente. Adicione um segundo container `certbot`, dedicado só a isso, rodando em loop:

```yaml
  certbot-renew:
    image: certbot/certbot
    volumes:
      - certbot_www:/var/www/certbot
      - certbot_conf:/etc/letsencrypt
    # Confere a cada 12h se algum certificado esta perto de expirar
    # (o Certbot so renova de fato quando faltam 30 dias ou menos)
    entrypoint: >
      sh -c 'trap exit TERM; while :; do
        certbot renew --webroot --webroot-path=/var/www/certbot --quiet;
        sleep 12h & wait $${!};
      done'
```

O comando `certbot renew` sozinho não recarrega o Nginx com o certificado novo — para isso, use a opção `--deploy-hook`, que roda um comando só quando uma renovação de fato acontece. Como o container do `certbot-renew` não tem acesso direto ao Nginx (são containers diferentes), a forma mais simples aqui é recarregar o Nginx manualmente após uma renovação, ou automatizar isso com um script de infraestrutura próprio — fica como próximo passo para quem for levar essa stack para produção de verdade.

---

## Parte 8 — Testando

No navegador, clique no cadeado ao lado da URL e confira os detalhes do certificado — emissor deve ser "Let's Encrypt", validade de aproximadamente 90 dias.

Pela linha de comando, também é possível inspecionar o certificado remotamente:

```bash
openssl s_client -connect SEU-DOMINIO.com:443 -servername SEU-DOMINIO.com < /dev/null
```

---

## Checklist final

- [ ] Domínio próprio com registro DNS tipo A apontando para o servidor
- [ ] `location /.well-known/acme-challenge/` configurado no `nginx.conf`, servido por HTTP
- [ ] Volumes `certbot_www` e `certbot_conf` criados e compartilhados entre `nginx` e `certbot`
- [ ] Certificado emitido com sucesso via `certbot certonly --webroot`
- [ ] `server { listen 443 ssl; ... }` configurado com `ssl_certificate`/`ssl_certificate_key` apontando para os arquivos emitidos
- [ ] `https://SEU-DOMINIO.com/` acessível sem nenhum aviso de segurança no navegador
- [ ] Serviço de renovação automática (`certbot-renew`) configurado

---

## Material de apoio

- Let's Encrypt — como funciona: https://letsencrypt.org/how-it-works/
- Certbot — documentação oficial: https://certbot.eff.org/
- Certbot — imagem oficial no Docker Hub: https://hub.docker.com/r/certbot/certbot
- Certbot — renovação automática: https://eff-certbot.readthedocs.io/en/stable/using.html#renewing-certificates
