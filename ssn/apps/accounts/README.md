# Accounts App - Sistema de Autenticación Flexible

La app `accounts` proporciona un sistema de autenticación flexible para el sistema SSN que soporta múltiples backends de autenticación.

## Características

- ✅ **Autenticación Flexible**: Soporta tanto autenticación local (Django) como servicio externo de identidad
- ✅ **Modelo de Usuario Personalizado**: Extiende AbstractUser con campos adicionales
- ✅ **Email como Identificador Principal**: Los usuarios se autentican con su email en lugar de username
- ✅ **Integración con Servicio de Identidad**: Sincronización automática de usuarios desde FastAPI identidad service
- ✅ **Decoradores de Protección**: Tools para proteger vistas con `@login_required`, `@permission_required`, etc.
- ✅ **Sistema de Sesiones**: Gestión de sesiones con soporte para "recuérdame"
- ✅ **Interfaz Admin Personalizada**: Admin mejorado para gestión de usuarios
- ✅ **Templates Responsivos**: Interfaz de login con Tailwind CSS

## Configuración

### Modelo Automático: Una Variable

El sistema **detecta automáticamente** el modo de autenticación basándose en una sola variable:

#### 🔵 IDENTITY_SERVICE_URL está vacía o no configurada → Autenticación Local

```bash
# .env
# No configurar IDENTITY_SERVICE_URL (o dejarla vacía)

# Django usa su base de datos local
python manage.py createsuperuser
```

**Perfecto para:**
- Desarrollo local
- Testing
- Interior de la empresa sin servicio centralizado

#### 🟢 IDENTITY_SERVICE_URL tiene un valor → Servicio de Identidad Externo

```bash
# .env
IDENTITY_SERVICE_URL=http://python_fastapi_identidad:8000
IDENTITY_SERVICE_VERIFY_SSL=True  # False para dev con certs self-signed
```

**Perfecto para:**
- Producción
- Múltiples servicios compartiendo usuarios
- LDAP/Active Directory integrado

### Instalación Inicial

1. **Crear migraciones** (la primera vez o si cambiaste models.py):
   ```bash
   python manage.py makemigrations accounts
   python manage.py migrate accounts
   ```
   
   ⚠️ **Nota sobre migraciones:**
   - Incluso si usas servicio externo, Django sincroniza usuarios localmente
   - La tabla de usuarios es necesaria para sesiones y datos locales
   - Las migraciones solo crean la tabla de usuarios, nada más

2. **Modo Local: Crear superusuario**:
   ```bash
   python manage.py createsuperuser
   ```

3. **Modo Identity Service: Ya está configurado**:
   - Solo necesitas que los usuarios estén registrados en el servicio
   - Django los sincroniza automáticamente en primer login

## Uso

### Proteger Vistas

#### Con Decoradores (Function-Based Views)

```python
from django.shortcuts import render
from accounts.middleware import login_required, permission_required, role_required

@login_required
def my_protected_view(request):
    """Solo usuarios autenticados pueden acceder."""
    return render(request, 'my_template.html')

@permission_required('operaciones.view_operacion')
def admin_view(request):
    """Requiere permiso específico."""
    return render(request, 'admin.html')

@role_required('admin')
def admin_only_view(request):
    """Solo administradores."""
    return render(request, 'admin_page.html')
```

#### Con Mixins (Class-Based Views)

```python
from django.views.generic import TemplateView
from accounts.middleware import LoginRequiredMixin, PermissionRequiredMixin

class ProtectedView(LoginRequiredMixin, TemplateView):
    """Requiere autenticación."""
    template_name = 'protected.html'

class AdminView(PermissionRequiredMixin, TemplateView):
    """Requiere permiso específico."""
    template_name = 'admin.html'
    permission_required = 'operaciones.view_operacion'
```

### Usar el Modelo de Usuario

```python
from django.contrib.auth import get_user_model

User = get_user_model()

# Crear usuario local
user = User.objects.create_user(
    email='test@example.com',
    password='securepass123',
    first_name='Juan',
    last_name='Pérez'
)

# Obtener usuario por email
user = User.objects.get(email='test@example.com')

# Chequear si es usuario externo
if user.is_external_user:
    print(f"User managed by identity service: {user.external_id}")
```

### Usar el Servicio de Autenticación

```python
from accounts.services import AuthenticationService

auth_service = AuthenticationService()

# Autenticar usuario
user = auth_service.authenticate('test@example.com', 'password123')

if user:
    print(f"✅ User authenticated: {user.email}")
    print(f"Last login via: {user.last_login_via}")
else:
    print("❌ Authentication failed")

# Obtener o crear usuario local
user = auth_service.get_or_create_user(
    email='newuser@example.com',
    first_name='Juan',
    last_name='Pérez'
)
```

## Endpoints

### URLs Públicas

- `GET /accounts/login/` - Página de login
- `POST /accounts/login/` - Procesar login
- `GET /accounts/logout/` - Logout
- `POST /accounts/logout-all/` - Logout de todos los dispositivos (requiere autenticación)

### URLs Protegidas

- `GET /accounts/profile/` - Perfil del usuario (requiere autenticación)

## Estructura de Carpetas

```
accounts/
├── __init__.py
├── apps.py              # Configuración de la app
├── models.py            # Modelo User personalizado
├── forms.py             # Formularios de login
├── views.py             # Vistas de autenticación
├── urls.py              # URLs de la app
├── backends.py          # Backends de autenticación
├── services.py          # Servicios de autenticación
├── middleware.py        # Decoradores y mixins
├── signals.py           # Señales de Django
├── admin.py             # Configuración admin
├── tests.py             # Tests
├── migrations/          # Migraciones de BD
└── templates/
    └── accounts/
        ├── login.html      # Página de login
        └── profile.html    # Perfil del usuario
```

## Modelo de Usuario

El modelo `User` extiende `AbstractUser` de Django con campos adicionales:

```python
class User(AbstractUser):
    # Campos principales
    uuid              # UUID único (para sistemas distribuidos)
    email             # Email (heredado, usado como USERNAME_FIELD)
    
    # Integración con servicio externo
    external_id       # ID del servicio de identidad
    is_external_user  # Flag si es usuario externo
    identity_service_token         # JWT token del servicio
    identity_service_token_obtained_at  # Timestamp del token
    
    # Metadatos
    last_login_via    # Método de autenticación último
    is_active         # Usuario activo
    created_at        # Timestamp de creación
    updated_at        # Timestamp de actualización
```

## Base de Datos

### Tabla Principal

La tabla de usuarios se crea automáticamente con:
- Índices en `email`, `uuid`, `external_id`, `is_active`
- Restricción UNIQUE en `email` y `uuid` (external_id es único pero permite NULL)

### Migraciones

```bash
# Crear migraciones después de cambios en models.py
python manage.py makemigrations accounts

# Aplicar migraciones
python manage.py migrate

# Ver estado de migraciones
python manage.py showmigrations accounts
```

## Logging

La app registra eventos de autenticación en el logger `accounts`:

```python
import logging
logger = logging.getLogger('accounts')

# Eventos logueados:
# ✅ Login exitoso
# ❌ Login fallido
# 📝 Nuevo usuario registrado
# 🔐 Servicio de identidad conectado
```

Configure en settings si desea capturar estos logs.

## Seguridad

- ✅ Contraseñas hasheadas con PBKDF2 (por defecto)
- ✅ CSRF protection en formularios
- ✅ Session security configurada
- ✅ Tokens JWT del servicio de identidad validados
- ✅ Email-based login (más seguro que username)

### Hardening en Producción

```python
# settings/prod.py
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
```

## Testing

Ejecuta los tests de la app:

```bash
# Correr todos los tests de accounts
python manage.py test accounts

# Test específico
python manage.py test accounts.tests.LoginViewTests

# Con verbosidad
python manage.py test accounts -v 2
```

## Troubleshooting

### Error: "AUTH_USER_MODEL refers to model 'accounts.User' that has not been installed"

Asegúrate que `accounts` esté en `INSTALLED_APPS` antes que otras apps que usen User.

### Error: "No such table: accounts_user"

Necesitas ejecutar migraciones:
```bash
python manage.py migrate
```

### Los logins no funcionan

1. Chequea que el usuario existe:
   ```bash
   python manage.py shell
   >>> from django.contrib.auth import get_user_model
   >>> User = get_user_model()
   >>> User.objects.filter(email='test@example.com').exists()
   ```

2. Si usas Identity Service, verifica que esté configurado:
   ```python
   from django.conf import settings
   identity_url = getattr(settings, 'IDENTITY_SERVICE_URL', '')
   print(f"Using identity service: {bool(identity_url.strip())}")
   print(f"URL: {identity_url}")
   ```

3. Chequea logs de autenticación:
   ```bash
   tail -f logs/ssn/accounts.log
   ```

## Ejemplos Avanzados

### Obtener datos del usuario actual en templates

```django
{% if user.is_authenticated %}
    <p>Bienvenido {{ user.get_full_name }}!</p>
    <p>Email: {{ user.email }}</p>
    <a href="{% url 'accounts:logout' %}">Logout</a>
{% else %}
    <a href="{% url 'accounts:login' %}">Login</a>
{% endif %}
```

### Proteger API REST endpoints

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_api_view(request):
    return Response({'message': f'Hello {request.user.email}'})
```

### Custom Permission Groups

```python
from django.contrib.auth.models import Group, Permission

# Crear grupo
group = Group.objects.create(name='Operadores')

# Asignar permisos
permission = Permission.objects.get(codename='add_operacion')
group.permissions.add(permission)

# Asignar usuario a grupo
user.groups.add(group)
```

## Documentación Relacionada

- [Django Authentication System](https://docs.djangoproject.com/en/5.1/topics/auth/)
- [Custom User Model](https://docs.djangoproject.com/en/5.1/topics/auth/customizing/#substituting-a-custom-user-model)
- [Decorators and Authentication](https://docs.djangoproject.com/en/5.1/topics/auth/default/#permissions-and-authorization)

## Contacto y Soporte

Para issues o preguntas sobre la app `accounts`:
1. Chequea este README
2. Ejecuta los tests: `python manage.py test accounts`
3. Revisa los logs: `logs/ssn/accounts.log`
4. Contacta a: soporte@compania.com
