# SSN Django Application

Sistema de gestión de operaciones financieras para presentación a la Superintendencia de Seguros de la Nación (SSN).

![Docker](https://img.shields.io/badge/Docker-ready-blue)
![Python](https://img.shields.io/badge/Python-3.12%2B-blue) 
![Django](https://img.shields.io/badge/Django-5.1%2B-blue) 
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15%2B-blue) 
![NGINX](https://img.shields.io/badge/NGINX-1.19%2B-blue)

## 📋 Descripción

Esta aplicación permite gestionar, registrar y enviar operaciones financieras a la SSN siguiendo los estándares requeridos. Facilita el proceso de registro y seguimiento de operaciones como compras, ventas, canjes y plazos fijos.

### Características principales

- Creación y gestión de solicitudes de operaciones
- Soporte para diferentes tipos de operaciones financieras (compras, ventas, canjes, plazos fijos)
- Interfaz intuitiva con Tailwind CSS
- Validación de datos según los requerimientos de la SSN
- Generación automática de reportes en Excel
- API client integrado para comunicación con servicios SSN
- Dockerizado para fácil despliegue

## 🚀 Instalación y Despliegue

### Requisitos previos

- Docker y Docker Compose (`docker compose`, versión 2+)
- Node.js y npm (para compilar Tailwind CSS)
- Git

### Instalación con Docker (recomendado)

1. **Clonar el repositorio**

```bash
git clone git@github.com:GDelpo/python_django_ssn.git
cd python_django_ssn
```

2. **Configurar archivos de entorno**

```bash
# Configurar variables de entorno
cp .env-example .env # Editar .env con tus valores

# Configurar Nginx
cp nginx/default.conf-example nginx/default.conf # Editar default.conf con tu dominio e IP que agregamos en el .env
```

3. **Preparar carpetas de media**

```bash
./prepare_media.sh
```

**‼ Es importante ejecutarlo al menos una vez antes del primer `docker compose up`.**

4. **Construir e iniciar con Docker Compose**

```bash
docker compose build --no-cache && docker compose up -d
```

4. **Acceder a la aplicación**

La aplicación estará disponible en http://localhost:8888 (o el puerto que hayas configurado en NGINX_PORT).  
Con SSL configurado, también estará en https://tu-dominio.com

### Instalación local (desarrollo)

1. **Clonar el repositorio**

```bash
git clone git@github.com:GDelpo/python_django_ssn.git
cd python_django_ssn
```

2. **Crear y activar entorno virtual**

```bash
python -m venv venv
source venv/bin/activate  # En Linux/Mac
venv\Scripts\activate     # En Windows
```

3. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**

```bash
cp .env-example .env # Edita el archivo .env con tus valores
```

5. **Aplicar migraciones**

```bash
cd ssn
python manage.py migrate
```

6. **Instalar y compilar Tailwind**

```bash
python manage.py tailwind install
python manage.py tailwind build
```

**o para desarrollo continuo:**

```bash
python manage.py tailwind start  # Para desarrollo continuo, abrir en otra consola aparte.
```

7. **Ejecutar servidor de desarrollo**

```bash
python manage.py runserver
```

## 🏗️ Estructura del Proyecto

```
.
├── .env-example             # Plantilla para variables de entorno
├── .env                     # Variables de entorno (no incluido en Git)
├── Dockerfile               # Configuración para Docker
├── Dockerfile.nginx         # Configuración específica para Nginx
├── docker-compose.yml       # Configuración de servicios
├── entrypoint.sh            # Script de inicio para el contenedor web
├── nginx/                   # Configuración de Nginx
│   ├── default.conf-example # Plantilla de configuración de Nginx
│   └── default.conf         # Configuración de Nginx (no incluido en Git)
├── nginx-entrypoint.sh      # Script de inicio para Nginx con certificados
├── prepare_media.sh         # Crea carpetas necesarias con permisos
├── requirements.txt         # Dependencias de Python
└── ssn/                     # Código principal de la aplicación
    ├── manage.py
    ├── apps/                # Aplicaciones de Django
    │   ├── operaciones/     # App principal de operaciones
    │   ├── ssn_client/      # Cliente para API de SSN
    │   └── theme/           # Configuración de Tailwind CSS
    ├── logs/                # Directorio para logs
    ├── media/               # Archivos subidos por usuarios
    └── ssn/                 # Configuración del proyecto Django
```

## 🔧 Uso

1. **Crear una solicitud base**: Comienza especificando el tipo de entrega y el cronograma.
2. **Agregar operaciones**: Añade operaciones financieras específicas a la solicitud.
3. **Revisar solicitud**: Verifica los datos antes del envío a la SSN.
4. **Enviar a SSN**: Transmite la información a la Superintendencia de Seguros de la Nación.

## 🔄 Variables de Entorno

Las principales variables de entorno que debes configurar:

| Variable | Descripción |
|----------|-------------|
| SECRET_KEY | Clave secreta para Django |
| DEBUG | Modo de depuración (True/False) |
| ALLOWED_HOSTS | Hosts permitidos |
| POSTGRES_DB | Nombre de la base de datos |
| POSTGRES_USER | Usuario de PostgreSQL |
| POSTGRES_PASSWORD | Contraseña de PostgreSQL |
| SSN_API_USERNAME | Usuario para la API de SSN |
| SSN_API_PASSWORD | Contraseña para la API de SSN |
| SSN_API_CIA | Código de compañía para SSN |
| SSN_API_BASE_URL | URL base de la API de SSN |
| SSL_DOMAIN | Dominio para certificados SSL |
| SSL_IP | Dirección IP del servidor |
| NGINX_PORT | Puerto para Nginx (por defecto 8888) |

## 📋 Mantenimiento

### Backups

Para respaldar la base de datos:

```bash
docker compose exec db pg_dump -U $POSTGRES_USER $POSTGRES_DB > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Logs

Para ver los logs de la aplicación:

```bash
docker compose logs web
```

### Actualizaciones

Para actualizar la aplicación:

```bash
git pull
docker compose down
docker compose up -d --build
```

### Renovación de certificados SSL

Los certificados se renuevan automáticamente con el contenedor certbot, pero si necesitas renovación manual:

```bash
docker compose exec certbot certbot renew
docker compose restart nginx
```

### Limpieza de solicitudes antiguas (sin enviar y vacías)

El comando `clean_requests` elimina solicitudes sin operaciones que no fueron enviadas,
y cuya antigüedad supera cierta cantidad de días (por defecto, 7 días).

Puedes ejecutarlo de estas dos formas:

**Desde contenedor Docker:**

```bash
docker compose exec web python ssn/manage.py clean_requests --days 7 # Reemplaza 7 por el número de días que desees (Es opcional usar --days)
```

**En entorno local de desarrollo:**

```bash
cd ssn
python manage.py clean_requests --days 7 # Reemplaza 7 por el número de días que desees (Es opcional usar --days)
```

> 💡 **Se recomienda programar este comando en el *host* mediante `cron`.** Podés utilizar herramientas como [crontab.guru](https://crontab.guru/) para validar y entender la sintaxis.

## 🛡️ Seguridad

Este repositorio está configurado para no incluir archivos con información sensible.  
Los archivos con datos sensibles no deben subirse a Git:

- `.env` (contiene contraseñas y claves)
- `nginx/default.conf` (configuración específica de servidor)

## ✏ TODOs

- Generar presentación MENSUAL de operaciones a la SSN.
- Revisar APIS BYMA, para poder generar reportes, etc.
