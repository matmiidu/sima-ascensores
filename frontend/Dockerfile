# Aplicación de SIMA (React + Vite, PWA). Se compila y la sirve Caddy, que además pone HTTPS y reenvía la API.
FROM node:22-alpine AS compilar
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM caddy:2.10-alpine
COPY --from=compilar /app/dist /srv
COPY Caddyfile /etc/caddy/Caddyfile
