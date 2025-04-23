# Stage 1: Compilar dependencias y assets
FROM python:3.12-slim-bookworm AS builder

WORKDIR /build

# Instalar dependencias del sistema para compilación
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc curl gnupg build-essential libmagic1 \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_22.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list \
    && apt-get update && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Variables para construcción
ENV SECRET_KEY=dummy DJANGO_SETTINGS_MODULE=config.settings

# Instalar dependencias Python
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Compilar assets (siguiendo el patrón del ejemplo oficial)
COPY . .
RUN cd ssn \
    && python manage.py tailwind install --no-input \
    && python manage.py tailwind build --no-input \
    && python manage.py collectstatic --no-input \
    && echo "Contenido del directorio static:" \
    && ls -la static/ || echo "No se encontró el directorio static/" \
    && mkdir -p /build/static \
    && cp -r static/. /build/static/ || echo "No se pudieron copiar archivos estáticos"

# Stage 2: Imagen final
FROM python:3.12-slim-bookworm

ARG UID=1000
ARG GID=1000

WORKDIR /app

# Instalar solo dependencias runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 netcat-openbsd postgresql-client libmagic1 curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -g ${GID} python 2>/dev/null || true \
    && useradd --create-home -u ${UID} -g ${GID} -s /bin/bash python 2>/dev/null || true \
    && mkdir -p /app/ssn/logs /app/ssn/media /app/static \
    && chown -R ${UID}:${GID} /app

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings \
    PYTHONPATH=/app/ssn

# Copiar dependencias y archivos
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder --chown=${UID}:${GID} /build/static /app/static
COPY --chown=${UID}:${GID} ./ssn /app/ssn
COPY --chown=${UID}:${GID} entrypoint.sh /entrypoint.sh

# Verificar contenido del directorio estático
RUN chmod +x /entrypoint.sh \
    && echo "Verificando archivos estáticos:" \
    && ls -la /app/static/ || echo "No hay archivos estáticos"

USER ${UID}:${GID}
EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]