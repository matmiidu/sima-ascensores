#!/bin/sh
# Arranque del contenedor backend: aplica las migraciones, carga la cartera de demostración si se pide y la
# base está vacía, y levanta gunicorn.
set -e
python manage.py migrate --noinput
if [ "$SIMA_CARGAR_DEMO" = "1" ]; then
  python manage.py cargar_demo
fi
exec gunicorn config.wsgi --bind 0.0.0.0:8000 --workers 3 --timeout 60 --access-logfile -
