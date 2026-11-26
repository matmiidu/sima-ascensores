# Servidor de SIMA (Django + Django REST Framework) para producción, servido con gunicorn.
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt requirements-produccion.txt ./
RUN pip install --no-cache-dir -r requirements-produccion.txt
COPY . .
# Archivos del panel de administración; los entrega whitenoise.
RUN DJANGO_DEBUG=0 DJANGO_SECRET_KEY=solo-para-construir python manage.py collectstatic --noinput
RUN useradd --create-home sima && chown -R sima /app
USER sima
EXPOSE 8000
CMD ["sh", "entrada.sh"]
