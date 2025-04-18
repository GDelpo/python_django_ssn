#!/bin/bash

# Script de despliegue para SSN Django Application
set -e

# Colores para la salida
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Iniciando despliegue de SSN Django Application ===${NC}"

# Verificar si Docker y Docker Compose están instalados
if ! command -v docker &> /dev/null || ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker y/o Docker Compose no están instalados.${NC}"
    echo -e "${YELLOW}Instalando Docker y Docker Compose...${NC}"
    
    # Instalar Docker
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    
    # Instalar Docker Compose
    apt-get update
    apt-get install -y docker-compose
fi

# Verificar si .env existe
if [ ! -f .env ]; then
    echo -e "${RED}El archivo .env no existe. Creando uno a partir de .env-example...${NC}"
    if [ -f .env-example ]; then
        cp .env-example .env
        echo -e "${YELLOW}Por favor, edita el archivo .env con tus valores antes de continuar.${NC}"
        exit 1
    else
        echo -e "${RED}No se encontró .env-example. Por favor, crea un archivo .env manualmente.${NC}"
        exit 1
    fi
fi

# Crear carpeta de logs si no existe
mkdir -p ssn/logs

# Detener contenedores existentes
echo -e "${YELLOW}Deteniendo contenedores existentes...${NC}"
docker-compose down

# Construir y levantar contenedores
echo -e "${YELLOW}Construyendo y levantando contenedores...${NC}"
docker-compose build
docker-compose up -d

# Mostrar logs iniciales
echo -e "${YELLOW}Mostrando logs iniciales...${NC}"
docker-compose logs --tail=50 web

echo -e "${GREEN}=== Despliegue completado ====${NC}"
echo -e "${GREEN}La aplicación debería estar disponible en http://localhost:\$(grep NGINX_PORT .env | cut -d '=' -f2)${NC}"