# 🔌 Ejemplos de Uso de API SGVA 3.0

Esta guía muestra ejemplos prácticos de cómo usar todos los endpoints disponibles.

## 🔑 Autenticación

### 1. Login (Token)

```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "usuario@example.com",
    "password": "mi-contraseña"
  }'

# Respuesta:
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 2. Usar Token en Requests

```bash
# Guardar token
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Usar en header
curl -X GET http://localhost:8000/api/aprendices/ \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Refrescar Token

```bash
curl -X POST http://localhost:8000/api/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

---

## 👤 Aprendices

### Listar Aprendices

```bash
# Todos
curl http://localhost:8000/api/aprendices/

# Con paginación
curl "http://localhost:8000/api/aprendices/?page=1&page_size=10"

# Con búsqueda
curl "http://localhost:8000/api/aprendices/?search=Juan"

# Con filtro por estado
curl "http://localhost:8000/api/aprendices/?estado=ACTIVO"

# Ordenado
curl "http://localhost:8000/api/aprendices/?ordering=-id"
```

**Respuesta:**
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/aprendices/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "usuario": "juan.perez",
      "nombre_completo": "Juan Pérez",
      "correo": "juan@example.com",
      "numero_documento": "1234567890",
      "estado": "ACTIVO",
      "fecha_creacion": "2026-01-15T10:30:00Z",
      "postulaciones": 5,
      "postulaciones_exitosas": 2
    }
  ]
}
```

### Crear Aprendiz

```bash
curl -X POST http://localhost:8000/api/aprendices/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre_completo": "María García",
    "correo": "maria@example.com",
    "numero_documento": "9876543210",
    "estado": "ACTIVO",
    "ficha": 123456,
    "programa_formacion": "Desarrollo de Software"
  }'
```

### Obtener Aprendiz

```bash
curl http://localhost:8000/api/aprendices/1/
```

### Actualizar Aprendiz

```bash
curl -X PUT http://localhost:8000/api/aprendices/1/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "estado": "INACTIVO",
    "programa_formacion": "Diseño Gráfico"
  }'
```

### Eliminar Aprendiz

```bash
curl -X DELETE http://localhost:8000/api/aprendices/1/ \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🏢 Empresas

### Listar Empresas

```bash
curl http://localhost:8000/api/empresas/

# Con filtro
curl "http://localhost:8000/api/empresas/?estado=ACTIVA&search=Tech"
```

**Respuesta:**
```json
{
  "count": 50,
  "results": [
    {
      "id": 1,
      "nombre": "Tech Corp",
      "correo": "rh@techcorp.com",
      "telefono": "+57 123 456 7890",
      "ciudad": "Bogotá",
      "estado": "ACTIVA",
      "descripcion": "Empresa de tecnología...",
      "capacidad_cupos": 10,
      "fecha_creacion": "2026-01-10T08:00:00Z"
    }
  ]
}
```

### Crear Empresa

```bash
curl -X POST http://localhost:8000/api/empresas/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Innovatech",
    "correo": "rh@innovatech.com",
    "telefono": "+57 987 654 3210",
    "ciudad": "Medellín",
    "descripcion": "Empresa especializada en desarrollo web",
    "capacidad_cupos": 5,
    "estado": "ACTIVA"
  }'
```

---

## 📋 Postulaciones

### Listar Postulaciones

```bash
# Todas
curl http://localhost:8000/api/postulaciones/

# Mis postulaciones (requiere autenticación)
curl http://localhost:8000/api/postulaciones/mis_postulaciones/ \
  -H "Authorization: Bearer $TOKEN"

# Filtrar por estado
curl "http://localhost:8000/api/postulaciones/?estado=PENDIENTE"

# Resumen por estado
curl http://localhost:8000/api/postulaciones/resumen/
```

### Crear Postulación

```bash
curl -X POST http://localhost:8000/api/postulaciones/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "aprendiz": 1,
    "empresa": 5,
    "estado": "PENDIENTE"
  }'
```

### Cambiar Estado de Postulación

```bash
curl -X PUT http://localhost:8000/api/postulaciones/10/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "estado": "SELECCIONADO",
    "aprendiz_dio_respuesta": true,
    "respuesta_aprendiz": true
  }'
```

---

## ⭐ Calificaciones (v3.0)

### Crear Calificación

```bash
curl -X POST http://localhost:8000/api/calificaciones/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "postulacion": 1,
    "tipo": "EMPRESA_A_APRENDIZ",
    "puntuacion": 5,
    "comentario": "Excelente desempeño en el proyecto"
  }'

# Respuesta:
{
  "id": 1,
  "postulacion": 1,
  "tipo": "EMPRESA_A_APRENDIZ",
  "calificador": 1,
  "puntuacion": 5,
  "comentario": "Excelente desempeño...",
  "fecha_creacion": "2026-02-06T14:30:00Z"
}
```

### Listar Mis Calificaciones Dadas

```bash
curl http://localhost:8000/api/calificaciones/mis_calificaciones/ \
  -H "Authorization: Bearer $TOKEN"
```

### Listar Calificaciones Recibidas

```bash
curl http://localhost:8000/api/calificaciones/calificaciones_recibidas/ \
  -H "Authorization: Bearer $TOKEN"
```

### Ver Mi Promedio de Calificación

```bash
curl http://localhost:8000/api/promedios/mi_promedio/ \
  -H "Authorization: Bearer $TOKEN"

# Respuesta:
{
  "aprendiz": 1,
  "promedio": 4.5,
  "total_calificaciones": 8,
  "ultima_actualizacion": "2026-02-06T14:30:00Z"
}
```

### Listar Todos los Promedios

```bash
curl http://localhost:8000/api/promedios/
```

---

## 📊 Analytics (v3.0)

### Resumen General

```bash
curl http://localhost:8000/api/analytics/resumen/

# Respuesta:
{
  "usuarios": {
    "total_aprendices": 150,
    "total_empresas": 40,
    "aprendices_activos": 125,
    "empresas_activas": 35
  },
  "postulaciones": {
    "total": 500,
    "este_mes": 120,
    "seleccionados": 85,
    "rechazados": 45,
    "pendientes": 370,
    "tasa_conversion": 17.0
  },
  "fecha_reporte": "2026-02-06"
}
```

### Postulaciones por Estado

```bash
curl http://localhost:8000/api/analytics/postulaciones-por-estado/

# Respuesta para gráfico:
{
  "labels": ["PENDIENTE", "SELECCIONADO", "RECHAZADO", "VENCIDO"],
  "data": [370, 85, 45, 0],
  "colors": ["#FFC107", "#28A745", "#DC3545", "#6C757D"]
}
```

### Tendencia Temporal

```bash
curl "http://localhost:8000/api/analytics/tendencia/?dias=30"

# Respuesta:
{
  "labels": ["2026-01-07", "2026-01-08", ..., "2026-02-06"],
  "postulaciones": [10, 12, 15, 8, ..., 20],
  "seleccionados": [2, 3, 4, 1, ..., 5]
}
```

### Top Empresas

```bash
curl http://localhost:8000/api/analytics/top-empresas/

# Respuesta:
{
  "top_empresas": [
    {
      "id": 5,
      "nombre": "Tech Corp",
      "postulaciones": 45,
      "seleccionados": 30,
      "tasa_aceptacion": 66.7
    },
    {
      "id": 8,
      "nombre": "Innovatech",
      "postulaciones": 38,
      "seleccionados": 25,
      "tasa_aceptacion": 65.8
    }
  ]
}
```

### Aprendices Exitosos

```bash
curl http://localhost:8000/api/analytics/aprendices-exitosos/

# Respuesta:
{
  "aprendices_exitosos": [
    {
      "id": 1,
      "nombre": "Juan Pérez",
      "selecciones": 8,
      "postulaciones": 10,
      "tasa_exito": 80.0
    }
  ]
}
```

### Salud del Sistema

```bash
curl http://localhost:8000/api/analytics/salud-sistema/

# Respuesta:
{
  "usuarios_activos_7_dias": 125,
  "total_usuarios": 190,
  "porcentaje_actividad": 65.8,
  "transacciones_ultima_hora": 42,
  "estado": "HEALTHY"
}
```

---

## 🔐 OAuth2 Google Login

### Iniciar Flujo

```bash
# Redirigir a:
https://localhost:8000/accounts/google/login/

# Usuario será redirigido a Google para autenticarse
```

### Callback Automático

```bash
# Google redirige a:
http://localhost:8000/accounts/google/login/callback/?code=...

# Django allauth maneja todo automáticamente
```

---

## 📧 Celery Tasks

### Enviar Email Postulación

```python
# En shell o código
from plataforma.tasks import enviar_email_postulacion

enviar_email_postulacion.delay(
    aprendiz_email='juan@example.com',
    aprendiz_nombre='Juan',
    empresa_nombre='Tech Corp'
)
```

### Procesar Tasks

```bash
# Celery Worker (en terminal aparte)
celery -A sgva worker -l info

# Celery Beat (scheduler)
celery -A sgva beat -l info
```

---

## 🧪 Tests

### Ejecutar Tests

```bash
# Todos
pytest

# Archivo específico
pytest plataforma/tests/test_api.py

# Test específico
pytest plataforma/tests/test_api.py::TestCalificaciones::test_crear_calificacion

# Con verbosity
pytest -v -s

# Con coverage
pytest --cov=plataforma --cov-report=html
```

### Ejemplo Test

```python
def test_crear_calificacion(client, authenticated_user):
    # Setup
    aprendiz = Aprendiz.objects.create(...)
    empresa = Empresa.objects.create(...)
    postulacion = Postulacion.objects.create(...)
    
    # Request
    response = client.post(
        '/api/calificaciones/',
        {
            'postulacion': postulacion.id,
            'tipo': 'EMPRESA_A_APRENDIZ',
            'puntuacion': 5,
            'comentario': 'Excelente'
        },
        HTTP_AUTHORIZATION=f'Bearer {token}'
    )
    
    # Assert
    assert response.status_code == 201
    assert response.data['puntuacion'] == 5
```

---

## 🔍 Debugging

### Ver Requests/Responses

```python
# En settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

### Celery Debug

```bash
# Logs con timestamp
celery -A sgva worker -l debug

# Inspeccionar tasks pendientes
celery -A sgva inspect active

# Stats del worker
celery -A sgva inspect stats
```

---

## 💾 Datos de Ejemplo

### Crear Aprendiz de Prueba

```bash
curl -X POST http://localhost:8000/api/aprendices/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre_completo": "Test Aprendiz",
    "correo": "test@example.com",
    "numero_documento": "1111111111",
    "estado": "ACTIVO",
    "ficha": 999999,
    "programa_formacion": "Testing Program"
  }'
```

### Crear Empresa de Prueba

```bash
curl -X POST http://localhost:8000/api/empresas/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Test Company",
    "correo": "test@company.com",
    "telefono": "+57 999 999 9999",
    "ciudad": "Bogotá",
    "descripcion": "Empresa de prueba",
    "capacidad_cupos": 10,
    "estado": "ACTIVA"
  }'
```

---

**Para más información, consulta:**
- [README_FINAL.md](./README_FINAL.md)
- [INTEGRACION_FEATURES.md](./INTEGRACION_FEATURES.md)
- [CARACTERISTICAS_AVANZADAS.md](./CARACTERISTICAS_AVANZADAS.md)
- http://localhost:8000/api/docs/ (Swagger UI interactivo)

---

**Versión**: 3.0.0 | **Fecha**: Febrero 2026 | **Status**: ✅ Production Ready
