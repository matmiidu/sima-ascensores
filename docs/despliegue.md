# Ambiente de despliegue de SIMA

SIMA se despliega con tres contenedores de Docker, definidos en `docker-compose.produccion.yml`:

| Contenedor | Imagen | Qué hace |
|---|---|---|
| `db` | `postgres:17` | Base de datos PostgreSQL. Sus datos viven en el volumen `datos_produccion`. No se publica hacia afuera: solo la ve el backend. |
| `backend` | `backend/Dockerfile` (Python 3.12) | Django + Django REST Framework servido con gunicorn (3 procesos). Al arrancar aplica las migraciones y, si se pide, carga la cartera de demostración. |
| `web` | `frontend/Dockerfile` (Node 22 para compilar, Caddy 2.10 para servir) | Entrega la aplicación React ya compilada (PWA), reenvía `/api`, `/admin` y `/static` al backend y pone HTTPS. |

```
celular / navegador ──HTTPS──> web (Caddy) ──/api, /admin, /static──> backend (gunicorn + Django) ──> db (PostgreSQL)
                                   └── el resto: la aplicación compilada (index.html, sw.js, ...)
```

## Por qué así

- **PostgreSQL** es el gestor que pide la asignatura y el que se eligió en el plan (EV2). En desarrollo se puede
  seguir usando SQLite sin Docker; el código es el mismo, porque la base se elige con `DATABASE_URL`.
- **HTTPS es obligatorio**, no un adorno: el service worker, que permite abrir SIMA sin señal (S01, H06, H07),
  solo funciona con HTTPS o en `localhost`. Caddy lo configura solo.
- **gunicorn** reemplaza al `runserver` de desarrollo, que no está hecho para producción.
- Las respuestas de la API llevan `Cache-Control: no-store` (hallazgo de la prueba de H07) y Caddy agrega
  `Strict-Transport-Security`; lo que entra por HTTP se redirige a HTTPS.

## Cómo se levanta

1. Copiar `despliegue/produccion.env.example` como `despliegue/produccion.env` y completar `POSTGRES_PASSWORD`
   y `DJANGO_SECRET_KEY` con claves largas al azar:
   `python -c "import secrets; print(secrets.token_urlsafe(40))"`. Ese archivo no se sube al repositorio.
2. Construir y levantar:
   ```
   docker compose -f docker-compose.produccion.yml --env-file despliegue/produccion.env up -d --build
   ```
3. Abrir `https://localhost`. Con `SIMA_DOMINIO=localhost` Caddy usa un certificado propio y el navegador
   avisa que no lo conoce ("Avanzado" > "Continuar"). Con un dominio real que apunte al servidor, Caddy pide
   un certificado de Let's Encrypt y no hay aviso.

Con `SIMA_CARGAR_DEMO=1` la primera vez se carga la cartera ficticia y los usuarios de prueba (clave `sima`).
En una empresa real va en `0` y la cartera se carga con **Importar planilla** (H02).

## Operación

| Tarea | Comando |
|---|---|
| Ver el estado | `docker compose -f docker-compose.produccion.yml --env-file despliegue/produccion.env ps` |
| Ver el registro del servidor | `... logs -f backend` |
| Actualizar a una versión nueva | `git pull` y `... up -d --build` (las migraciones se aplican al arrancar) |
| Respaldar la base | `... exec db pg_dump -U sima sima > respaldo.sql` |
| Restaurar un respaldo | `... exec -T db psql -U sima sima < respaldo.sql` |
| Correr las pruebas con PostgreSQL | `... run --rm --no-deps -e DJANGO_DEBUG=1 backend python manage.py test` |
| Detener (los datos se conservan) | `... down` |

## Verificación (26 de noviembre de 2026)

En el computador del equipo (Docker 28.4, Windows 11):

- Las imágenes se construyen y los tres contenedores arrancan; la base queda "healthy" antes de que arranque el backend.
- **79 de 79 pruebas automáticas aprobadas contra PostgreSQL 17**, dentro del contenedor del backend.
- Por `https://localhost`: la aplicación (200), el manifiesto de la PWA (200), la API (`no-store`), el panel de
  administración con sus estilos (200) y la redirección de HTTP a HTTPS (308).
- Flujo completo sobre PostgreSQL: el jefe genera noviembre (140 de 140 equipos), Luis prepara su jornada
  (hasta el 2 de diciembre) y registra una mantención, y el jefe descarga el informe del Edificio Plaza en PDF.

## Pendiente

Publicarlo en un servidor con dominio propio. Eso permite la prueba en un celular real (RNF-01 y H07 dentro de
un subterráneo) y es el único paso que falta para que lo use una empresa: el ambiente ya está configurado.
