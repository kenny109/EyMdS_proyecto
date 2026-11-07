# NOMBRE DEL PROYECTO
    Almacen Los Tios

# SOBRE EL AUTOR
    Mi nombre es Eduardo Enrique Ureta Campos y es mi proyecto de título para la Universidad Andres Bello, 2023.

# PARA INGRESAR
    - Descarga el repositorio.
    - Copia .env.example como .env y completa las claves (SECRET_KEY es obligatoria).
    - instala los requirements.txt: pip install -r requirements.txt
    - Para iniciar, el comando es python manage.py runserver
    - Para correr las pruebas: python manage.py test carrito productos home
    - INICIO: http://127.0.0.1:8000/home/
    - Puedes navegar por todas las pestañas

    superuser: admin
    superclave: admin123

# DESCRIPCION BREVE DEL PROYECTO
    Consiste en un sitio web alojado en Django, con funcionalidades que permitan crear una base de datos necesaria para renderizar los distintos productos que se puedan exhibir en el sitio web. Asimismo se puede crear, leer, actualizar y eliminar productos desde el sitio web y el panel de administración. Por otro lado, hay un sistema automático de alerta de niveles de stocks, cuando llega a un umbral mínimo, el cual consiste en enviar un correo con la información detallada del producto y su stock en cantidades mínimas. Ademas, se incorporó un carrito de compras con sus detalles, el cual realiza una solicitud de reserva de productos, notificando al local y al cliente, cual es el pedido de productos a reservar.

# LA PARTE TÉCNICA DEL PROYECTO
    Se utilizo Django, Python, HTML, CSS, Bootstrap

# FUTURAS MEJORAS
    Mejorar la parte estética
    Introducir usuarios


### Línea Base

#### Versión: 1.0.0

**Resumen de Funcionalidades:**
- Registro de superusuario con autenticación.
- Inventario y CRUD de productos, categorías, vendedores.
- Ingreso de transacciones con un producto en punto de Venta.
- CRUD de transacciones o ventas.

**Correcciones de Errores:**
- Corregidos errores de ingreso de productos y categorias.

**Requisitos del Sistema:**
- Navegadores compatibles: Chrome, Firefox, Safari.
- Conexión a internet para el acceso a las funcionalidades.

**Diagrama de Arquitectura:**
- Estructura basada en modelo-vista-controlador (MVC).
- Uso de base de datos relacional para almacenar productos, categorias, vendedores y venta de productos.

**Control de Versiones:**
- Se ha etiquetado la versión 1.1.0 como la línea base inicial en el repositorio de Git.

**Fecha de Lanzamiento:**
- Fecha de lanzamiento: 30 de noviembre de 2023.

**Notas Adicionales:**
- Se espera que futuras versiones incluya el sitio web de exhibición.


---

### Release Notes - Versión 1.1.0

#### Fecha de Lanzamiento: 08 de diciembre de 2023

**Nuevas Funcionalidades:**
- **Ingreso de uno o más productos en punto de venta:** Ahora el locatario podrá ingresar distintos productos en una transacción .
- **Modelo de Productos con umbral mínimo de stock:** Cada producto tiene un umbral mínimo definido previamente.
- **Envio de correo - umbral mínimo:** Al realizar una venta de productos, y este reduce su stock bajo el umbral mínimo, se notificará por correo.
  
**Correcciones:**
- **Corrección de Errores Menores:** Solucionados errores de formato.

**Cambios en la Configuración:**
- **Adición de Nueva Columnas en la Base de Datos:** Se han añadido un campo adicional para definir umbral mínimo de productos.
- **Adición de Nueva Tabla en la Base de Datos:** Se ha añadido una nueva tabla para soportar la función de transacción.


**Notas Finales:**
- Esta versión expande significativamente las capacidades de gestión de inventarios, registro de transacciones en el punto de ventas y notificación vía correo electrónico, proporcionando a los locatarios nuevas herramientas para organizar y manejar su negocio de manera más eficiente.

---

### Release Notes - Versión 1.1.1

#### Fecha de Lanzamiento: 24 de diciembre de 2023

**Nuevas Funcionalidades:**
- **Sitio Web con Renderización de Productos y Categorías:** Ahora el sistema muestra los productos y categorías almacenados en la base de datos en el sitio web.
- **Creación de Carrito de Reserva de Pedidos:** Implementación de un carrito que permite reservar pedidos, mostrando subtotal y total de la compra.
- **Verificación con reCaptcha:** Se ha añadido la verificación con reCaptcha para una capa adicional de seguridad.
- **Envío de Alerta Automática por Umbral Mínimo:** Si un producto alcanza su umbral mínimo, se enviará una alerta automática.

**Notas Finales:**
Esta versión introduce un sitio web funcional con visualización de productos y categorías desde la base de datos. Además, facilita a los usuarios la reserva de pedidos con un carrito que muestra los totales. Se ha reforzado la seguridad con la verificación mediante reCaptcha y se implementa la alerta automática cuando un producto desciende por debajo o iguala el umbral mínimo. En versiones futuras, se planea mejorar las vistas y agregar la gestión de usuarios, así como la integración de portales de pagos para una experiencia más completa y versátil.

---

### Release Notes - Versión 2.0.0

#### Fecha de Lanzamiento: Octubre de 2026 (proyecto de Evolución y Mantenimiento de Software)

**Plataforma y dependencias (MR-101 a MR-106):**
- Migración a Django 5.x compatible con Python 3.13 y depuración de `requirements.txt`.
- SECRET_KEY, DEBUG y credenciales leídas desde `.env` (ver `.env.example`).
- Pruebas unitarias del carrito.

**Panel de administración e interfaces (MR-107 a MR-109):**
- Tema Jazzmin, filtros reordenados y filtro de rango de precios.
- Rediseño de las interfaces públicas.

**Correcciones y mejoras (MR-110 a MR-114):**
- **MR-110 (Correctiva):** el CRUD de productos y categorías y el portal de usuarios quedan restringidos al personal (`is_staff`).
- **MR-111 (Adaptativa):** cierre de sesión por POST (Django 5), rutas de plantillas en minúscula para servidores Linux, login con redirección y `STATIC_ROOT`.
- **MR-112 (Correctiva):** verificación real de reCAPTCHA, remitente de correo de la tienda, revalidación de stock al reservar y manejo de errores 404.
- **MR-113 (Perfectiva):** nueva navegación con contador del carrito, página de inicio con categorías y destacados, footer informativo.
- **MR-114 (Perfectiva):** catálogo con búsqueda, filtro por categoría, paginación, indicadores de stock y ficha pública de producto.

---

### Release Notes - Versión 2.1.0

#### Fecha: 31 de octubre de 2026

- **MR-115 (Perfectiva) – Cuentas de cliente:** tabla `usuarios_cliente` (vinculada a `auth.User`), registro público en `/usuarios/registro/`, página "Mi cuenta" para editar datos y enlace "Crear cuenta" en el navbar y el login. Los clientes nunca son staff.
- **MR-116 (Perfectiva) – Registro de reservas:** tablas `carrito_reserva` y `carrito_detallereserva`; cada solicitud del carrito queda guardada con un código (`LT-XXXXXX`), estado (pendiente / retirada / cancelada / vencida) y plazo de 24 h. Los clientes ven su historial en `/usuarios/mis-reservas/`; el personal gestiona todo en `/carrito/reservas/` y en el admin.
- **Permisos:** permiso nuevo `carrito.gestionar_reservas` y grupo **Vendedores** (ver y gestionar reservas) creado por migración. Un cliente solo puede ver sus propias reservas.
- Zona horaria cambiada a `America/Santiago`.
- Tras actualizar: `python manage.py migrate`. Pruebas: `python manage.py test carrito productos home usuarios` (50 pruebas).

---

### Release Notes - Versión 2.2.0

#### Fecha: 7 de noviembre de 2026

- **MR-117 (Perfectiva) – Pantalla propia de tiendas:** nueva tabla `home_tienda` editable desde el admin (nombre, dirección, horarios, teléfono, coordenadas, foto, activa/orden) y página `/home/tiendas/`. Una migración carga las 3 tiendas que antes estaban escritas en la plantilla.
- **MR-118 (Perfectiva) – Minimapa de ubicaciones:** mapa interactivo con Leaflet 1.9.4 + OpenStreetMap (sin clave de API), un marcador por tienda, botón "Ver en el mapa" y enlace "Cómo llegar" a Google Maps.
- **MR-119 (Perfectiva) – Recuperar y cambiar contraseña:** "¿Olvidaste tu contraseña?" envía un enlace por correo válido por 2 horas (no revela si el correo existe) y "Cambiar contraseña" para usuarios con sesión.
- **MR-120 (Correctiva) – Stock de ventas:** el stock se descontaba en `clean()` (cada validación repetida descontaba otra vez) y no se devolvía al borrar/editar. Ahora se descuenta una sola vez al guardar, se ajusta al editar y se devuelve al borrar; un fallo del correo de stock bajo ya no impide registrar la venta.
- **MR-121 (Perfectiva) – Vencimiento automático y cancelación:** las reservas pendientes con más de 24 h pasan solas a "Vencida" (y con `python manage.py vencer_reservas`); el cliente puede cancelar su reserva pendiente y la tienda recibe un aviso.
- Tras actualizar: `python manage.py migrate`. Pruebas: `python manage.py test carrito productos home usuarios venta` (71 pruebas).
