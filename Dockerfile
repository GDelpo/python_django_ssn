# ---
# Stage 1: Compilar dependencias y assets de frontend
# Esta etapa instala todas las herramientas de build, compila los assets y prepara los paquetes de Python.
# ---
FROM python:3.12-slim-bookworm AS builder

WORKDIR /build

# 1. Instalar dependencias del sistema y Node.js.
# Node.js es un requisito para que los comandos de django-tailwind funcionen.
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl gnupg build-essential libpq-dev libmagic1 && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_22.x nodistro main" > /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends nodejs && \
    rm -rf /var/lib/apt/lists/*

# 2. Instalar dependencias Python.
# Se copia solo requirements.txt primero para aprovechar la caché de Docker.
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 3. Copiar todo el contexto del proyecto.
COPY . .

# 4. Copiar y renombrar el archivo de entorno para el build.
#    Esto crea el archivo .env que `decouple` buscará durante el build.
COPY .env.build /build/.env

# 5. Establecer el directorio de trabajo y los settings para el build.
WORKDIR /build/ssn
ENV DJANGO_SETTINGS_MODULE=config.settings.build

# 6. Instalar, actualizar y compilar los estilos de Tailwind en una sola capa para eficiencia.
#    - install: Descarga el CLI de Tailwind.
#    - update: Actualiza el CLI a la última versión.
#    - build: Genera el archivo CSS de producción, optimizado y purgado.
RUN python manage.py tailwind install && \
    python manage.py tailwind update && \
    python manage.py tailwind build

# 7. Recolectar todos los archivos estáticos (incluyendo el CSS recién creado por Tailwind).
RUN python manage.py collectstatic --noinput --clear


# ---
# Stage 2: Imagen final de producción, más liviana y segura
# Esta etapa solo contiene lo estrictamente necesario para ejecutar la aplicación.
# ---
FROM python:3.12-slim-bookworm

# Argumentos para definir el UID/GID y evitar problemas de permisos con los volúmenes.
ARG UID=1000
ARG GID=1000

# 1. Crear grupo, usuario no-root, e instalar solo las dependencias de ejecución.
RUN groupadd -g ${GID} -o python && \
    useradd --create-home -u ${UID} -g ${GID} -s /bin/bash python && \
    apt-get update && \
    apt-get install -y --no-install-recommends curl libpq5 netcat-openbsd postgresql-client libmagic1 && \
    rm -rf /var/lib/apt/lists/*

# 2. Crear la estructura de directorios que la aplicación necesita.
RUN mkdir -p /app/static /app/ssn/media/previews /app/ssn/media/comprobantes /app/ssn/logs && \
    chown -R python:python /app

WORKDIR /app

# 3. Variables de entorno estándar para Python en producción.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/ssn

# 4. Copiar los artefactos pre-compilados desde la etapa 'builder'.
#    Esto mantiene la imagen final pequeña y sin herramientas de build.
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder --chown=python:python /build/static /app/static
COPY --chown=python:python ./ssn /app/ssn
COPY --chown=python:python entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 5. Cambiar al usuario no-root por seguridad.
USER python

# 6. Exponer el puerto y definir el comando de inicio.
EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]