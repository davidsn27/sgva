# 🚀 Guía de Integración - SGVA 3.0

Este documento describe cómo integrar y ejecutar todas las características avanzadas de SGVA.

## ✅ Estado Actual

Todas las características han sido implementadas y las migraciones aplicadas:

- ✅ OAuth2 (Google/Microsoft)
- ✅ Notificaciones por Email (Celery)
- ✅ Sistema de Calificaciones
- ✅ CI/CD (GitHub Actions)
- ✅ Sentry (Error Tracking)
- ✅ Analytics (Dashboard)

## 📋 Guía Paso a Paso

### 1. Setup Inicial

```bash
# Crear ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores
```

### 2. Variables de Entorno (.env)

```env
# Django
DEBUG=True
SECRET_KEY=tu-secret-key-aqui
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3
# O para PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/sgva

# Email (Gmail)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password  # NO tu contraseña normal

# OAuth2 - Google
GOOGLE_CLIENT_ID=xxxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxxxx

# OAuth2 - Microsoft
MICROSOFT_CLIENT_ID=xxxxx
MICROSOFT_CLIENT_SECRET=xxxxx

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Sentry
SENTRY_DSN=https://xxxxx@xxxxx.ingest.sentry.io/xxxxx
ENVIRONMENT=development  # o 'production'

# Redis
REDIS_URL=redis://localhost:6379/0
```

### 3. Configurar OAuth2

#### Google OAuth2

1. Ir a https://console.cloud.google.com
2. Crear nuevo proyecto
3. Habilitar "Google+ API"
4. Ir a "Credentials"
5. Crear "OAuth 2.0 Client ID"
6. Agregar redirect URI: `http://localhost:8000/accounts/google/login/callback/`
7. Copiar Client ID y Secret

**En Django Admin:**
```
http://localhost:8000/admin/

Socialaccount > Social Applications > Add
- Provider: Google
- Name: Google
- Client ID: [Tu Client ID]
- Secret: [Tu Secret]
- Sites: Seleccionar el sitio actual
```

#### Microsoft OAuth2

1. Ir a https://portal.azure.com
2. Azure Active Directory > App registrations > New registration
3. Nombre: SGVA
4. Redirect URI: `http://localhost:8000/accounts/microsoft/login/callback/`
5. Copiar Application ID
6. Ir a "Certificates & secrets" y crear nuevo Client Secret

**En Django Admin:**
```
Socialaccount > Social Applications > Add
- Provider: Microsoft Graph
- Name: Microsoft
- Client ID: [Application ID]
- Secret: [Client Secret]
- Sites: Seleccionar el sitio actual
```

### 4. Configurar Email (Gmail)

1. Ir a https://myaccount.google.com/security
2. Habilitar "2-Step Verification"
3. Generar "App Password"
4. Copiar contraseña en EMAIL_HOST_PASSWORD

### 5. Iniciar Servicios

**Terminal 1: Django**
```bash
python manage.py runserver
# http://localhost:8000
```

**Terminal 2: Celery Worker**
```bash
celery -A sgva worker -l info
```

**Terminal 3: Celery Beat (Scheduler)**
```bash
celery -A sgva beat -l info
```

**Terminal 4: Redis** (si no está en Docker)
```bash
redis-server
```

O con Docker:
```bash
docker-compose up -d
```

### 6. Crear Superuser

```bash
python manage.py createsuperuser
# Username: admin
# Email: admin@example.com
# Password: [Tu contraseña]
```

### 7. Acceso a Servicios

```
Web App:
  http://localhost:8000

Admin Panel:
  http://localhost:8000/admin

API REST:
  http://localhost:8000/api/

API Docs (Swagger):
  http://localhost:8000/api/docs/

API Docs (ReDoc):
  http://localhost:8000/api/redoc/

OAuth2 Login:
  http://localhost:8000/accounts/login/
```

---

## 🔌 Endpoints de API

### Calificaciones

```bash
# Crear calificación
POST /api/calificaciones/
{
  "postulacion": 1,
  "tipo": "EMPRESA_A_APRENDIZ",
  "puntuacion": 5,
  "comentario": "Excelente trabajo"
}

# Listar mis calificaciones
GET /api/calificaciones/mis_calificaciones/

# Listar calificaciones recibidas
GET /api/calificaciones/calificaciones_recibidas/

# Mi promedio
GET /api/promedios/mi_promedio/
```

### Analytics

```bash
# Resumen general
GET /api/analytics/resumen/

# Postulaciones por estado
GET /api/analytics/postulaciones-por-estado/

# Tendencia (últimos 30 días)
GET /api/analytics/tendencia/?dias=30

# Top empresas
GET /api/analytics/top-empresas/

# Aprendices exitosos
GET /api/analytics/aprendices-exitosos/

# Salud del sistema
GET /api/analytics/salud-sistema/
```

---

## 📊 Celery Tasks

Las siguientes tareas están programadas automáticamente:

```python
# Recordar postulaciones vencidas
# Cada día a las 9:00 AM

# Limpiar postulaciones vencidas
# Cada día a las 00:00 (medianoche)

# Enviar emails:
# - Postulación enviada (inmediato)
# - Cambio de estado (inmediato)
# - Nueva postulación empresa (inmediato)
```

### Ejecutar tasks manualmente

```bash
python manage.py shell

from plataforma.tasks import enviar_email_postulacion

# Ejecutar inmediato
enviar_email_postulacion(
    aprendiz_email='test@example.com',
    aprendiz_nombre='Juan',
    empresa_nombre='Tech Corp'
)

# O con delay
enviar_email_postulacion.delay(
    aprendiz_email='test@example.com',
    aprendiz_nombre='Juan',
    empresa_nombre='Tech Corp'
)
```

---

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=plataforma --cov-report=html

# Test específico
pytest plataforma/tests/test_api.py::TestCalificaciones -v

# Con output verbose
pytest -v -s
```

---

## 🔍 Debugging

### Verificar estado de Celery

```bash
# Listar tasks activas
celery -A sgva inspect active

# Estadísticas
celery -A sgva inspect stats

# Workers registrados
celery -A sgva inspect registered
```

### Verificar conexión Redis

```bash
redis-cli ping
# Debe responder: PONG

redis-cli keys '*'
# Ver todas las keys
```

### Verificar Sentry

En código:
```python
import sentry_sdk

# Enviar evento de prueba
sentry_sdk.capture_message("Test message")

# Simular excepción
raise Exception("Test exception")
```

---

## 🚀 Deploy a Producción

### Con Docker

```bash
# Build
docker-compose build

# Ejecutar migraciones
docker-compose run django python manage.py migrate

# Crear superuser
docker-compose run django python manage.py createsuperuser

# Iniciar
docker-compose up -d
```

### Manual en Servidor

```bash
# Clone repo
git clone <repo> /app
cd /app

# Setup venv
python -m venv venv
source venv/bin/activate

# Instalar
pip install -r requirements.txt

# Configurar .env
nano .env

# Migraciones
python manage.py migrate

# Static files
python manage.py collectstatic --noinput

# Gunicorn + Nginx
gunicorn sgva.wsgi:application --bind 0.0.0.0:8000

# Celery en background
celery -A sgva worker -l info --detach
celery -A sgva beat -l info --detach
```

---

## 🆘 Solución de Problemas

### Email no se envía

- Verificar EMAIL_HOST_PASSWORD (app password, no contraseña normal)
- Verificar que gmail tenga 2FA habilitado
- Revisar logs de Celery: `celery -A sgva worker -l debug`
- En desarrollo, cambiar a: `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend`

### OAuth2 no funciona

- Verificar que los redirect URIs en Google/Microsoft coincidan
- Comprobar que GOOGLE_CLIENT_ID y GOOGLE_CLIENT_SECRET estén en .env
- Ir a Admin > Social Applications y verificar que estén configuradas
- Limpiar cookies del navegador

### Celery no procesa tasks

- Verificar que Redis esté corriendo: `redis-cli ping`
- Revisar logs del worker: `celery -A sgva worker -l debug`
- Verificar CELERY_BROKER_URL en .env
- Reiniciar: `pkill -f celery`

### Analytics no muestra datos

- Ejecutar actualización manual: `python manage.py shell < script_actualizar_stats.py`
- Verificar que Postulacion tenga datos
- Revisar logs de Django: `DEBUG=True`

---

## 📚 Recursos Útiles

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Django Allauth](https://django-allauth.readthedocs.io/)
- [Celery](https://docs.celeryproject.io/)
- [Sentry Django](https://docs.sentry.io/platforms/python/integrations/django/)
- [drf-spectacular](https://drf-spectacular.readthedocs.io/)

---

**Versión**: 3.0.0  
**Fecha**: Febrero 2026  
**Status**: Producción Ready ✅

Para soporte: [Tu contacto aquí]
