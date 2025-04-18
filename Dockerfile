FROM python:3.12-slim-bookworm

# Instala Node.js (para Django Tailwind) y dependencias
ARG NODE_MAJOR=22
RUN apt-get update \
    && apt-get install -y curl gnupg tzdata build-essential libpq-dev libmagic1 netcat-openbsd \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list \
    && apt-get update && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Configurar variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instala dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de la app
COPY . .

# Tailwind y staticfiles (con SECRET_KEY dummy porque es obligatorio)
RUN SECRET_KEY=dummy python ssn/manage.py tailwind install --no-input --no-package-lock
RUN SECRET_KEY=dummy python ssn/manage.py tailwind build --no-input
RUN SECRET_KEY=dummy python ssn/manage.py collectstatic --no-input

# Entrypoint y permisos
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "ssn.ssn.wsgi:application", "--bind", "0.0.0.0:8000"]
