<<<<<<< HEAD
# 📋 SGVA - Sistema de Gestión de Vinculación de Aprendices

## 📝 Descripción General

SGVA es una plataforma web profesional desarrollada en **Django** que conecta aprendices con empresas para oportunidades laborales:
- **👨‍🎓 Aprendices**: Buscar y postularse a oportunidades de empleo
- **🏢 Empresas**: Publicar oportunidades y gestionar postulaciones
- **👨‍💼 Administradores**: Supervisar y controlar el sistema
- **🔌 API REST**: Integración con aplicaciones externas
- **⚡ WebSockets**: Notificaciones en tiempo real
- **🐳 Docker**: Deploy en contenedores

---

## ✨ Características Principales

### 🎯 Funcionalidades Comunes
- ✅ Autenticación segura con Django
- ✅ Panel de usuario personalizado
- ✅ Gestión de perfiles
- ✅ Base de datos relacional

### 🔌 API REST (DRF)
- ✅ Full CRUD para Aprendices, Empresas y Postulaciones
- ✅ Filtrado, búsqueda y ordenamiento avanzado
- ✅ Paginación automática
- ✅ Validación de datos

### 📊 Documentación API (Swagger/OpenAPI)
- ✅ Acceso en `/api/docs/` (Swagger UI)
- ✅ Acceso en `/api/redoc/` (ReDoc)
- ✅ Schema JSON en `/api/schema/`

### ⚡ WebSockets (Django Channels)
- ✅ Conexiones en tiempo real
- ✅ Notificaciones de nuevas postulaciones
- ✅ Alertas de cambio de estado
- ✅ Recordatorios de vencimiento

### 🧪 Tests Automatizados
- ✅ Tests con pytest y Django TestCase
- ✅ Cobertura de modelos, vistas y API
- ✅ Tests de API REST

### 🐳 Containerización
- ✅ Dockerfile para producción
- ✅ Docker Compose con PostgreSQL, Redis y Nginx
- ✅ Configuración ASGI con Daphne
- ✅ Proxy inverso con Nginx

---

## 🚀 Instalación y Setup

### Opción 1: Setup Automático (Recomendado)

**Windows:**
```cmd
setup.bat
```

**Linux/Mac:**
```bash
bash setup.sh
```

### Opción 2: Setup Manual

1. **Crear entorno virtual:**
   ```powershell
   python -m venv venv
   venv\Scripts\activate
   ```

2. **Instalar dependencias:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Ejecutar migraciones:**
   ```powershell
   python manage.py migrate
   ```

4. **Generar datos de prueba:**
   ```powershell
   python manage.py shell < seed_data.py
   ```

5. **Iniciar servidor:**
   ```powershell
   python manage.py runserver
   ```

6. **Acceder a la plataforma:**
   Abre http://127.0.0.1:8000/

### Opción 3: Con Docker (Producción)

```bash
docker-compose up --build
```

Acceder en: http://localhost

---

## 🔌 API REST - Endpoints

### Aprendices
```
GET    /api/aprendices/              - Listar todos
POST   /api/aprendices/              - Crear nuevo
GET    /api/aprendices/{id}/         - Detalle
PUT    /api/aprendices/{id}/         - Actualizar
DELETE /api/aprendices/{id}/         - Eliminar
GET    /api/aprendices/{id}/postulaciones/  - Postulaciones de aprendiz
GET    /api/aprendices/activos/      - Solo aprendices activos
```

### Empresas
```
GET    /api/empresas/                - Listar todas
POST   /api/empresas/                - Crear nueva
GET    /api/empresas/{id}/           - Detalle
PUT    /api/empresas/{id}/           - Actualizar
DELETE /api/empresas/{id}/           - Eliminar
GET    /api/empresas/{id}/postulaciones/    - Postulaciones recibidas
GET    /api/empresas/disponibles/    - Solo empresas disponibles
```

### Postulaciones
```
GET    /api/postulaciones/           - Listar todas
POST   /api/postulaciones/           - Crear nueva
GET    /api/postulaciones/{id}/      - Detalle
PUT    /api/postulaciones/{id}/      - Actualizar
POST   /api/postulaciones/{id}/cambiar_estado/  - Cambiar estado
GET    /api/postulaciones/vencidas/  - Postulaciones vencidas (>15 días)
```

### Documentación
```
GET    /api/docs/                    - Swagger UI
GET    /api/redoc/                   - ReDoc
GET    /api/schema/                  - OpenAPI Schema JSON
```

---

## ⚡ WebSockets

### Conectar a WebSocket
```javascript
// JavaScript
const ws = new WebSocket('ws://localhost:8000/ws/notificaciones/usuario_id/');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    if (data.type === 'notificacion_postulacion') {
        console.log(`Nuevo aprendiz: ${data.aprendiz}`);
    } else if (data.type === 'notificacion_cambio_estado') {
        console.log(`Estado cambió a: ${data.estado_nuevo}`);
    }
};
```

### Tipos de Notificaciones
- `notificacion_postulacion` - Nueva postulación recibida
- `notificacion_cambio_estado` - Cambio de estado en postulación
- `notificacion_vencimiento` - Postulación próxima a vencer

---

## 🧪 Tests

### Ejecutar todos los tests
```powershell
pytest
```

### Tests específicos
```powershell
pytest plataforma/tests/test_api.py -v
pytest plataforma/tests/test_models.py -v
pytest plataforma/tests/test_views.py -v
```

### Con cobertura
```powershell
pytest --cov=plataforma
```

---

## 🐳 Docker - Guía Completa

### Construir y ejecutar
```bash
docker-compose up --build
```

### Servicios disponibles
- **App**: http://localhost:8000
- **Nginx**: http://localhost:80
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### Comandos útiles
```bash
# Entrar en shell Django
docker-compose exec app python manage.py shell

# Crear superuser
docker-compose exec app python manage.py createsuperuser

# Ver logs
docker-compose logs -f app

# Detener servicios
docker-compose down

# Limpiar todo
docker-compose down -v
```

---

## 📊 Usuarios de Prueba Disponibles

### 2. Registro e Inicio de Sesion

#### Opción A: Registrarse como Aprendiz
1. Click en **📝 Registro**
2. Elige **Soy Aprendiz**
3. Completa el formulario con:
   - Usuario: (ej: juan_mendez)
   - Correo: tu@email.com
   - Contraseña: mínimo 8 caracteres
4. Click **Registrarse como Aprendiz**
5. Inicia sesion con tus credenciales

#### Opción B: Registrarse como Empresa
1. Click en **📝 Registro**
2. Elige **Soy una Empresa**
3. Completa el formulario con:
   - Información de cuenta (usuario, correo, contraseña)
   - Información de empresa (nombre, NIT, dirección, descripción, cupos)
4. Click **Crear Empresa**
5. Inicia sesion con tus credenciales

### 3. Usuarios de Prueba Disponibles

#### 👨‍🎓 Aprendices (Crear nuevo en el sistema)
```
Usuario: juan | Contraseña: juan123
Usuario: maria | Contraseña: maria123
```

#### 🏢 Empresas (Listas para usar)
```
Usuario: empresa1 | Contraseña: empresa123
Empresa: Tech Solutions S.A. (3 cupos)

Usuario: empresa2 | Contraseña: empresa123
Empresa: Innovatech Ltd. (2 cupos)
```

#### 👨‍💼 Administrador
```
Usuario: admin | Contraseña: admin123
```

---

## 👨‍🎓 Guía para Aprendices

### Dashboard de Aprendiz
Una vez iniciado sesion, ves un panel con:
- **Tus datos**: Nombre, correo, estado
- **Postulaciones activas**: Lista de empresas a las que te postulaste
- **Estado de postulaciones**: Pendiente, Seleccionado, Rechazado

### Ver Oportunidades de Empleo
1. Click en **💼 Oportunidades** en la barra de navegación
2. Visualiza todas las empresas activas con:
   - Nombre de empresa
   - Descripción
   - Ubicación (dirección)
   - Cupos disponibles
   - Estado (Activa, Oferta caducada)

### Postularse a una Empresa
1. En la página de oportunidades, busca la empresa de tu interés
2. Click en **✅ Postularme** (si hay cupos disponibles)
3. Confirma tu postulación en el modal
4. ¡Espera a que la empresa revise tu perfil!

### Gestionar tu Perfil
1. Click en **📊 Dashboard**
2. Actualiza tu información personal
3. Guarda los cambios

---

## 🏢 Guía para Empresas

### Dashboard de Empresa
Una vez iniciado sesion, ves un panel con:
- **Informacion de tu empresa**
- **Aprendices postulados**: Lista de quiénes se han postulado
- **Postulaciones por estado**: Pendiente, Seleccionado, Rechazado

### Gestionar tu Empresa
1. Click en **📊 Dashboard**
2. Click en **Editar** tu empresa
3. Actualiza:
   - Descripción
   - Dirección
   - Capacidad de cupos
   - Observaciones
4. Guarda los cambios

### Revisar Postulaciones
1. Click en **Aprendices** en la barra de navegación
2. Ve el perfil detallado de cada aprendiz que se postulo
3. Ver estado de postulación:
   - **Pendiente**: Aún sin evaluar
   - **Seleccionado**: Aceptado
   - **Rechazado**: No seleccionado

### Cambiar Estado de Postulaciones
1. Click en la postulación específica
2. Click en **Cambiar estado**
3. Elige entre:
   - **Seleccionado**: Aceptar aprendiz
   - **Rechazado**: Rechazar aprendiz
4. Guarda el cambio

### Sistema de Cupos
- **Capacidad de cupos**: Cupos totales que puede contratar
- **Cupos disponibles**: Se calcula automáticamente restando seleccionados
- **Oferta caducada**: Cuando cupos_disponibles = 0, aparece este estado
- Los aprendices NO pueden postularse cuando la oferta está caducada

---

## 📊 Guía para Administradores

### Panel Administrativo
1. Click en **Admin** en la barra de navegación
2. O entra a: **http://127.0.0.1:8000/admin/**
3. Inicia sesion con: admin / admin123

### Funciones Administrativas
Desde el panel puedes:
- **Ver/Editar Usuarios**: Crear, modificar, eliminar usuarios
- **Ver/Editar Empresas**: Cambiar estados, capacidades, información
- **Ver/Editar Aprendices**: Actualizar perfiles
- **Ver/Editar Postulaciones**: Revisar historial completo
- **Ver/Editar Solicitudes**: Gestionar solicitudes especiales

---

## 🔄 Flujo Completo de Uso

### Para un Aprendiz
```
1. Registro como aprendiz
   ↓
2. Iniciar sesion
   ↓
3. Ver dashboard personal
   ↓
4. Click en "Oportunidades"
   ↓
5. Buscar y explorar empresas
   ↓
6. Postularse a empresas de interés
   ↓
7. Esperar respuesta de empresas
   ↓
8. Ver estado en dashboard
```

### Para una Empresa
```
1. Registro como empresa (completo)
   ↓
2. Iniciar sesion
   ↓
3. Ver dashboard con datos de empresa
   ↓
4. Revisar postulaciones de aprendices
   ↓
5. Ver perfil de cada aprendiz
   ↓
6. Aceptar o rechazar postulaciones
   ↓
7. Editar información de empresa si es necesario
```

---

## 🎨 Características Principales

### Interfaz Usuario
- ✅ Diseño responsivo (funciona en móvil y desktop)
- ✅ Navegación intuitiva con iconos
- ✅ Gradientes y colores atractivos
- ✅ Cards interactivas con hover effects
- ✅ Formularios validados

### Funcionalidad
- ✅ Búsqueda y filtrado de empresas
- ✅ Sistema de postulaciones con estados
- ✅ Gestión de cupos/capacidades
- ✅ Historial de cambios de estado
- ✅ Roles de usuario (Estudiante, Trabajador)
- ✅ Paginación de resultados (6 por página)

### API JavaScript
- ✅ Postulación sin recargar página (AJAX)
- ✅ Modal de confirmación
- ✅ Alertas de éxito/error
- ✅ Actualización dinámica de cupos

---

## 🛠 Tecnologías Utilizadas

- **Backend**: Django 6.0.2
- **Base de Datos**: SQLite3
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Lenguaje**: Python 3.12
- **API**: REST (JSON)

---

## 📁 Estructura de Proyecto

```
sgva_web/
├── plataforma/
│   ├── models.py          # Modelos (Empresa, Aprendiz, Postulacion, etc)
│   ├── views.py           # Vistas (lógica de negocio)
│   ├── urls.py            # Rutas de la aplicación
│   ├── admin.py           # Configuración de admin
│   ├── templates/
│   │   └── plataforma/
│   │       ├── base.html            # Template base
│   │       ├── landing.html         # Página de inicio (sin autenticar)
│   │       ├── registro_tipo.html   # Elegir tipo de registro
│   │       ├── registro_aprendiz.html
│   │       ├── registro_empresa.html
│   │       ├── login.html
│   │       ├── oportunidades.html   # Bolsa de empleos
│   │       ├── empresas.html        # Listado de empresas
│   │       ├── aprendices.html      # Listado de aprendices
│   │       ├── dashboard.html       # Panel de usuario
│   │       └── (templates detalle)
│   └── migrations/        # Migraciones de base de datos
├── sgva/                  # Configuración principal del proyecto
├── manage.py
├── db.sqlite3             # Base de datos SQLite
└── actualizar_datos.py    # Script para crear datos de prueba
```

---

## 🔐 Seguridad

- ✅ Contraseñas hasheadas (Django)
- ✅ Autenticación requerida para funciones críticas
- ✅ CSRF tokens en formularios
- ✅ Validación de entrada en servidor

---

## 📱 Responsividad

La plataforma se adapta a:
- 📱 Móviles (320px+)
- 📱 Tablets (768px+)
- 💻 Desktops (1024px+)

---

## ❓ Preguntas Frecuentes

**P: ¿Puedo cambiar mis datos después de registrarme?**
R: Sí, accede a tu dashboard y haz clic en "Editar perfil"

**P: ¿Qué pasa si una empresa llena sus cupos?**
R: Aparecerá "Oferta caducada" y los aprendices no podrán postularse

**P: ¿Puedo postularme a la misma empresa dos veces?**
R: No, el sistema previene postulaciones duplicadas

**P: ¿Cómo elimino mi cuenta?**
R: Contacta al administrador (admin@ejemplo.com)

**P: ¿Qué información ven las empresas sobre mí?**
R: Tu nombre, correo, teléfono (si lo proporcionaste) y otros datos de tu perfil

---

## 📧 Soporte

Para reportar bugs o sugerencias:
- 📧 Email: contacto@sgva.local
- 📱 Teléfono: (Contactar administrador)

---

**Versión**: 2.0.0  
**Última actualización**: Febrero 2026  
**Estado**: ✅ Producción

=======
# sgva
>>>>>>> 8e37a6f5e6f1a636a15acd41c49018cd755fa02d
