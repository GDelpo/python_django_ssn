#!/bin/sh

set -e

echo "ℹ️ Iniciando aplicación..."

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

# Crear superusuario si no existe y las variables están definidas
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    python ssn/manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="$DJANGO_SUPERUSER_USERNAME").exists():
    User.objects.create_superuser("$DJANGO_SUPERUSER_USERNAME", "$DJANGO_SUPERUSER_EMAIL", "$DJANGO_SUPERUSER_PASSWORD")
    print("✅ Superusuario creado")
else:
    print("✅ Superusuario ya existe")
EOF
fi

echo "🚀 Iniciando servidor..."
exec "$@"