#!/bin/sh

set -e

echo "ℹ️ Iniciando aplicación..."

# Configurar entorno
export PYTHONPATH="/app/ssn"
export DJANGO_SETTINGS_MODULE="config.settings"

# Esperar por la base de datos
echo "⏳ Esperando a la base de datos..."
host="${POSTGRES_HOST:-db}"
port="${POSTGRES_PORT:-5432}"
db_name="${POSTGRES_DB:-ssn_db}"  # Usa la variable correcta para el nombre de la BD
user="${POSTGRES_USER:-ssn_user}"
password="${POSTGRES_PASSWORD}"
retries=0

# Primero verificar que el servicio está disponible
while ! nc -z "$host" "$port"; do
    retries=$((retries+1))
    if [ "$retries" -ge 30 ]; then
        echo "❌ Base de datos no disponible después de 30 intentos"
        exit 1
    fi
    echo "⏳ Esperando PostgreSQL... (intento $retries/30)"
    sleep 2
done

# Luego intentar conectarse específicamente a la base de datos correcta
retries=0
until PGPASSWORD="$password" psql -h "$host" -p "$port" -U "$user" -d "$db_name" -c "SELECT 1" > /dev/null 2>&1; do
    retries=$((retries+1))
    if [ "$retries" -ge 10 ]; then
        # Si no podemos conectarnos a la base de datos específica después de varios intentos,
        # intentemos crearla
        echo "⚠️ Base de datos $db_name no encontrada. Intentando crearla..."
        if PGPASSWORD="$password" psql -h "$host" -p "$port" -U "$user" -c "CREATE DATABASE $db_name" > /dev/null 2>&1; then
            echo "✅ Base de datos $db_name creada exitosamente"
            break
        else
            echo "❌ No se pudo crear la base de datos $db_name"
            exit 1
        fi
    fi
    echo "⏳ Esperando base de datos $db_name... (intento $retries/10)"
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