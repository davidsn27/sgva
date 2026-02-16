# 🚀 Quick Reference - SGVA 2.0

## ⚡ Comandos Rápidos

### Setup Inicial
```bash
# Automático (Recomendado)
setup.bat              # Windows
bash setup.sh          # Linux/Mac

# Manual
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python manage.py migrate
python manage.py shell < seed_data.py
```

### Ejecutar Servidor
```bash
# Desarrollo
python manage.py runserver

# ASGI (con WebSockets)
daphne -b 0.0.0.0 -p 8000 sgva.asgi:application

# Gunicorn (WSGI)
gunicorn sgva.wsgi --bind 0.0.0.0:8000
```

### Docker
```bash
# Construir y ejecutar
docker-compose up --build

# Solo logs
docker-compose logs -f app

# Detener
docker-compose down
```

### Tests
```bash
# Todos
pytest

# Archivo específico
pytest plataforma/tests/test_api.py -v

# Con cobertura
pytest --cov=plataforma
```

---

## 📍 URLs Importantes

| URL | Descripción |
|-----|-------------|
| `/` | Página de inicio |
| `/admin/` | Panel administrativo |
| `/api/` | Root de API REST |
| `/api/aprendices/` | Endpoint Aprendices |
| `/api/empresas/` | Endpoint Empresas |
| `/api/postulaciones/` | Endpoint Postulaciones |
| `/api/docs/` | Swagger UI |
| `/api/redoc/` | ReDoc |
| `/api/schema/` | OpenAPI Schema |
| `ws://localhost/ws/notificaciones/{id}/` | WebSocket |

---

## 🔧 Archivos Clave

| Archivo | Propósito |
|---------|-----------|
| `models.py` | Definición de modelos |
| `serializers.py` | Serialización para API |
| `viewsets.py` | API REST ViewSets |
| `consumers.py` | WebSocket Consumers |
| `views.py` | Vistas tradicionales (HTML) |
| `urls.py` | Rutas de la aplicación |
| `settings.py` | Configuración Django |
| `requirements.txt` | Dependencias Python |
| `seed_data.py` | Datos de prueba |
| `pytest.ini` | Configuración pytest |

---

## 📦 Dependencias Principales

```
djangorestframework>=3.14
django-cors-headers>=4.0
drf-spectacular>=0.29
channels>=4.0
daphne>=4.0
pytest>=9.0
pytest-django>=4.11
gunicorn>=25.0
whitenoise>=6.0
psycopg2>=2.9
```

---

## 🔐 Usuarios de Prueba

```
Aprendiz:
  usuario: juan
  contraseña: juan123

Empresa:
  usuario: empresa1
  contraseña: empresa123

Admin:
  usuario: admin
  contraseña: admin123
```

---

## 📊 Estructura de BD

```
User (Django Auth)
├── Perfil
├── Aprendiz
│   └── Postulacion
│       ├── Empresa
│       └── HistorialPostulacion
├── Empresa
    └── Postulacion
        └── HistorialPostulacion
```

---

## 🎯 Endpoints Ejemplo

### GET - Listar Aprendices
```bash
curl http://localhost:8000/api/aprendices/
```

### POST - Crear Aprendiz
```bash
curl -X POST http://localhost:8000/api/aprendices/ \
  -H "Content-Type: application/json" \
  -d '{
    "usuario": 1,
    "nombres": "Juan",
    "apellidos": "Pérez",
    "email": "juan@test.com",
    "numero_identificacion": "123456789",
    "estado": "Activo"
  }'
```

### POST - Cambiar Estado Postulación
```bash
curl -X POST http://localhost:8000/api/postulaciones/1/cambiar_estado/ \
  -H "Content-Type: application/json" \
  -d '{"estado": "SELECCIONADO"}'
```

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'rest_framework'"
```bash
pip install djangorestframework
```

### "Cannot import name 'ProtocolTypeRouter'"
```bash
pip install channels daphne
```

### Migraciones pendientes
```bash
python manage.py migrate
```

### Puerto 8000 en uso
```bash
python manage.py runserver 8001
```

---

## 📈 Performance Tips

1. **Usar filtros en lugar de cargar todo**
   ```bash
   GET /api/aprendices/?estado=Activo
   ```

2. **Ordenamiento eficiente**
   ```bash
   GET /api/aprendices/?ordering=-fecha_registro
   ```

3. **Búsqueda rápida**
   ```bash
   GET /api/aprendices/?search=juan
   ```

4. **Paginación**
   ```bash
   GET /api/aprendices/?page=2
   ```

---

## 🔄 Git Workflow

```bash
# Clonar
git clone <url>

# Rama nueva
git checkout -b feature/nueva-feature

# Cambios
git add .
git commit -m "Descripción clara"

# Push
git push origin feature/nueva-feature

# Pull Request
# Crear en GitHub/GitLab
```

---

## 📞 Ayuda Rápida

- **Documentación Django**: https://docs.djangoproject.com/
- **DRF Docs**: https://www.django-rest-framework.org/
- **Django Channels**: https://channels.readthedocs.io/
- **Pytest**: https://docs.pytest.org/

---

**Versión**: 2.0.0  
**Última actualización**: 2026-02-06
