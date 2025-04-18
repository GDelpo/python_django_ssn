# SSN Django Application

Sistema de gestión de operaciones financieras para presentación a la Superintendencia de Seguros de la Nación (SSN).

![Django](https://img.shields.io/badge/Django-5.1.7-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![Docker](https://img.shields.io/badge/Docker-ready-blue)

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

- Docker y Docker Compose
- Git

### Instalación con Docker (recomendado)

1. **Clonar el repositorio**

```bash
git clone git@github.com:GDelpo/python_django_ssn.git
cd python_django_ssn
```

2. **Configurar variables de entorno**

```bash
cp .env-example .env
# Edita el archivo .env con tus valores
```

3. **Iniciar con Docker Compose**

```bash
docker-compose up -d
```

4. **Acceder a la aplicación**

La aplicación estará disponible en http://localhost:8888 (o el puerto que hayas configurado en NGINX_PORT).

### Instalación local (desarrollo)

1. **Clonar el repositorio**

```bash
git clone https://github.com/tuusuario/ssn-django-application.git
cd ssn-django-application
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
cp .env-example .env
# Edita el archivo .env con tus valores
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

7. **Ejecutar servidor de desarrollo**

```bash
python manage.py runserver
```

## 🏗️ Estructura del Proyecto

```
.
├── .env                    # Variables de entorno
├── Dockerfile              # Configuración para Docker
├── docker-compose.yml      # Configuración de servicios
├── entrypoint.sh           # Script de inicio para Docker
├── nginx/                  # Configuración de Nginx
│   └── default.conf
├── requirements.txt        # Dependencias de Python
└── ssn/                    # Código principal de la aplicación
    ├── manage.py
    ├── apps/               # Aplicaciones de Django
    │   ├── operaciones/    # App principal de operaciones
    │   ├── ssn_client/     # Cliente para API de SSN
    │   └── theme/          # Configuración de Tailwind CSS
    ├── logs/               # Directorio para logs
    ├── media/              # Archivos subidos por usuarios
    └── ssn/                # Configuración del proyecto Django
```

## 🔧 Uso

1. **Crear una solicitud base**: Comienza especificando el tipo de entrega y el cronograma.
2. **Agregar operaciones**: Añade operaciones financieras específicas a la solicitud.
3. **Revisar solicitud**: Verifica los datos antes del envío a la SSN.
4. **Enviar a SSN**: Transmite la información a la Superintendencia de Seguros de la Nación.

## 🧪 Testing

Para ejecutar las pruebas:

```bash
cd ssn
python manage.py test
```

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

## 📋 Mantenimiento

### Backups

Para respaldar la base de datos:

```bash
docker-compose exec db pg_dump -U $POSTGRES_USER $POSTGRES_DB > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Logs

Para ver los logs de la aplicación:

```bash
docker-compose logs web
```

### Actualizaciones

Para actualizar la aplicación:

```bash
git pull
docker-compose down
docker-compose up -d --build
```