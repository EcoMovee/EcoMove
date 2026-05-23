# [HU-014] Registro de pago

## 📖 Historia de Usuario

**Como** sistema de EcoMove,

**quiero** registrar cada transacción de pago en una tabla de pagos con todos los detalles de la operación,

**para** mantener un control financiero adecuado, permitir auditorías posteriores y tener trazabilidad completa de cada operación económica.

## 🔁 Flujo Esperado

- El sistema, después de procesar un pago (exitoso o rechazado), registra la transacción en la tabla `pagos`.
- El registro incluye: fecha y hora exacta, monto pagado, método de pago, estado de la transacción, identificador de la reserva, identificador del usuario y ID de transacción de la pasarela.
- Una vez creado, el registro es inmutable (no se puede modificar).
- El registro se crea automáticamente como parte del flujo de procesamiento de pago (HU-013).

## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [ ] Se registra cada transacción de pago en la tabla `pagos`.
- [ ] Los campos obligatorios del registro son:
  - `fecha_pago`: fecha y hora exacta de la transacción
  - `monto`: monto pagado
  - `metodo_pago`: método de pago utilizado
  - `estado`: estado de la transacción (aprobado, rechazado, reembolsado)
  - `reserva_id`: identificador de la reserva asociada
  - `usuario_id`: identificador del usuario que realizó el pago
  - `transaccion_id`: identificador único de la transacción en la pasarela
- [ ] El registro es inmutable: no se permite actualizar ni eliminar registros de pago.
- [ ] Si el pago es exitoso, se registra con estado `aprobado`.
- [ ] Si el pago es rechazado, se registra con estado `rechazado` y se guarda el `motivo_rechazo`.
- [ ] Si se procesa un reembolso (HU-011), se registra un nuevo registro con estado `reembolsado` o se actualiza el existente (según regla de negocio).

### 2. 📆 Estructura de la información

- [ ] Se responde con la siguiente estructura en JSON al consultar un pago (`GET /api/v1/pagos/{id}`):

~~~json
{
  "success": true,
  "statusCode": 200,
  "message": "Pago encontrado",
  "data": {
    "id": 5001,
    "reserva_id": 1001,
    "usuario_id": 1,
    "usuario_nombre": "Juan Perez",
    "monto": 5000,
    "metodo_pago": "tarjeta_credito",
    "estado": "aprobado",
    "transaccion_id": "tx_123456789",
    "fecha_pago": "2025-01-15T10:35:00Z",
    "motivo_rechazo": null
  }
}
~~~

- [ ] Si el pago fue rechazado, el sistema retorna:

~~~json
{
  "success": true,
  "statusCode": 200,
  "message": "Pago encontrado",
  "data": {
    "id": 5002,
    "reserva_id": 1002,
    "usuario_id": 1,
    "usuario_nombre": "Juan Perez",
    "monto": 5000,
    "metodo_pago": "tarjeta_credito",
    "estado": "rechazado",
    "transaccion_id": "tx_987654321",
    "fecha_pago": "2025-01-15T10:40:00Z",
    "motivo_rechazo": "Fondos insuficientes"
  }
}
~~~

- [ ] Si el pago no existe, el sistema retorna:

~~~json
{
  "success": false,
  "statusCode": 404,
  "message": "Pago no encontrado",
  "error": {
    "code": "PAYMENT_NOT_FOUND",
    "details": "No existe un pago con el ID proporcionado"
  }
}
~~~

- [ ] Si el token no es válido o no se envía, el sistema retorna error `UNAUTHORIZED`.
- [ ] Si hay error de conexión a la base de datos, el sistema retorna error `DATABASE_ERROR`.

## 🔧 Notas Técnicas

### Reglas de negocio

- Los pagos no son reembolsables una vez que el usuario ha iniciado el viaje.
- El sistema aplica una tarifa mínima por viaje equivalente a 60 minutos de uso.

### Base de datos (tabla `pagos`)

La tabla debe incluir las siguientes columnas:

- id: SERIAL / AUTO_INCREMENT (PK)
- reserva_id: INT, FK a reservas(id), UNIQUE NOT NULL
- usuario_id: INT, FK a usuarios(id), NOT NULL
- monto: DECIMAL(10,2), NOT NULL
- metodo_pago: ENUM('tarjeta_credito', 'tarjeta_debito', 'monedero_electronico'), NOT NULL
- estado: ENUM('aprobado', 'rechazado', 'reembolsado'), NOT NULL
- transaccion_id: VARCHAR(100), NOT NULL, UNIQUE
- fecha_pago: TIMESTAMP, DEFAULT CURRENT_TIMESTAMP
- motivo_rechazo: VARCHAR(255), NULLABLE
- fecha_reembolso: TIMESTAMP, NULLABLE

### Inmutabilidad de registros

- No permitir operaciones UPDATE ni DELETE en la tabla `pagos` desde la API.
- Si se necesita un reembolso, se puede:
  - Opción A: Crear un nuevo registro con estado `reembolsado` referenciando el pago original.
  - Opción B: Actualizar el estado del pago existente a `reembolsado` (menos estricto).
- Recomendación: Opción A (nuevo registro) para mantener trazabilidad completa.

### Integración con HU-013

- El registro del pago debe ocurrir dentro de la misma transacción que el procesamiento del pago.
- Si el pago es exitoso, se registra con `estado = 'aprobado'`.
- Si el pago es rechazado, se registra con `estado = 'rechazado'` y `motivo_rechazo`.

### Consulta de pagos

- Endpoint `GET /api/v1/pagos/{id}` para consultar un pago específico.
- Endpoint `GET /api/v1/pagos/reserva/{reservaId}` para consultar pagos de una reserva.

### Índices

- Índice en `reserva_id` (búsqueda por reserva).
- Índice en `usuario_id` (búsqueda por usuario).
- Índice en `transaccion_id` (unicidad).

### Manejo de errores

- Códigos de error sugeridos: `PAYMENT_NOT_FOUND`, `UNAUTHORIZED`, `DATABASE_ERROR`.

## 🚀 Endpoints

### Endpoint 1 – Consultar pago por ID

- **Método HTTP:** `GET`
- **Ruta:** `/api/v1/pagos/{id}`
- **Headers:** `Authorization: Bearer <token>`

### Endpoint 2 – Consultar pago por reserva

- **Método HTTP:** `GET`
- **Ruta:** `/api/v1/pagos/reserva/{reservaId}`
- **Headers:** `Authorization: Bearer <token>`

### 📤 Ejemplo de Request (Endpoint 1)

`http GET /api/v1/pagos/5001`

### 📤 Ejemplo de Respuesta JSON Exitosa (Endpoint 1)

~~~json
{
  "success": true,
  "statusCode": 200,
  "message": "Pago encontrado",
  "data": {
    "id": 5001,
    "reserva_id": 1001,
    "usuario_id": 1,
    "usuario_nombre": "Juan Perez",
    "monto": 5000,
    "metodo_pago": "tarjeta_credito",
    "estado": "aprobado",
    "transaccion_id": "tx_123456789",
    "fecha_pago": "2025-01-15T10:35:00Z",
    "motivo_rechazo": null
  }
}
~~~

### 📤 Ejemplo de Respuesta JSON Pago Rechazado

~~~json
{
  "success": true,
  "statusCode": 200,
  "message": "Pago encontrado",
  "data": {
    "id": 5002,
    "reserva_id": 1002,
    "usuario_id": 1,
    "usuario_nombre": "Juan Perez",
    "monto": 5000,
    "metodo_pago": "tarjeta_credito",
    "estado": "rechazado",
    "transaccion_id": "tx_987654321",
    "fecha_pago": "2025-01-15T10:40:00Z",
    "motivo_rechazo": "Fondos insuficientes"
  }
}
~~~

### 📤 Ejemplo de Respuesta JSON Error (Pago no encontrado)

~~~json
{
  "success": false,
  "statusCode": 404,
  "message": "Pago no encontrado",
  "error": {
    "code": "PAYMENT_NOT_FOUND",
    "details": "No existe un pago con el ID proporcionado"
  }
}
~~~

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

## ✅ Caso 1: Registro de pago exitoso

- **Precondición:** Se procesa un pago exitoso (HU-013).
- **Acción:** Verificar la tabla `pagos`.
- **Resultado esperado:**
  - Existe un registro con:
    - reserva_id correcto
    - usuario_id correcto
    - monto correcto
    - metodo_pago correcto
    - estado = 'aprobado'
    - transaccion_id no nulo
    - fecha_pago no nula
    - motivo_rechazo = NULL

## ✅ Caso 2: Registro de pago rechazado

- **Precondición:** Se procesa un pago rechazado (HU-013).
- **Acción:** Verificar la tabla `pagos`.
- **Resultado esperado:**
  - Existe un registro con:
    - estado = 'rechazado'
    - motivo_rechazo contiene la razón del rechazo

## ✅ Caso 3: Consultar pago por ID exitosamente

- **Precondición:** Existe un pago con ID 5001.
- **Acción:** Ejecutar GET /api/v1/pagos/5001.
- **Resultado esperado:**
  - Código HTTP 200 OK
  - data contiene todos los campos del pago

## ✅ Caso 4: Consultar pago por reserva exitosamente

- **Precondición:** Existe un pago asociado a la reserva 1001.
- **Acción:** Ejecutar GET /api/v1/pagos/reserva/1001.
- **Resultado esperado:**
  - Código HTTP 200 OK
  - data contiene el pago de la reserva

## ❌ Caso 5: Consultar pago que no existe

- **Precondición:** No existe pago con ID 99999.
- **Acción:** Ejecutar GET /api/v1/pagos/99999.
- **Resultado esperado:**
  - Código HTTP 404 Not Found
  - error.code: "PAYMENT_NOT_FOUND"

## ❌ Caso 6: Intentar modificar un pago (inmutabilidad)

- **Precondición:** Existe un pago registrado.
- **Acción:** Intentar PUT o PATCH a /api/v1/pagos/{id}.
- **Resultado esperado:**
  - El endpoint no debe existir o debe retornar 405 Method Not Allowed
  - El registro no se modifica

## ❌ Caso 7: Intentar eliminar un pago (inmutabilidad)

- **Precondición:** Existe un pago registrado.
- **Acción:** Intentar DELETE a /api/v1/pagos/{id}.
- **Resultado esperado:**
  - El endpoint no debe existir o debe retornar 405 Method Not Allowed
  - El registro no se elimina

## ✅ Caso 8: Unicidad de transaccion_id

- **Precondición:** Se procesa un pago con transaccion_id = "tx_123".
- **Acción:** Intentar procesar otro pago con el mismo transaccion_id.
- **Resultado esperado:**
  - La base de datos rechaza el duplicado (constraint UNIQUE)
  - Se retorna error DATABASE_ERROR o similar

## ❌ Caso 9: Token no enviado

- **Precondición:** Ninguna.
- **Acción:** Ejecutar GET /api/v1/pagos/5001 sin header Authorization.
- **Resultado esperado:**
  - Código HTTP 401 Unauthorized
  - error.code: "UNAUTHORIZED"

## ❌ Caso 10: Error de conexión a base de datos

- **Precondición:** La base de datos no está disponible.
- **Acción:** Ejecutar GET /api/v1/pagos/5001 bajo condiciones de fallo de BD.
- **Resultado esperado:**
  - Código HTTP 503 Service Unavailable
  - error.code: "DATABASE_ERROR"

## ✅ Caso 11: Verificar que el registro es inmutable después de creado

- **Precondición:** Pago registrado con estado `aprobado`.
- **Acción:** Intentar cambiar el estado a través de cualquier operación.
- **Resultado esperado:** El estado no cambia (a menos que sea un reembolso, que debería crear un nuevo registro).

## ✅ Definición de Hecho

### Historia: [HU-014] Registro de pago

### 📦 Alcance Funcional

- [ ] Cada transacción de pago se registra en la tabla `pagos`.
- [ ] Los campos obligatorios se almacenan correctamente.
- [ ] El registro incluye `fecha_pago`, `monto`, `metodo_pago`, `estado`, `reserva_id`, `usuario_id`, `transaccion_id`.
- [ ] El registro es inmutable (no se permite UPDATE ni DELETE).
- [ ] Los pagos rechazados registran `motivo_rechazo`.
- [ ] Existen endpoints para consultar pagos por ID y por reserva.
- [ ] La respuesta JSON cumple con el contrato definido.

### 🧪 Pruebas Completadas

- [ ] Prueba de integración para registro de pago exitoso.
- [ ] Prueba de integración para registro de pago rechazado.
- [ ] Prueba de integración para consulta de pago por ID.
- [ ] Prueba de integración para consulta de pago por reserva.
- [ ] Prueba de integración para pago no encontrado.
- [ ] Prueba de integración para inmutabilidad (sin UPDATE/DELETE).
- [ ] Prueba de integración para unicidad de `transaccion_id`.
- [ ] Las pruebas funcionales están documentadas y pasadas.

### 📄 Documentación Técnica

- [ ] Endpoints documentados en Swagger / OpenAPI.
- [ ] Se describe el esquema de la tabla `pagos`.
- [ ] Se documenta la inmutabilidad de los registros.

### 🔐 Manejo de Errores

- [ ] HTTP 404 para pago no encontrado (PAYMENT_NOT_FOUND).
- [ ] HTTP 401 para token no válido (UNAUTHORIZED).
- [ ] HTTP 503 para error de conexión a base de datos (DATABASE_ERROR).
- [ ] HTTP 405 para intentos de modificación (Method Not Allowed).
- [ ] Mensajes de error claros.