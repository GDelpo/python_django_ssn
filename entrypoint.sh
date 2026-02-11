#!/bin/sh

set -e

# ============================================================================
# If running as root, fix volume permissions and re-exec as 'python' user.
# This solves the recurring PermissionError on Docker volume mounts
# (volumes mount as root, but the app runs as UID 1000).
# ============================================================================
if [ "$(id -u)" = '0' ]; then
    echo "🔧 Ajustando permisos de volúmenes montados..."
    chown -R python:python /app/ssn/logs /app/ssn/media 2>/dev/null || true
    echo "✅ Permisos ajustados, cambiando a usuario 'python'..."
    exec gosu python "$0" "$@"
fi

# ============================================================================
# From here on, we are running as the 'python' user (UID 1000)
# ============================================================================
echo "ℹ️ Iniciando aplicación (usuario: $(whoami))..."

# Esperar por la base de datos
echo "⏳ Esperando a la base de datos en ${POSTGRES_HOST}:${POSTGRES_PORT}..."
retries=0
while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
    retries=$((retries+1))
    if [ "$retries" -ge 30 ]; then
        echo "❌ Base de datos no disponible después de 30 intentos"
        exit 1
    fi
    sleep 2
done
echo "✅ Base de datos disponible"

# Aplicar migraciones
echo "ℹ️ Aplicando migraciones..."
python ssn/manage.py migrate --noinput
echo "✅ Migraciones aplicadas"

# Crear superusuario solo en modo local (sin servicio de identidad externo)
# Si IDENTITY_SERVICE_URL está configurado, los usuarios se gestionan desde el servicio de identidad
if [ -z "$IDENTITY_SERVICE_URL" ]; then
    if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
        python ssn/manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email="$DJANGO_SUPERUSER_EMAIL").exists():
    User.objects.create_superuser(
        email="$DJANGO_SUPERUSER_EMAIL",
        password="$DJANGO_SUPERUSER_PASSWORD",
        first_name="${DJANGO_SUPERUSER_FIRST_NAME:-Admin}",
        last_name="${DJANGO_SUPERUSER_LAST_NAME:-User}"
    )
    print("✅ Superusuario creado")
else:
    print("✅ Superusuario ya existe")
EOF
    fi
else
    echo "ℹ️ Usando servicio de identidad externo - saltando creación de superusuario local"
fi

echo "🚀 Iniciando servidor..."
exec "$@"