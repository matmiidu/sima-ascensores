# SIMA · Sistema de Mantención de Ascensores

Proyecto de Ingeniería de Software I (UCM). Caso ficticio: **Ascensores Altavía**, empresa que mantiene
140 ascensores en 62 edificios. Enfoque adaptativo, tablero en JIRA (proyecto SIMA).

| Entrega | Fechas | Elementos | Estado |
|---|---|---|---|
| Entrega 1 | 19 oct – 1 nov 2026 | H01, S01, H03, A03 | Construida; ver `docs/entrega1/` |
| Entrega 2 | 2 – 15 nov 2026 | H04, H06, A02 | Construida; ver `docs/entrega2/` |
| Entrega 3 | 16 – 29 nov 2026 | H09, H10, A05 | Construida; ver `docs/entrega3/` |
| **Entrega 4** (adicional) | 26 nov – 3 dic 2026 | H07, H02 | Construida; ver `docs/entrega4/` |

## Tecnologías

Python 3.12 · Django 5.2 con Django REST Framework · React 19 con TypeScript (Vite) como PWA ·
PostgreSQL 17 (SQLite en desarrollo si no hay `DATABASE_URL`) · informe en PDF con xhtml2pdf, desde una plantilla HTML ·
despliegue con Docker: gunicorn y Caddy con HTTPS (ver `docs/despliegue.md`).

## Cómo correrlo

Servidor:

```bash
cd backend
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt      # en Linux/Mac: .venv/bin/pip
.venv/Scripts/python manage.py migrate
.venv/Scripts/python manage.py cargar_demo          # cartera ficticia y usuarios de prueba
.venv/Scripts/python manage.py runserver
```

Aplicación (otra terminal):

```bash
cd frontend
npm install
npm run dev            # http://localhost:5173
# para probar el modo sin conexión hay que usar la versión compilada:
npm run build && npm run preview   # http://localhost:4173
```

Usuarios de prueba, todos con la clave `sima`: `jefe` para el jefe técnico (cartera, calendario, certificaciones e informes), `asistente` para la
asistente administrativa (importar la planilla) y `juan`,
`rodrigo`, `camila`, `luis`, `andres` y `felipe` para los técnicos (sus visitas y el checklist).

Panel de administración: http://localhost:8000/admin/ (usuario `jefe`).

Pruebas: `cd backend && .venv/Scripts/python manage.py test` (79 pruebas).

PostgreSQL en desarrollo: `docker compose up -d` y `DATABASE_URL=postgres://sima:sima@localhost:5432/sima`.

## Despliegue

```bash
cp despliegue/produccion.env.example despliegue/produccion.env   # y completar las claves
docker compose -f docker-compose.produccion.yml --env-file despliegue/produccion.env up -d --build
# https://localhost
```

PostgreSQL + Django con gunicorn + Caddy con HTTPS. Detalle, operación y verificación en `docs/despliegue.md`.

## Estructura

```
backend/
  cartera/        H01: edificios, ascensores y técnicos; H04: usuario de cada técnico; H10: certificaciones;
                  H02: importar la planilla (importacion.py)
  planificacion/  H03: calendario mensual, feriados; H04: visitas del día de un técnico; H07: jornada sin señal
  terreno/        H06: registro de la mantención con su checklist (S01 queda como evidencia);
                  H09: informe mensual en PDF (informe.py y templates/terreno/informe_mensual.html)
  config/permisos.py   quién consulta y quién modifica
frontend/src/
  paginas/        Jefe técnico: Cartera, ficha de edificio, Calendario, Checklists, Certificaciones,
                  Informes y registro de una mantención
                  Técnico: Mis visitas y Checklist
  terreno.ts      copia de las visitas en el celular, guardado sin señal y envío al volver
herramientas/
  validar_planilla.py   A03: revisión de la planilla y muestra para terreno
docs/entrega1/    criterios de aceptación, resultado de S01, acta de A03, revisión y capturas
docs/entrega2/    planificación, criterios de aceptación, acta de A02, verificación de RNF-01, revisión y capturas
docs/entrega3/    criterios de aceptación, acta de A05 con el extracto de la OGUC, ejemplos del informe, revisión y capturas
docs/entrega4/    planificación, criterios de aceptación, prueba de la jornada sin señal, revisión y capturas
docs/despliegue.md   ambiente de despliegue con Docker
```
