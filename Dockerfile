# Stage 1: Compilar dependencias y assets de frontend
FROM python:3.12-slim-bookworm AS builder

WORKDIR /build

# Instalar dependencias del sistema y Node.js en una sola capa para eficiencia
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl gnupg build-essential libpq-dev libmagic1 && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_22.x nodistro main" > /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends nodejs && \
    rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python, copiando solo requirements.txt para aprovechar la caché
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación y compilar assets
COPY ./ssn /build/ssn
WORKDIR /build/ssn

ENV DJANGO_SETTINGS_MODULE=config.settings.build

RUN python manage.py tailwind install --no-input && \
    python manage.py tailwind build --no-input && \
    python manage.py collectstatic --noinput --clear


# ---
# Stage 2: Imagen final de producción, más liviana y segura
# ---
FROM python:3.12-slim-bookworm

ARG UID=1000
ARG GID=1000

# Crear grupo, usuario no-root, y toda la estructura de carpetas necesaria
RUN groupadd -g ${GID} -o python && \
    useradd --create-home -u ${UID} -g ${GID} -s /bin/bash python && \
    apt-get update && \
    apt-get install -y --no-install-recommends libpq5 netcat-openbsd postgresql-client libmagic1 && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /app/static /app/ssn/media/previews /app/ssn/media/comprobantes /app/ssn/logs && \
    chown -R python:python /app

WORKDIR /app

# Variables de entorno para la aplicación
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/ssn

# Copiar artefactos desde la etapa 'builder' y el código fuente
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder --chown=python:python /build/ssn/staticfiles /app/static
COPY --chown=python:python ./ssn /app/ssn
COPY --chown=python:python entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Cambiar al usuario no-root por seguridad
USER python

# Exponer el puerto (documentación) y definir el comando de inicio
EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]