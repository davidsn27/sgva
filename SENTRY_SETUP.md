# 📋 Configuración de Sentry para SGVA

## 🎯 ¿Qué es Sentry?

Sentry es una plataforma de monitoreo de errores y rendimiento que ayuda a:
- **Capturar errores automáticamente** cuando ocurren en producción
- **Monitorear el rendimiento** de la aplicación
- **Recibir alertas** en tiempo real
- **Analizar tendencias** de errores

## 🔧 Pasos para Configurar Sentry

### 1. Crear Cuenta en Sentry

1. Ve a [https://sentry.io](https://sentry.io)
2. Regístrate o inicia sesión
3. Crea un nuevo proyecto
4. Selecciona **Django** como plataforma

### 2. Obtener el DSN

Una vez creado el proyecto, Sentry te proporcionará un **DSN (Data Source Name)** con este formato:
```
https://xxxxx@sentry.io/xxxxx
```

### 3. Configurar en SGVA

#### Opción A: Usar Variables de Entorno (Recomendado)

1. Copia el archivo `.env.example` a `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edita `.env` y agrega tu DSN:
   ```env
   SENTRY_DSN=https://tu-dsn@sentry.io/tu-proyecto
   ENVIRONMENT=production
   APP_VERSION=1.0.0
   ```

#### Opción B: Configurar Directamente en settings.py

```python
# En sgva/settings.py, reemplaza la línea:
SENTRY_DSN = os.getenv("SENTRY_DSN", "https://tu-dsn@sentry.io/tu-proyecto")
```

### 4. Probar la Configuración

Reinicia el servidor y verifica que no aparezcan advertencias:

```bash
python manage.py runserver
```

Si está configurado correctamente, no deberías ver:
```
⚠️ Advertencia: No se pudo inicializar Sentry (DSN inválido)
```

## 🚀 Características Configuradas

### ✅ **Monitoreo de Errores**
- Captura automática de excepciones
- Stack traces detallados
- Información del usuario y request

### ✅ **Monitoreo de Rendimiento**
- Seguimiento de transacciones
- Métricas de tiempo de respuesta
- Detección de cuellos de botella

### ✅ **Integraciones**
- **Django**: Middleware y vistas
- **Celery**: Tareas asíncronas
- **Redis**: Conexiones y caché

### ✅ **Filtros Avanzados**
- Ignorar errores de modo debug
- Muestreo del 10% de transacciones
- Entorno diferenciado (development/production)

## 📊 Uso en Producción vs Desarrollo

### **Desarrollo**
```env
SENTRY_DSN=  # Vacío para desactivar
ENVIRONMENT=development
```

### **Producción**
```env
SENTRY_DSN=https://tu-dsn@sentry.io/tu-proyecto
ENVIRONMENT=production
APP_VERSION=1.0.0
```

## 🔍 Verificación de Funcionamiento

### Para probar que Sentry está funcionando:

1. **Genera un error intencional**:
   ```python
   # En una vista
   raise Exception("Error de prueba para Sentry")
   ```

2. **Verifica en Sentry** que el error aparece en el dashboard

3. **Revisa las alertas** configuradas

## 📱 Configuración de Alertas

1. En el dashboard de Sentry, ve a **Settings → Alerts**
2. Configura notificaciones por:
   - **Email**
   - **Slack**
   - **Discord**
   - **Webhooks**

## 🛠️ Solución de Problemas Comunes

### **"DSN inválido"**
- Verifica que el DSN esté correcto
- Asegúrate de no tener espacios extra
- Confirma que el proyecto exista en Sentry

### **"No se envían errores"**
- Verifica que `SENTRY_DSN` no esté vacío
- Confirma que `ENVIRONMENT=production`
- Revisa la conectividad de red

### **"Muchos errores de debug"**
- El filtro `before_send` debería ignorar errores de desarrollo
- Verifica que `DEBUG=False` en producción

## 📚 Referencias

- [Documentación oficial de Sentry](https://docs.sentry.io/)
- [Integración con Django](https://docs.sentry.io/platforms/integrations/django/)
- [Configuración de variables de entorno](https://docs.sentry.io/product/configuration/)

---

**¿Necesitas ayuda?** Revisa la documentación oficial o contacta al equipo de desarrollo.
