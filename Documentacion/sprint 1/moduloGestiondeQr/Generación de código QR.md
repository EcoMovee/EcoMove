# [HU-017] Generación de código QR

## 📖 Historia de Usuario

**Como** sistema de EcoMove,

**quiero** generar automáticamente un código QR único e irrepetible cuando una reserva ha sido confirmada y pagada,

**para** permitir al usuario acceder al vehículo de forma segura sin necesidad de contacto humano.

## 🔁 Flujo Esperado

- El sistema detecta que una reserva ha sido pagada exitosamente (estado `confirmada`).
- El sistema genera un código QR único para esa reserva.
- El código QR contiene información cifrada: `reserva_id`, `vehiculo_id`, `fecha_hora_inicio`, `fecha_hora_fin`.
- El sistema agrega una firma digital al contenido para evitar falsificaciones.
- El código QR se almacena en la tabla `qrs` con estado `activo`.
- El código QR se pone a disposición del usuario a través de la aplicación móvil y correo electrónico.

## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [ ] Se expone un endpoint `POST /api/v1/qrs` para generar un código QR (disparado por el sistema automáticamente).
- [ ] La generación se dispara automáticamente después de un pago exitoso (HU-013).
- [ ] El código QR es único por reserva (una reserva solo tiene un QR activo).
- [ ] El contenido del QR incluye:
  - `reserva_id`
  - `vehiculo_id`
  - `fecha_hora_inicio`
  - `fecha_hora_fin`
  - `firma_digital`
- [ ] La información se cifra antes de ser codificada en el QR.
- [ ] Se genera una firma digital con un secreto del sistema para validar autenticidad.
- [ ] El QR se almacena en la tabla `qrs` con estado `activo`.
- [ ] El QR se pone a disposición del usuario en formato imagen (Base64 o URL).
- [ ] El QR se envía al correo electrónico del usuario.

### 2. 📆 Estructura de la información

- [ ] Se responde con la siguiente estructura en JSON para generación exitosa:

~~~json
{
  "success": true,
  "statusCode": 201,
  "message": "Código QR generado exitosamente",
  "data": {
    "id": 7001,
    "reserva_id": 1001,
    "vehiculo_id": 1,
    "codigo_qr": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
    "estado": "activo",
    "fecha_expiracion": "2025-01-20T12:00:00Z",
    "fecha_generacion": "2025-01-15T10:36:00Z"
  }
}
~~~

- [ ] Si la reserva no tiene pago confirmado, el sistema retorna:

~~~json
{
  "success": false,
  "statusCode": 400,
  "message": "No se puede generar el código QR",
  "error": {
    "code": "PAYMENT_NOT_CONFIRMED",
    "details": "La reserva no ha sido pagada. Debes completar el pago para generar el QR"
  }
}
~~~

- [ ] Si ya existe un QR activo para la reserva, el sistema retorna:

~~~json
{
  "success": true,
  "statusCode": 200,
  "message": "Código QR ya existe",
  "data": {
    "id": 7001,
    "codigo_qr": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
    "estado": "activo"
  }
}
~~~

- [ ] Si la reserva no existe, el sistema retorna error `RESERVATION_NOT_FOUND`.
- [ ] Si hay error de conexión a la base de datos, el sistema retorna error `DATABASE_ERROR`.

## 🔧 Notas Técnicas

### Reglas de negocio

- El código QR tiene una validez de 10 minutos desde su generación; si no es escaneado en ese lapso, expira y se debe solicitar uno nuevo.
- Cada código QR es único por transacción y solo puede ser escaneado una vez.

### Base de datos (tabla `qrs`)

La tabla debe incluir las siguientes columnas:

- id: SERIAL / AUTO_INCREMENT (PK)
- reserva_id: INT, FK a reservas(id), UNIQUE NOT NULL
- vehiculo_id: INT, FK a vehiculos(id), NOT NULL
- codigo_hash: VARCHAR(255), NOT NULL (hash del contenido del QR)
- codigo_qr_base64: TEXT, NOT NULL (imagen del QR en Base64)
- estado: ENUM('activo', 'usado', 'expirado'), DEFAULT 'activo'
- fecha_generacion: TIMESTAMP, DEFAULT CURRENT_TIMESTAMP
- fecha_expiracion: TIMESTAMP, NOT NULL (fecha_generacion + 10 minutos)
- fecha_uso: TIMESTAMP, NULLABLE

### Contenido del QR y firma digital

Información a incluir:

~~~json
{
  "reserva_id": 1001,
  "vehiculo_id": 1,
  "inicio": "2025-01-20T10:00:00Z",
  "fin": "2025-01-20T12:00:00Z",
  "exp": 1737388800
}
~~~

Generación de firma:

- Usar HMAC-SHA256 con un secreto del sistema.
- Firmar el string: `reserva_id:vehiculo_id:inicio:fin:exp`
- Incluir la firma en el contenido del QR.

### Cifrado

- Opcional: cifrar todo el contenido con AES-256 antes de codificar en QR.
- El descifrado se realiza en el momento de la validación (HU-018).

### Generación de la imagen QR

- Usar librería `qrcode` (Node.js), `pyqrcode` (Python), o similar.
- Generar imagen en formato PNG.
- Convertir a Base64 para enviar en la respuesta JSON.
- Almacenar en base de datos para no tener que regenerar.

### Disparo automático

- Escuchar el evento de pago exitoso (webhook o after save en el servicio de pagos).
- Llamar al servicio de generación de QR automáticamente.

### Envío por correo

- Enviar el código QR al usuario como adjunto o enlace.

### Manejo de errores

- Códigos de error sugeridos: `PAYMENT_NOT_CONFIRMED`, `RESERVATION_NOT_FOUND`, `QR_ALREADY_EXISTS`, `DATABASE_ERROR`.

## 🚀 Endpoint – Generación de código QR

- **Método HTTP:** `POST`
- **Ruta:** `/api/v1/qrs`
- **Headers:** `Authorization: Bearer <token>`

### 📤 Ejemplo de Request JSON

~~~json
{
  "reserva_id": 1001
}
~~~

### 📤 Ejemplo de Respuesta JSON Exitosa

~~~json
{
  "success": true,
  "statusCode": 201,
  "message": "Código QR generado exitosamente",
  "data": {
    "id": 7001,
    "reserva_id": 1001,
    "vehiculo_id": 1,
    "codigo_qr": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
    "estado": "activo",
    "fecha_expiracion": "2025-01-15T10:46:00Z",
    "fecha_generacion": "2025-01-15T10:36:00Z"
  }
}
~~~

### 📤 Ejemplo de Respuesta JSON Error (Pago no confirmado)

~~~json
{
  "success": false,
  "statusCode": 400,
  "message": "No se puede generar el código QR",
  "error": {
    "code": "PAYMENT_NOT_CONFIRMED",
    "details": "La reserva no ha sido pagada. Debes completar el pago para generar el QR"
  }
}
~~~

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

## ✅ Caso 1: Generación exitosa de QR después de pago

- **Precondición:** Reserva existe, estado `confirmada`, pagada. No hay QR previo.
- **Acción:** Ejecutar POST /api/v1/qrs con reserva_id válido.
- **Resultado esperado:**
  - Código HTTP 201 Created
  - estado: "activo"
  - fecha_expiracion = fecha_generacion + 10 minutos
  - Se almacena registro en `qrs`

## ✅ Caso 2: QR ya existe para la reserva

- **Precondición:** Reserva ya tiene un QR activo.
- **Acción:** Ejecutar POST /api/v1/qrs nuevamente.
- **Resultado esperado:**
  - Código HTTP 200 OK
  - Se retorna el QR existente (no se genera uno nuevo)

## ❌ Caso 3: Reserva no pagada

- **Precondición:** Reserva existe pero estado no es `confirmada` (ej: `pendiente`).
- **Acción:** Ejecutar POST /api/v1/qrs.
- **Resultado esperado:**
  - Código HTTP 400 Bad Request
  - error.code: "PAYMENT_NOT_CONFIRMED"

## ❌ Caso 4: Reserva no existe

- **Precondición:** Reserva con ID 99999 no existe.
- **Acción:** Ejecutar POST /api/v1/qrs con reserva_id = 99999.
- **Resultado esperado:**
  - Código HTTP 404 Not Found
  - error.code: "RESERVATION_NOT_FOUND"

## ✅ Caso 5: Verificar contenido cifrado del QR

- **Precondición:** QR generado exitosamente.
- **Acción:** Decodificar el contenido del QR.
- **Resultado esperado:**
  - El contenido incluye `reserva_id`, `vehiculo_id`, `inicio`, `fin`, `exp`
  - El contenido incluye una firma válida

## ✅ Caso 6: Verificar expiración del QR

- **Precondición:** QR generado con `fecha_expiracion = fecha_generacion + 10 minutos`.
- **Acción:** Consultar el registro en la base de datos.
- **Resultado esperado:** `fecha_expiracion` es correcta.

## ✅ Caso 7: QR generado automáticamente después de pago

- **Precondición:** Usuario realiza un pago exitoso (HU-013).
- **Acción:** Verificar la tabla `qrs` después del pago.
- **Resultado esperado:** Existe un registro con la reserva asociada.

## ✅ Caso 8: Verificar envío de QR por correo

- **Precondición:** QR generado exitosamente.
- **Acción:** Revisar el correo del usuario.
- **Resultado esperado:** El correo contiene el QR (como adjunto o enlace).

## ❌ Caso 9: Generación de QR falla por error de librería

- **Precondición:** La librería de generación de QR no está disponible.
- **Acción:** Ejecutar POST /api/v1/qrs.
- **Resultado esperado:**
  - Código HTTP 500 Internal Server Error
  - Se registra error en logs

## ❌ Caso 10: Error de conexión a base de datos

- **Precondición:** La base de datos no está disponible.
- **Acción:** Ejecutar POST /api/v1/qrs bajo condiciones de fallo de BD.
- **Resultado esperado:**
  - Código HTTP 503 Service Unavailable
  - error.code: "DATABASE_ERROR"

## ✅ Definición de Hecho

### Historia: [HU-017] Generación de código QR

### 📦 Alcance Funcional

- [ ] Se expone un endpoint POST /api/v1/qrs para generar QR.
- [ ] La generación se dispara automáticamente después de pago exitoso.
- [ ] El código QR es único por reserva.
- [ ] El contenido del QR incluye `reserva_id`, `vehiculo_id`, `inicio`, `fin` y firma digital.
- [ ] La información se cifra antes de codificarse.
- [ ] Se genera firma digital con HMAC-SHA256.
- [ ] El QR se almacena en base de datos (tabla `qrs`).
- [ ] El QR se envía al correo del usuario.
- [ ] La respuesta JSON cumple con el contrato definido.

### 🧪 Pruebas Completadas

- [ ] Prueba de integración para generación exitosa.
- [ ] Prueba de integración para QR ya existente.
- [ ] Prueba de integración para reserva no pagada.
- [ ] Prueba de integración para reserva no encontrada.
- [ ] Prueba de integración para verificar contenido cifrado.
- [ ] Prueba de integración para verificar expiración.
- [ ] Prueba de integración para generación automática post-pago.
- [ ] Prueba de integración para envío de correo.
- [ ] Las pruebas funcionales están documentadas y pasadas.

### 📄 Documentación Técnica

- [ ] Endpoint documentado en Swagger / OpenAPI.
- [ ] Se documenta el formato del contenido cifrado.
- [ ] Se documenta el algoritmo de firma digital.

### 🔐 Manejo de Errores

- [ ] HTTP 400 para reserva no pagada (PAYMENT_NOT_CONFIRMED).
- [ ] HTTP 404 para reserva no encontrada (RESERVATION_NOT_FOUND).
- [ ] HTTP 503 para error de conexión a base de datos (DATABASE_ERROR).
- [ ] Mensajes de error claros.