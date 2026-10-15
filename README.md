# SIMA · Sistema de Mantención de Ascensores

Proyecto de Ingeniería de Software I (UCM). Caso ficticio: **Ascensores Altavía**, empresa que mantiene
140 ascensores en 62 edificios. Enfoque adaptativo, tablero en JIRA (proyecto SIMA).

| Entrega | Fechas | Elementos | Estado |
|---|---|---|---|
| **Entrega 1** | 19 oct – 1 nov 2026 | H01, S01, H03, A03 | Construida; ver `docs/entrega1/` |
| Entrega 2 | 2 – 15 nov 2026 | H04, H06, A02 | Pendiente |
| Entrega 3 | 16 – 29 nov 2026 | H09, H10, A05 | Pendiente |

## Tecnologías

Python 3.12 · Django 5.2 con Django REST Framework · React 19 con TypeScript (Vite) como PWA ·
PostgreSQL (SQLite en desarrollo si no hay `DATABASE_URL`).

## Cómo correrlo

Servidor:

```bash
cd backend
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt      # en Linux/Mac: .venv/bin/pip
.venv/Scripts/python manage.py migrate
.venv/Scripts/python manage.py cargar_demo          # cartera ficticia; usuario jefe / sima-demo-2026
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

Panel de administración: http://localhost:8000/admin/ (mismo usuario).

Pruebas: `cd backend && .venv/Scripts/python manage.py test` (24 pruebas).

PostgreSQL opcional: `docker compose up -d` y `DATABASE_URL=postgres://sima:sima@localhost:5432/sima`.

## Estructura

```
backend/
  cartera/        H01: edificios, ascensores y técnicos
  planificacion/  H03: calendario mensual, feriados
  terreno/        S01: checklists de prueba recibidos sin conexión
frontend/src/
  paginas/        Cartera, ficha de edificio, Calendario, Terreno (S01)
  sinConexion.ts  guardado en el celular y envío al volver la señal
herramientas/
  validar_planilla.py   A03: revisión de la planilla y muestra para terreno
docs/entrega1/    criterios de aceptación, resultado de S01, acta de A03, revisión y capturas
```
