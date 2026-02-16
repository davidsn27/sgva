<!-- Configuración para servir el frontend con Django -->
<!-- Agregar esto a django/settings.py en TEMPLATES si lo deseas integrar -->

# Frontend Moderno SGVA

## 📊 Características Implementadas

✅ **Dashboard profesional** con:
  - Login elegante con OAuth2 (Google/Microsoft)
  - Estadísticas en tiempo real (postulaciones, aceptadas, pendientes, calificación)
  - Vista de postulaciones recientes
  - Sistema de filtrado y búsqueda

✅ **Gestión de Postulaciones**:
  - Listar todas las postulaciones
  - Filtrar por estado (Pendiente, Seleccionado, Rechazado)
  - Búsqueda en tiempo real
  - Cambiar estado de postulaciones

✅ **Analytics Dashboard**:
  - Estadísticas generales
  - Tasa de conversión
  - Postulaciones por estado
  - Métricas de uso

✅ **Diseño moderno**:
  - Interfaz responsiva (mobile, tablet, desktop)
  - Gradientes modernos
  - Animaciones suaves
  - Iconos Font Awesome
  - Notificaciones toast

## 🚀 Cómo usar

### Opción 1: Abrir en navegador (más fácil)

```bash
# En Windows
cd c:\Users\Aprendiz\Documents\sgva_web\frontend

# Abre index.html directamente en navegador
# O sírvelo con Python:
python -m http.server 3000
```

Accede a: `http://localhost:3000`

### Opción 2: Integrar con Django (Production)

```bash
# Copiar archivos al directorio static de Django
cp frontend/index.html plataforma/templates/
cp frontend/app.js frontend/styles.css plataforma/static/js/
```

Luego en Django urls.py:
```python
from django.views.generic import TemplateView

path('dashboard/', TemplateView.as_view(template_name='index.html')),
```

## 🔑 Credenciales de Prueba

Usa las del seed data de Django:
- Usuario: `aprendiz1` / Password: `password123`
- Usuario: `empresa1` / Password: `password123`

## 🎨 Personalización

### Cambiar colores primarios
Edita `styles.css`:
```css
:root {
    --primary: #3b82f6;  /* Azul - Cambiar aquí */
    --secondary: #10b981; /* Verde */
}
```

### Cambiar API base
Edita `app.js`:
```javascript
const API_BASE = 'http://tu-servidor/api'; // Cambiar aquí
```

## 📱 Pantallas

1. **Login** - Autenticación con OAuth2
2. **Dashboard** - Vista general con estadísticas
3. **Postulaciones** - Gestión completa de postulaciones
4. **Analytics** - Métricas y análisis

## 🔗 API Endpoints Conectados

- `POST /api/token/` - Login
- `GET /api/postulaciones/` - Listar postulaciones
- `POST /api/postulaciones/{id}/cambiar_estado/` - Cambiar estado
- `GET /api/calificaciones/mi_promedio/` - Calificación actual
- `GET /api/analytics/estadisticas/` - Stats generales

## 📦 Archivos

```
frontend/
├── index.html        (HTML principal - 350 líneas)
├── styles.css        (Estilos modernos - 600 líneas)
├── app.js            (Lógica JavaScript - 300 líneas)
└── README.md         (Documentación)
```

Total: ~1250 líneas de código frontend de calidad production-ready.

## 🎯 Próximas mejoras opcionales

- [ ] Agregar Chart.js para gráficos
- [ ] Formularios de registro
- [ ] Notificaciones push (FCM)
- [ ] Exportar reportes PDF
- [ ] Dark mode
- [ ] Internacionalización (i18n)

---

**Estado**: ✅ Production Ready  
**Última actualización**: Febrero 2026
**Horas de desarrollo**: ~3 horas
