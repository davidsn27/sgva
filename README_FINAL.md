# 📊 SGVA 3.0 - Sistema de Gestión de Vinculación de Aprendices

**Versión**: 3.0.0 | **Estado**: Production Ready ✅ | **Fecha**: Febrero 2026

---

## 🎯 Resumen Ejecutivo

SGVA es una plataforma integral de gestión de oportunidades de formación que conecta aprendices del SENA con empresas oferentes. La versión 3.0 introduce características empresariales avanzadas para un sistema completamente escalable y monitoreado.

### ✨ Características Principales

#### Core Plataforma
- ✅ Gestión de Aprendices con CRUD completo
- ✅ Gestión de Empresas con perfiles y requisitos
- ✅ Sistema de Postulaciones bidireccional
- ✅ Historial de cambios automático
- ✅ Dashboard de reportes

#### Versión 3.0 - Nuevas Características
- ✅ **API REST** con 18+ endpoints
- ✅ **WebSockets** para notificaciones en tiempo real
- ✅ **OAuth2** (Google + Microsoft)
- ✅ **Celery** para tareas asincrónicas
- ✅ **Sistema de Calificaciones** (aprendiz ⭐ empresa)
- ✅ **Dashboard Analytics** con 6+ métricas
- ✅ **Docker** para conteneurización
- ✅ **GitHub Actions** CI/CD
- ✅ **Sentry** para monitoreo de errores
- ✅ **Swagger/OpenAPI** documentación automática

---

## 🏗️ Arquitectura Técnica

### Stack Tecnológico

```
Frontend:
  ├─ HTML5/CSS3/JavaScript
  ├─ Django Templates
  └─ (Opcional) React/Vue.js

Backend:
  ├─ Django 5.2.11
  ├─ Django REST Framework 3.16.1
  ├─ Django Channels 4.3.2 (WebSockets)
  ├─ Celery 5.6.2 (Async Tasks)
  ├─ django-allauth 65.14.0 (OAuth2)
  └─ drf-spectacular 0.29.0 (OpenAPI)

Infraestructura:
  ├─ PostgreSQL 15 (BD Producción)
  ├─ Redis 7.1.0 (Cache/Broker)
  ├─ Nginx (Reverse Proxy)
  ├─ Gunicorn (WSGI Server)
  └─ Docker Compose (Orquestación)

Monitoreo:
  ├─ Sentry 2.52.0 (Error Tracking)
  ├─ pytest 9.0.2 (Testing)
  └─ GitHub Actions (CI/CD)
```

### Modelo de Datos

```
Perfil
 └─ Usuario (Django Auth)
     ├─ Aprendiz
     │   ├─ Ficha
     │   ├─ Programa de Formación
     │   ├─ Estado (ACTIVO, INACTIVO, EGRESADO)
     │   └─ Postulaciones
     │
     ├─ Empresa
     │   ├─ Descripción
     │   ├─ Contacto
     │   ├─ Estado (ACTIVA, INACTIVA)
     │   └─ Oportunidades
     │
     └─ Funcionario (Staff Django)
         └─ Permisos administrativos

Postulacion
 ├─ Aprendiz (FK)
 ├─ Empresa (FK)
 ├─ Estado (PENDIENTE, SELECCIONADO, RECHAZADO, VENCIDO)
 ├─ Respuesta Aprendiz
 ├─ Historial Cambios
 └─ Calificaciones

Calificacion
 ├─ Postulacion (FK)
 ├─ Tipo (EMPRESA→APRENDIZ, APRENDIZ→EMPRESA)
 ├─ Puntuación (1-5 estrellas)
 └─ Comentario

EstadisticaDiaria
 ├─ Usuarios (Total, Activos)
 ├─ Postulaciones (Por Estado, Tendencia)
 └─ Tasa de Conversión
```

---

## 🚀 Inicio Rápido

### Requisitos
- Python 3.11+
- PostgreSQL 15+ (o SQLite para dev)
- Redis 7+ 
- Docker & Docker Compose (opcional)

### Instalación (5 minutos)

```bash
# 1. Clonar repositorio
git clone <url>
cd sgva_web

# 2. Crear ambiente
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables
cp .env.example .env
# Editar .env con tus valores (ver INTEGRACION_FEATURES.md)

# 5. Ejecutar migraciones
python manage.py migrate

# 6. Crear superuser
python manage.py createsuperuser

# 7. Iniciar servidor
python manage.py runserver
```

**Acceso:**
- App: http://localhost:8000
- Admin: http://localhost:8000/admin
- API Docs: http://localhost:8000/api/docs/

---

## 🔌 API REST Endpoints

### Autenticación

```
POST   /api/auth/token/               - Obtener token JWT
POST   /api/auth/refresh/             - Refrescar token
POST   /accounts/logout/              - Logout
POST   /accounts/login/               - Login tradicional
POST   /accounts/signup/              - Registrarse
POST   /accounts/google/login/        - Login con Google
POST   /accounts/microsoft/login/     - Login con Microsoft
```

### Aprendices

```
GET    /api/aprendices/               - Listar aprendices
POST   /api/aprendices/               - Crear aprendiz
GET    /api/aprendices/{id}/          - Obtener aprendiz
PUT    /api/aprendices/{id}/          - Actualizar aprendiz
DELETE /api/aprendices/{id}/          - Eliminar aprendiz
GET    /api/aprendices/{id}/postulaciones/ - Mis postulaciones
```

### Empresas

```
GET    /api/empresas/                 - Listar empresas
POST   /api/empresas/                 - Crear empresa
GET    /api/empresas/{id}/            - Obtener empresa
PUT    /api/empresas/{id}/            - Actualizar empresa
DELETE /api/empresas/{id}/            - Eliminar empresa
```

### Postulaciones

```
GET    /api/postulaciones/            - Listar postulaciones
POST   /api/postulaciones/            - Crear postulación
GET    /api/postulaciones/{id}/       - Obtener postulación
PUT    /api/postulaciones/{id}/       - Cambiar estado
GET    /api/postulaciones/resumen/    - Resumen por estado
```

### Calificaciones

```
POST   /api/calificaciones/           - Crear calificación
GET    /api/calificaciones/           - Listar
GET    /api/calificaciones/mis_calificaciones/     - Mis ratings
GET    /api/calificaciones/calificaciones_recibidas/ - Ratings recibidos
GET    /api/promedios/mi_promedio/    - Mi promedio
```

### Analytics

```
GET    /api/analytics/resumen/            - KPIs generales
GET    /api/analytics/postulaciones-por-estado/  - Gráfico estados
GET    /api/analytics/tendencia/?dias=30 - Línea temporal
GET    /api/analytics/top-empresas/      - Ranking empresas
GET    /api/analytics/aprendices-exitosos/ - Aprendices destacados
GET    /api/analytics/salud-sistema/      - Health check
```

---

## 📨 Email & Notificaciones

### Emails Automáticos (Celery)

1. **Postulación Enviada** - Al aprendiz inmediatamente
2. **Cambio de Estado** - Notifica cambios (seleccionado/rechazado)
3. **Nueva Postulación** - A la empresa cuando recibe aplicación
4. **Recordatorio Vencimiento** - Diario a las 9 AM

### Notificaciones en Tiempo Real (WebSocket)

```javascript
// Conectar a WebSocket
const socket = new WebSocket(
  'ws://localhost:8000/ws/notificaciones/'
);

socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Nueva notificación:', data);
  // {
  //   type: 'postulacion_nueva',
  //   empresa: 'Tech Corp',
  //   aprendiz: 'Juan Pérez'
  // }
};
```

---

## 🔍 Monitoreo & Debugging

### Celery Tasks

```bash
# Ver tasks activas
celery -A sgva inspect active

# Ver worker stats
celery -A sgva inspect stats

# Limpiar queue (¡cuidado!)
celery -A sgva purge
```

### Sentry Dashboard

- URL: https://sentry.io
- Monitorea automáticamente:
  - Excepciones en Django
  - Errores en Celery tasks
  - Performance (P95, P99)
  - User feedback

### Logs

```bash
# Django
tail -f logs/django.log

# Celery Worker
tail -f logs/celery.log

# Celery Beat
tail -f logs/beat.log

# Nginx (Docker)
docker-compose logs -f nginx
```

---

## 🧪 Testing

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Con cobertura
pytest --cov=plataforma --cov-report=html

# Test específico
pytest plataforma/tests/test_api.py::TestAprendizAPI -v

# Con markers
pytest -m slow
pytest -m fast
```

### Coverage Report

```bash
# Generar reporte HTML
pytest --cov=plataforma --cov-report=html
open htmlcov/index.html
```

---

## 🐳 Docker Deployment

### Desarrollo

```bash
# Build & ejecutar
docker-compose up --build

# Migraciones
docker-compose exec django python manage.py migrate

# Crear superuser
docker-compose exec django python manage.py createsuperuser

# Acceso:
# App: http://localhost
# Admin: http://localhost/admin
# API: http://localhost/api/
```

### Producción

```yaml
# docker-compose.prod.yml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: sgva
      POSTGRES_PASSWORD: secure-password
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

  django:
    image: sgva:latest
    environment:
      DEBUG: "False"
      ALLOWED_HOSTS: tu-dominio.com
      DATABASE_URL: postgresql://...
    depends_on:
      - postgres
      - redis

  celery:
    image: sgva:latest
    command: celery -A sgva worker -l info

  celery-beat:
    image: sgva:latest
    command: celery -A sgva beat -l info

  nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.prod.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro

volumes:
  pgdata:
```

```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## 📊 Métricas & KPIs

### Dashboard Analytics

| Métrica | API | Descripción |
|---------|-----|-------------|
| Total Usuarios | `/api/analytics/resumen/` | Aprendices + Empresas |
| Postulaciones/Mes | `/api/analytics/resumen/` | Cantidad mensual |
| Tasa Conversión | `/api/analytics/resumen/` | % seleccionados |
| Top Empresas | `/api/analytics/top-empresas/` | Por # postulaciones |
| Aprendices Exitosos | `/api/analytics/aprendices-exitosos/` | Con + selecciones |
| Salud Sistema | `/api/analytics/salud-sistema/` | Usuarios activos |

### Actualizar Estadísticas

```bash
# Manual
python actualizar_estadisticas.py

# O en shell
python manage.py shell
>>> from actualizar_estadisticas import actualizar_estadisticas
>>> actualizar_estadisticas()
```

---

## 🔐 Seguridad

### HTTPS/SSL

```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
}
```

### CSRF Protection

Todos los POST/PUT/DELETE requieren CSRF token:

```html
<!-- En templates Django -->
<form method="POST">
  {% csrf_token %}
  <!-- campos -->
</form>
```

### Rate Limiting (API)

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}
```

### Permisos

```python
# Solo propietario puede editar
permission_classes = [IsAuthenticated, IsOwner]

# Solo admin
permission_classes = [IsAdminUser]

# Basado en roles
@permission_required('plataforma.view_aprendiz')
def vista(request):
    pass
```

---

## 🚀 Next Steps & Roadmap

### Próximas Versiones

- **v3.1** - Notificaciones Push (FCM)
- **v3.2** - Machine Learning (Recomendaciones)
- **v4.0** - Mobile App (React Native)
- **v4.1** - Marketplace de Servicios
- **v5.0** - Internacionalización

### Mejoras Planeadas

- [ ] Sistema de Contratos digitales
- [ ] Video entrevistas integradas
- [ ] Pruebas técnicas automáticas
- [ ] Portal de empresas avanzado
- [ ] Mobile responsive mejorado
- [ ] Multi-idioma (ES/EN/PT)

---

## 📞 Soporte

### Contacto

- 📧 Email: soporte@sgva.com
- 💬 Chat: discord.com/invite/sgva
- 📱 WhatsApp: +57 3XX XXX XXXX
- 🐛 Issues: github.com/sgva/sgva-web/issues

### Documentación

- [Guía Integración Features](./INTEGRACION_FEATURES.md)
- [Características Avanzadas](./CARACTERISTICAS_AVANZADAS.md)
- [API Documentation](http://localhost:8000/api/docs/)
- [GitHub Wiki](https://github.com/sgva/sgva-web/wiki)

---

## 📝 Licencia

Este proyecto está bajo licencia MIT. Consulta [LICENSE](./LICENSE) para más detalles.

---

**Desarrollado con ❤️ para el SENA**

**Última actualización**: Febrero 2026  
**Versión actual**: 3.0.0  
**Status**: Production Ready ✅
