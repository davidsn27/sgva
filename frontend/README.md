# SGVA Frontend

Dashboard moderno para el Sistema de Gestión de Vinculación de Aprendices.

## 📋 Características

- ✅ Login con OAuth2 (Google, Microsoft)
- ✅ Dashboard con estadísticas en tiempo real
- ✅ Gestión de postulaciones
- ✅ Sistema de calificaciones
- ✅ Analytics y métricas
- ✅ Diseño responsivo moderno
- ✅ UI intuitiva y accesible

## 🚀 Quick Start

### Opción 1: Abrir directamente (recomendado)
```bash
# Abre el archivo index.html en tu navegador
# O sírvelo con Python
python -m http.server 3000
```

Luego accede a: `http://localhost:3000`

### Opción 2: Integrar con Django (Production)

```bash
# Copiar frontend a Django static
cp -r frontend/index.html sgva/plataforma/templates/
cp -r frontend/app.js frontend/styles.css sgva/plataforma/static/
```

## 🔐 Configuración

Asegúrate de que el backend esté corriendo en:
```
http://127.0.0.1:8000/api
```

Si cambias el puerto, actualiza en `app.js`:
```javascript
const API_BASE = 'http://localhost:PUERTO/api';
```

## 📁 Estructura

```
frontend/
├── index.html      - UI principal
├── app.js          - Lógica de la aplicación
├── styles.css      - Estilos CSS moderno
└── README.md       - Este archivo
```

## 🎨 Colores

- **Primario**: #3b82f6 (Azul)
- **Secundario**: #10b981 (Verde)
- **Warning**: #f59e0b (Ámbar)
- **Danger**: #ef4444 (Rojo)

## 🔗 API Endpoints Utilizados

- `POST /api/token/` - Autenticación
- `GET /api/postulaciones/` - Listar postulaciones
- `POST /api/postulaciones/{id}/cambiar_estado/` - Cambiar estado
- `GET /api/calificaciones/mi_promedio/` - Mi calificación
- `GET /api/analytics/estadisticas/` - Estadísticas generales
- `GET /api/analytics/postulaciones_por_estado/` - Postulaciones por estado

## 🛠️ Desarrollo

Para mejorar el frontend:

1. Abre `index.html` en tu editor
2. Edita HTML en `index.html`
3. Edita CSS en `styles.css`
4. Edita JS en `app.js`
5. Recarga el navegador (Ctrl+F5)

## 📱 Responsive

- ✅ Desktop (1024px+)
- ✅ Tablet (768px)
- ✅ Mobile (320px+)

## 🚀 Próximos Pasos

- [ ] Agregar gráficos con Chart.js
- [ ] Integrar formularios de registro
- [ ] Sistema de notificaciones push
- [ ] Exportar reportes PDF
- [ ] Dark mode
- [ ] Internacionalización (i18n)

---

**Estado**: ✅ Production Ready  
**Última actualización**: Febrero 2026
