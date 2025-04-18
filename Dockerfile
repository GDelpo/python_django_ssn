FROM python:3.12-slim-bookworm

WORKDIR /app

# Instalar Node.js
ARG NODE_MAJOR=22
RUN apt-get update \
    && apt-get install -y \
        ca-certificates curl gnupg \
        libpq-dev libmagic1 netcat-openbsd \
        gcc build-essential \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list \
    && apt-get update \
    && apt-get install nodejs -y \
    && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
    && apt-get clean \
    && useradd --create-home python \
    && chown python:python -R /app

# Cambiar al usuario no-root
USER python

# Configurar variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED="true" \
    PATH="${PATH}:/home/python/.local/bin" \
    USER="python" \
    SECRET_KEY=dummy \
    POSTGRES_DB=devdb \
    POSTGRES_USER=devuser \
    POSTGRES_PASSWORD=devpass \
    DB_HOST=localhost \
    DB_PORT=5432 \
    SSN_API_BASE_URL=https://example.com

# Instalar dependencias
COPY --chown=python:python requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY --chown=python:python . .

# Instalar y construir Tailwind + collectstatic
RUN python ssn/manage.py tailwind install --no-input && python ssn/manage.py tailwind build --no-input && python ssn/manage.py collectstatic --no-input

# Entrypoint y permisos
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "ssn.ssn.wsgi:application", "--bind", "0.0.0.0:8000"]
