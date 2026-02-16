# 🚀 SGVA 3.0 - Características Avanzadas

## 📋 Tabla de Contenidos

1. [OAuth2 - Google & Microsoft](#oauth2-google--microsoft)
2. [Notificaciones por Email](#notificaciones-por-email)
3. [Sistema de Calificaciones](#sistema-de-calificaciones)
4. [CI/CD con GitHub Actions](#cicd-con-github-actions)
5. [Sentry - Monitoreo de Errores](#sentry---monitoreo-de-errores)
6. [Dashboard de Analytics](#dashboard-de-analytics)

---

## 🔐 OAuth2 - Google & Microsoft

### Setup Google OAuth

1. **Crear aplicación en Google Cloud:**
   - Ir a https://console.cloud.google.com
   - Crear nuevo proyecto
   - Habilitar "Google+ API"
   - Crear credenciales (OAuth 2.0 Client ID)
   - Copiar Client ID y Secret

2. **Configurar en Django:**
   ```python
   # En admin: http://localhost:8000/admin/
   # Socialaccount > Social Applications > Agregar
   # - Provider: Google
   # - Name: Google
   # - Client ID: Tu_Client_ID
   # - Secret: Tu_Secret
   ```

3. **Usar en template:**
   ```html
   {% load socialaccount %}
   <a href="{% provider_login_url 'google' %}">Login con Google</a>
   ```

### Setup Microsoft OAuth

1. **Crear aplicación en Azure:**
   - Ir a https://portal.azure.com
   - Azure Active Directory > App registrations
   - Crear "New registration"
   - Agregar "Redirect URI": `http://localhost:8000/accounts/microsoft/login/callback/`
   - Copiar Application ID y Secret

2. **Configurar en Django:**
   ```python
   # En admin crear Social Application:
   # - Provider: Microsoft Graph
   # - Name: Microsoft
   # - Client ID: Application_ID
   # - Secret: Client_Secret
   ```

### URLs disponibles

```
/accounts/login/              - Login
/accounts/signup/             - Signup
/accounts/logout/             - Logout
/accounts/google/login/       - Login Google
/accounts/microsoft/login/    - Login Microsoft
/accounts/profile/            - Editar perfil social
```

---

## 📧 Notificaciones por Email

### Configuración SMTP

```env
# .env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
DEFAULT_FROM_EMAIL=tu-email@gmail.com
```

### Tareas de Email (Celery)

```python
# Tareas disponibles
from plataforma.tasks import (
    enviar_email_postulacion,
    enviar_email_cambio_estado,
    enviar_email_empresa_nueva_postulacion,
    recordar_postulaciones_vencidas,
    limpiar_postulaciones_vencidas,
)

# Usar en código
enviar_email_postulacion.delay(
    aprendiz_email='aprendiz@test.com',
    aprendiz_nombre='Juan',
    empresa_nombre='Tech Corp'
)
```

### Ejecutar Celery

```bash
# Worker
celery -A sgva worker -l info

# Beat (Scheduler)
celery -A sgva beat -l info

# Con Docker
docker-compose up celery celery-beat
```

---

## ⭐ Sistema de Calificaciones

### Modelos

```
Calificacion
├── postulacion (FK)
├── tipo (EMPRESA_A_APRENDIZ | APRENDIZ_A_EMPRESA)
├── calificador (FK User)
├── puntuacion (1-5)
└── comentario

PromedioCalificacion
├── aprendiz (FK)
├── empresa (FK)
├── promedio (decimal)
└── total_calificaciones
```

### API Endpoints

```
POST   /api/calificaciones/           - Crear calificación
GET    /api/calificaciones/           - Listar
GET    /api/calificaciones/{id}/      - Detalle
PUT    /api/calificaciones/{id}/      - Actualizar
DELETE /api/calificaciones/{id}/      - Eliminar
GET    /api/calificaciones/mis_calificaciones/         - Mis calificaciones
GET    /api/calificaciones/calificaciones_recibidas/   - Recibidas

GET    /api/promedios/                - Listar promedios
GET    /api/promedios/mi_promedio/    - Mi promedio
```

### Ejemplo de uso

```bash
curl -X POST http://localhost:8000/api/calificaciones/ \
  -H "Authorization: Bearer tu_token" \
  -H "Content-Type: application/json" \
  -d '{
    "postulacion": 1,
    "tipo": "EMPRESA_A_APRENDIZ",
    "puntuacion": 5,
    "comentario": "Excelente desempeño"
  }'
```

---

## 🔄 CI/CD con GitHub Actions

### Workflows Incluidos

#### 1. **tests.yml** - Tests automáticos

```yaml
# Ejecuta en:
# - Push a main/develop
# - Pull requests a main/develop

# Incluye:
- Tests con pytest
- Linting (flake8, black, isort)
- Análisis de seguridad (bandit, safety)
- Coverage con Codecov
- Soporte Python 3.11, 3.12
- PostgreSQL + Redis en test
```

#### 2. **deploy.yml** - Deploy a producción

```yaml
# Ejecuta en:
# - Push a main (automático)
# - Manual (workflow_dispatch)

# Incluye:
- Deploy a servidor via SSH
- Docker rebuild
- Notificación en Slack
```

### Configurar secrets en GitHub

```
Settings > Secrets > New repository secret

DEPLOY_KEY=      # SSH private key
DEPLOY_HOST=     # IP/Domain del servidor
DEPLOY_USER=     # Usuario SSH
SLACK_WEBHOOK=   # URL webhook Slack
```

### Ejecutar Tests Localmente

```bash
# Todos los tests
pytest

# Con cobertura
pytest --cov=plataforma --cov-report=html

# Test específico
pytest plataforma/tests/test_api.py::TestAprendizAPI::test_list_aprendices -v

# Con markers
pytest -m integration
```

---

## 🚨 Sentry - Monitoreo de Errores

### Setup Sentry

1. **Crear cuenta:**
   - https://sentry.io

2. **Crear proyecto Django**
   - Copiar DSN

3. **Configurar en .env:**
   ```env
   SENTRY_DSN=https://xxxxx@xxxxx.ingest.sentry.io/xxxxx
   ENVIRONMENT=production
   ```

### Usar Sentry en código

```python
from plataforma.sentry_utils import crear_sentry_context, capture_exception_con_contexto

# En vistas
def mi_vista(request):
    crear_sentry_context(request.user, {
        'postulacion_id': 123,
        'accion': 'cambiar_estado'
    })
    
    try:
        # Tu código
        resultado = hacer_algo()
    except Exception as e:
        capture_exception_con_contexto(e, {
            'usuario': request.user.username,
            'url': request.path,
        })
        raise
```

### Características

- ✅ Captura automática de excepciones
- ✅ Integración con Celery
- ✅ Integración con Redis
- ✅ Contexto de usuario automático
- ✅ Stack traces completos
- ✅ Alertas configurables

---

## 📊 Dashboard de Analytics

### API Endpoints

```
GET /api/analytics/resumen/              - KPIs generales
GET /api/analytics/postulaciones-por-estado/
GET /api/analytics/tendencia/?dias=30    - Tendencia temporal
GET /api/analytics/top-empresas/         - Top 10 empresas
GET /api/analytics/aprendices-exitosos/  - Aprendices con éxito
GET /api/analytics/salud-sistema/        - Estado sistema
```

### Respuesta ejemplo

```json
{
  "usuarios": {
    "total_aprendices": 50,
    "total_empresas": 20,
    "aprendices_activos": 45,
    "empresas_activas": 18
  },
  "postulaciones": {
    "total": 500,
    "este_mes": 120,
    "seleccionados": 85,
    "rechazados": 45,
    "pendientes": 370,
    "tasa_conversion": 17.00
  },
  "fecha_reporte": "2026-02-06"
}
```

### Métricas incluidas

- **Usuarios**: Total, activos, nuevos
- **Postulaciones**: Por estado, tendencia, tasa conversión
- **Top Empresas**: Por cantidad de postulaciones y tasa aceptación
- **Aprendices Exitosos**: Con más selecciones
- **Salud del Sistema**: Actividad, transacciones

### Actualizar estadísticas

```python
# En manage.py shell o Celery task
from plataforma.models_analytics import EstadisticaDiaria
EstadisticaDiaria.actualizar_hoy()
```

---

## 📝 Guía Rápida de Setup Completo

### Instalación

```bash
# 1. Clonar e instalar
git clone <url>
cd sgva_web
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Configurar variables
cp .env.example .env
# Editar .env con valores reales

# 3. Migrar BD
python manage.py migrate

# 4. Crear admin
python manage.py createsuperuser

# 5. Cargar datos prueba
python manage.py shell < seed_data.py

# 6. Iniciar servicios
# Terminal 1: Django
python manage.py runserver

# Terminal 2: Celery Worker
celery -A sgva worker -l info

# Terminal 3: Celery Beat
celery -A sgva beat -l info

# Terminal 4: Redis (si no está en docker)
redis-server
```

### Con Docker

```bash
docker-compose up --build

# Acceso
http://localhost:80        # Aplicación
http://localhost:8000      # Django dev
```

---

## 🔗 URLs Importantes

| URL | Descripción |
|-----|-------------|
| `/admin/` | Panel administrativo |
| `/api/docs/` | Swagger UI |
| `/api/redoc/` | ReDoc |
| `/accounts/login/` | Login |
| `/accounts/logout/` | Logout |
| `/api/calificaciones/` | API Calificaciones |
| `/api/analytics/resumen/` | Dashboard |

---

## 🎯 Próximos pasos

1. **Notificaciones push** - OneSignal o FCM
2. **Frontend React** - Dashboard interactivo
3. **Mobile app** - React Native
4. **Machine Learning** - Recomendaciones
5. **Internacionalización** - Multi idioma
6. **Marketplace** - Freelancers

---

**Versión**: 3.0.0  
**Fecha**: Febrero 2026  
**Estado**: Producción Ready ✅
