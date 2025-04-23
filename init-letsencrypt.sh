#!/bin/bash

# Configuraciones desde variables de entorno o valores predeterminados
domain="${SSL_DOMAIN:-localhost}"
email="${SSL_EMAIL:-}" # No necesario para desarrollo interno
rsa_key_size=4096
data_path="./certbot"

# Crear directorios requeridos
mkdir -p "$data_path/conf/live/$domain"

# Crear configuración dummy para iniciar nginx
if [ ! -e "$data_path/conf/options-ssl-nginx.conf" ]; then
  echo "### Creando opciones dummy ssl..."
  mkdir -p "$data_path/conf"
  openssl req -x509 -nodes -newkey rsa:$rsa_key_size -days 1 \
    -keyout "$data_path/conf/live/$domain/privkey.pem" \
    -out "$data_path/conf/live/$domain/fullchain.pem" \
    -subj "/CN=localhost" 
  echo
fi

echo "### Iniciando contenedores..."
docker-compose up -d

# Para un entorno interno, necesitamos usar el desafío DNS o generar certificados autofirmados
echo ""
echo "### IMPORTANTE: Para un entorno interno, tienes dos opciones:"
echo "1. Configurar un plugin DNS para Certbot si tienes control sobre los registros DNS"
echo "2. Usar certificados autofirmados (recomendado para entornos puramente internos)"
echo ""
echo "Para generar un certificado autofirmado válido por 1 año:"
echo "openssl req -x509 -nodes -days 365 -newkey rsa:$rsa_key_size -keyout $data_path/conf/live/$domain/privkey.pem -out $data_path/conf/live/$domain/fullchain.pem"
echo ""
echo "Después de generar los certificados, ejecuta: docker-compose restart nginx"