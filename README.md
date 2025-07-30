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
- Python 3.12 o superior (para desarrollo local)
- PostgreSQL 15 o superior (para desarrollo local)
- Certificados SSL válidos (opcional, pero recomendado para producción)

<details>

<summary>⚙️ Guía para Configurar Permisos de Docker en Linux  🐧</summary>

Este es el procedimiento para permitir que un usuario ejecute comandos de `docker` sin `sudo` y para diagnosticar y resolver los problemas de permisos más habituales.

##### Paso 1: Asegurar que el grupo `docker` exista y añadir tu usuario

Primero, nos aseguramos de que el grupo `docker` exista y luego agregamos nuestro usuario a él.

1.  **Ejecutá los siguientes dos comandos.** El primero crea el grupo `docker` si no existe (si ya existe, solo mostrará un error inofensivo). El segundo agrega tu usuario actual (identificado por la variable `$USER`) a ese grupo.

    ```bash
    sudo groupadd docker
    sudo usermod -aG docker $USER
    ```

##### Paso 2: Aplicar los cambios de grupo (Paso crucial 🔄)

Los cambios de grupo no se aplican a las sesiones de terminal que ya están abiertas. Este es el punto donde ocurren la mayoría de los problemas.

1.  **Cerrá la sesión por completo y volvé a entrar.** Esta es la forma más confiable de asegurar que tu usuario inicie con los nuevos permisos.

    ```bash
    exit
    ```

2.  **Reconectate** a tu servidor.

-----

##### Paso 3: Verificar la instalación

Una vez que te hayas reconectado, verificá si la configuración funcionó.

1.  **Ejecutá un comando de Docker** sin `sudo`:
    ```bash
    docker ps
    ```
2.  Si todo está correcto, deberías ver una tabla vacía con los encabezados `CONTAINER ID`, `IMAGE`, etc., y **ningún error de "permission denied"**. Si es así, ¡listo\! ✅

-----

##### Troubleshooting: ¿Todavía tenés el error "permission denied"? ⚠️

Si después de reiniciar la sesión el error persiste, el problema casi siempre está en los permisos del archivo de comunicación de Docker, conocido como "socket".

1.  **Inspeccioná los permisos del socket** de Docker con este comando:

    ```bash
    ls -l /var/run/docker.sock
    ```

2.  **Analizá la salida.** Tenés que fijarte en el propietario y el grupo (la tercera y cuarta columna).

      * **Salida CORRECTA:** El grupo debe ser `docker`.
        ```
        srw-rw---- 1 root docker 0 jul 30 15:30 /var/run/docker.sock
        ```
      * **Salida INCORRECTA:** El grupo es `root`, lo que causa el error.
        ```
        srw-rw---- 1 root root 0 jul 30 15:20 /var/run/docker.sock
        ```

3.  **Corregí los permisos (si es necesario).** Si tu salida fue la incorrecta, ejecutá este comando para cambiar el grupo del archivo a `docker`:

    ```bash
    sudo chown root:docker /var/run/docker.sock
    ```

4.  **Volvé a verificar.** Ahora sí, el comando `docker ps` debería funcionar inmediatamente.

</details>

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
```

3. **Construir e iniciar con Docker Compose**

```bash
docker compose build --no-cache && docker compose up -d
```

4. **Acceder a la aplicación**

La aplicación estará disponible en https://'SSL_DOMAIN':'NGINX_PORT_HTTPS'" o "https://'SSL_IP':'NGINX_PORT_HTTPS'". Valores que debes configurar en tu archivo `.env`. Entonces, asegúrate de que el puerto NGINX esté libre y que el dominio o IP estén correctamente configurados.

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

> [!TIP]
> Si estás en un entorno Windows y encuentras un error relacionado con la librería `python-magic`, es probable que necesites una versión precompilada. Para solucionarlo, puedes optar por una de las siguientes opciones:
> * **Reemplazar en `requirements.txt`**: Edita tu archivo `requirements.txt` y cambia `python-magic` por `python-magic-bin`.
> * **Instalación manual**: Si prefieres no modificar el `requirements.txt` o necesitas instalarlo de forma puntual, ejecuta el siguiente comando:
>  ```bash
>  pip install python-magic-bin
>  ```
> * **Desinstalación (si ya tienes `python-magic` y no funciona)**: Si ya intentaste instalar `python-magic` sin éxito, te recomendamos desinstalarlo primero antes de instalar la versión `bin`:
>  ```bash
>  pip uninstall python-magic
>  pip install python-magic-bin
>  ```

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

> [!IMPORTANT] 
> Tenemos `DJANGO_SETTINGS_MODULE=config.settings.dev` que es el entorno de desarrollo, trae configuraciones de depuración y desarrollo, además de que no se usa la base de datos de producción, sino una SQLite en el directorio `ssn/`.

## 🏗️ Estructura del Proyecto

```
.
├── .env-example              # Plantilla para variables de entorno
├── .env                      # Variables de entorno (no incluido en Git)
├── Dockerfile                # Configuración para Docker
├── Dockerfile.nginx          # Configuración específica para Nginx
├── docker-compose.yml        # Configuración de servicios
├── entrypoint.sh             # Script de inicio para el contenedor web
├── nginx/                    # Configuración de Nginx
│   ├── default.conf.template # Plantilla de configuración de Nginx
├── nginx-entrypoint.sh       # Script de inicio para Nginx con certificados
├── requirements.txt          # Dependencias de Python
└── ssn/                      # Código principal de la aplicación
    ├── manage.py
    ├── apps/                 # Aplicaciones de Django
    │   ├── operaciones/      # App principal de operaciones
    │   ├── ssn_client/       # Cliente para API de SSN
    │   └── theme/            # Configuración de Tailwind CSS y Templates base
    ├── logs/                 # Directorio para logs
    ├── media/                # Archivos subidos por usuarios
    └── config/               # Configuración del proyecto Django
```

## 🔧 Uso

1. **Crear una solicitud base**: Comienza especificando el tipo de entrega y el cronograma.
2. **Agregar operaciones**: Añade operaciones financieras específicas a la solicitud.
3. **Revisar solicitud**: Verifica los datos antes del envío a la SSN.
4. **Enviar a SSN**: Transmite la información a la Superintendencia de Seguros de la Nación.

## 🔄 Variables de Entorno

Las principales variables de entorno que debes configurar:

| Variable | Descripción | Ejemplo / Notas |
|----------|-------------|-----------------|
| `DJANGO_SETTINGS_MODULE` | Define el módulo de configuración de Django a utilizar. | `config.settings.prod` (producción) o `config.settings.dev` (desarrollo) |
| `DEBUG` | Activa o desactiva el modo de depuración de Django. En producción, debe ser `False`. | `True` o `False` |
| `SECRET_KEY` | **Clave secreta única y segura para tu instalación de Django.** ¡Absolutamente crítica para la seguridad! | Genera una cadena aleatoria compleja. |
| `ALLOWED_HOSTS` | Lista de hosts/dominios permitidos para servir la aplicación. Múltiples valores se separan con comas. | `"localhost,inversiones.test.tu-compania.com,192.168.190.001"` |
| `POSTGRES_DB` | Nombre de la base de datos PostgreSQL a la que la aplicación se conectará. | `inversiones_db` |
| `POSTGRES_USER` | Nombre de usuario para la conexión a la base de datos PostgreSQL. | `inversiones_user` |
| `POSTGRES_PASSWORD` | **Contraseña** del usuario de PostgreSQL. | |
| `POSTGRES_HOST` | Host donde se ejecuta el servidor de base de datos PostgreSQL. | `db` (común en Docker Compose) o `localhost` |
| `POSTGRES_PORT` | Puerto de conexión de la base de datos PostgreSQL. | `5432` |
| `SSN_API_USERNAME` | Nombre de usuario para autenticación con la API de la SSN. | |
| `SSN_API_PASSWORD` | **Contraseña** para autenticación con la API de la SSN. | |
| `SSN_API_CIA` | Código de compañía asociado a las operaciones de la API de SSN. | `0000` |
| `SSN_API_BASE_URL` | URL base de la API de la SSN. Asegúrate de usar la URL correcta para el entorno (test/producción). | `https://testri.ssn.gob.ar/api` |
| `SSL_DOMAIN` | Dominio principal para la configuración de certificados SSL. | `inversiones.test.tu-compania.com` |
| `SSL_IP` | Dirección IP asociada al dominio SSL (útil para ciertas configuraciones de certificados). | `192.168.190.001` |
| `NGINX_PORT_HTTP` | Puerto HTTP que Nginx expondrá en el host. | `8888` (o `80` para el puerto HTTP estándar) |
| `NGINX_PORT_HTTPS` | Puerto HTTPS que Nginx expondrá en el host. | `443` (el puerto HTTPS estándar) |
| `COMPANY_NAME` | Nombre de la compañía a mostrar en la aplicación. | `Tu Compania` |
| `COMPANY_WEBSITE` | URL del sitio web oficial de la compañía. | `https://www.tu-compania.com` |
| `COMPANY_LOGO_URL` | URL del logo de la compañía para usar en la aplicación. | `https://tu-compania_logo_negro.png` |

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

Para ver los logs de Nginx:

```bash
docker compose logs nginx
```

También puedes acceder a los logs propios de Django yendo al directorio `ssn/logs/`.

### Renovación de certificados SSL

Los certificados se renuevan automáticamente con el contenedor certbot, pero si necesitas renovación manual:

```bash
docker compose exec certbot certbot renew
docker compose restart nginx
```

### 🔹 Limpieza de solicitudes antiguas (sin enviar y vacías)

El comando `clean_requests` elimina solicitudes sin operaciones asociadas, que no fueron enviadas y cuya antigüedad supera cierta cantidad de días (**por defecto, 7 días**).

**Desde contenedor Docker:**

```bash
docker compose exec web python ssn/manage.py clean_requests --days 7
# Reemplaza 7 por el número de días que desees (el parámetro --days es opcional)
```

**En entorno local de desarrollo:**

```bash
cd ssn
python manage.py clean_requests --days 7
# Reemplaza 7 por el número de días que desees (el parámetro --days es opcional)
```

---

### 🔹 Limpieza de archivos Excel de previews

El comando `clean_preview_excels` elimina archivos temporales de Excel generados como preview para solicitudes, cuya antigüedad supera cierta cantidad de horas (**por defecto, 1 hora**).

**Desde contenedor Docker:**

```bash
docker compose exec web python ssn/manage.py clean_preview_excels --hours 1
# Reemplaza 1 por la cantidad de horas que desees (el parámetro --hours es opcional)
```

**En entorno local de desarrollo:**

```bash
cd ssn
python manage.py clean_preview_excels --hours 1
# Reemplaza 1 por la cantidad de horas que desees (el parámetro --hours es opcional)
```

> [!TIP]
> **Se recomienda programar estos comandos en el *host* mediante `cron`** para que la limpieza sea automática y la aplicación no acumule datos ni archivos innecesarios.
>
> **Ejemplo de entrada en crontab para ejecutarlo periódicamente:**
>
> ```cron
> 0 * * * * docker compose exec web python ssn/manage.py clean_preview_excels # “At minute 0.”
> 0 * * * 1 docker compose exec web python ssn/manage.py clean_requests # “At minute 0 on Monday.”
> ```
>
> Herramienta útil para probar la sintaxis: [crontab.guru](https://crontab.guru/)

## 🛡️ Seguridad

Este repositorio está configurado para no incluir archivos con información sensible.  
Los archivos con datos sensibles no deben subirse a Git:

- `.env` (contiene contraseñas y claves)

## ✏ TODOs

- Generar presentación MENSUAL de operaciones a la SSN.
- Revisar APIS BYMA, para poder generar reportes, etc.

---

## 📧 Contacto

Si tenes preguntas, sugerencias o necesitas ayuda con este proyecto, no dudes en contactarme, Guido Delponte, a través de mi linkedIn: [linkedin.com/in/gdelponte](https://www.linkedin.com/in/guido-delponte/).