# NOMBRE DEL PROYECTO
    Almacen Los Tios

# SOBRE EL AUTOR
    Mi nombre es Eduardo Enrique Ureta Campos y es mi proyecto de título para la Universidad Andres Bello, 2023.

# PARA INGRESAR
    - Descarga el repositorio.
    - instala los requirements.txt 
    - Para iniciar, el comando es python manage.py runserver
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