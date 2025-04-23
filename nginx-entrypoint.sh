#!/bin/sh

set -e

echo "ℹ️ Iniciando servicio Nginx con soporte SSL..."

# Instalar openssl si no está presente
if ! command -v openssl > /dev/null; then
    echo "⏳ Instalando openssl..."
    apk add --no-cache openssl
fi

# Definir variables (usar valores del .env o predeterminados)
DOMAIN="${SSL_DOMAIN:-localhost}"
SERVER_IP="${SSL_IP:-127.0.0.1}"
ORGANIZATION="${SSL_ORGANIZATION:-Example Organization}"
COUNTRY="${SSL_COUNTRY:-AR}"
CERT_DIR="/etc/letsencrypt/live/$DOMAIN"

# Verificar si los certificados ya existen
if [ ! -f "$CERT_DIR/fullchain.pem" ] || [ ! -f "$CERT_DIR/privkey.pem" ]; then
    echo "⏳ Generando certificados SSL autofirmados..."
    
    # Crear directorios necesarios
    mkdir -p "$CERT_DIR"
    
    # Generar certificado autofirmado
    openssl req -x509 -nodes -days 3650 -newkey rsa:4096 \
      -keyout "$CERT_DIR/privkey.pem" \
      -out "$CERT_DIR/fullchain.pem" \
      -subj "/CN=$DOMAIN/O=$ORGANIZATION/C=$COUNTRY" \
      -addext "subjectAltName = DNS:$DOMAIN,IP:$SERVER_IP"
    
    # Crear archivos de cadena para compatibilidad
    cp "$CERT_DIR/fullchain.pem" "$CERT_DIR/chain.pem"
    cp "$CERT_DIR/fullchain.pem" "$CERT_DIR/cert.pem"
    
    # Ajustar permisos
    chmod -R 644 "$CERT_DIR"
    chmod 700 "$CERT_DIR"
    chmod 600 "$CERT_DIR/privkey.pem"
    
    echo "✅ Certificados SSL generados correctamente"
else
    echo "✅ Certificados SSL ya existen"
fi

echo "🚀 Iniciando Nginx..."
# Ejecuta el comando original de nginx
exec nginx -g "daemon off;"