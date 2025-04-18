#!/bin/sh

set -e  # Detiene el script si hay errores

echo "🔄 Esperando a la base de datos..."
while ! nc -z ${POSTGRES_HOST:-db} ${POSTGRES_PORT:-5432}; do
  sleep 1
done

echo "✅ Base de datos disponible."

echo "📋 Verificando migraciones pendientes..."
PENDING=$(python ssn/manage.py showmigrations --plan | grep '\[ \]' | wc -l)

if [ "$PENDING" -gt 0 ]; then
  echo "🛠️ Migraciones pendientes detectadas. Ejecutando makemigrations..."
  python ssn/manage.py makemigrations
  python ssn/manage.py makemigrations operaciones

  echo "📦 Aplicando migraciones..."
  python ssn/manage.py migrate
else
  echo "✔️ No hay migraciones pendientes."
fi

echo "📦 Recolectando archivos estáticos..."
python ssn/manage.py collectstatic --no-input

echo "🔐 Verificando existencia de superusuario..."
python ssn/manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="${DJANGO_SUPERUSER_USERNAME}").exists():
    print("➡️  Creando superusuario '${DJANGO_SUPERUSER_USERNAME}'...")
    User.objects.create_superuser(
        "${DJANGO_SUPERUSER_USERNAME}",
        "${DJANGO_SUPERUSER_EMAIL}",
        "${DJANGO_SUPERUSER_PASSWORD}"
    )
else:
    print("✔️  El superusuario '${DJANGO_SUPERUSER_USERNAME}' ya existe.")
EOF

echo "🚀 Iniciando Gunicorn..."
exec "$@"
