# [HU-013] Procesamiento de pago

## 📖 Historia de Usuario

**Como** usuario autenticado de EcoMove,

**quiero** procesar el pago de una reserva asociada a un vehículo,

**para** confirmar mi reserva y poder acceder al vehículo mediante código QR.

## 🔁 Flujo Esperado

- El usuario envía una solicitud al endpoint `POST /api/v1/pagos` con los datos del pago.
- El sistema valida que el usuario esté autenticado y activo.
- El sistema verifica que la reserva exista y esté en estado `pendiente`.
- El sistema valida que el monto a pagar coincida con el `costo_estimado` de la reserva.
- El sistema valida el método de pago seleccionado (tarjeta de crédito, débito, monedero electrónico).
- El sistema verifica que no exista un pago aprobado previo para esta reserva.
- El sistema ejecuta la transacción contra la pasarela de pagos.
- Si la transacción es exitosa, el sistema actualiza el estado de la reserva a `confirmada`.
- El sistema registra el pago en la tabla `pagos`.
- El sistema retorna el resultado del pago.

## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [ ] Se expone un endpoint `POST /api/v1/pagos` para procesar pagos.
- [ ] Se valida que los campos `reserva_id`, `monto` y `metodo_pago` sean obligatorios.
- [ ] Se valida que el usuario esté autenticado y sea el propietario de la reserva.
- [ ] Se valida que la reserva exista y tenga estado `pendiente`.
- [ ] Se valida que el `monto` enviado coincida con `costo_estimado` de la reserva.
- [ ] Se valida que `metodo_pago` sea uno de: `tarjeta_credito`, `tarjeta_debito`, `monedero_electronico`.
- [ ] Se verifica que no exista un pago aprobado previo para esta reserva.
- [ ] Se integra con pasarela de pagos externa para procesar la transacción.
- [ ] Si el pago es exitoso, se cambia el estado de la reserva a `confirmada`.
- [ ] Si el pago es rechazado, la reserva permanece en `pendiente`.
- [ ] Se registra el pago en la tabla `pagos` con estado `aprobado` o `rechazado`.

### 2. 📆 Estructura de la información

- [ ] Se responde con la siguiente estructura en JSON para pago exitoso:

~~~json
{
  "success": true,
  "statusCode": 200,
  "message": "Pago procesado exitosamente",
  "data": {
    "pago_id": 5001,
    "reserva_id": 1001,
    "monto": 5000,
    "metodo_pago": "tarjeta_credito",
    "estado": "aprobado",
    "fecha_pago": "2025-01-15T10:35:00Z",
    "transaccion_id": "tx_123456789",
    "reserva_confirmada": true
  }
}
~~~

- [ ] Si el pago es rechazado, el sistema retorna:

~~~json
{
  "success": false,
  "statusCode": 400,
  "message": "Pago rechazado",
  "error": {
    "code": "PAYMENT_REJECTED",
    "details": "La transacción fue rechazada por la pasarela de pagos",
    "motivo": "Fondos insuficientes"
  }
}
~~~

- [ ] Si el monto no coincide con el costo estimado, el sistema retorna:

~~~json
{
  "success": false,
  "statusCode": 400,
  "message": "Monto incorrecto",
  "error": {
    "code": "INVALID_AMOUNT",
    "details": "El monto enviado no coincide con el costo estimado de la reserva",
    "esperado": 5000,
    "recibido": 4000
  }
}
~~~

- [ ] Si la reserva no está en estado `pendiente`, el sistema retorna:

~~~json
{
  "success": false,
  "statusCode": 400,
  "message": "La reserva no está pendiente de pago",
  "error": {
    "code": "INVALID_RESERVATION_STATUS",
    "details": "La reserva ya fue pagada o cancelada"
  }
}
~~~

- [ ] Si ya existe un pago aprobado para esta reserva, el sistema retorna:

~~~json
{
  "success": false,
  "statusCode": 400,
  "message": "La reserva ya ha sido pagada",
  "error": {
    "code": "PAYMENT_ALREADY_EXISTS",
    "details": "Esta reserva ya tiene un pago aprobado"
  }
}
~~~

- [ ] Si la reserva no existe, el sistema retorna error `RESERVATION_NOT_FOUND`.
- [ ] Si el usuario no es el propietario de la reserva, el sistema retorna error `FORBIDDEN`.
- [ ] Si el token no es válido o no se envía, el sistema retorna error `UNAUTHORIZED`.
- [ ] Si la pasarela de pagos no está disponible, el sistema retorna error `PAYMENT_GATEWAY_ERROR`.
- [ ] Si hay error de conexión a la base de datos, el sistema retorna error `DATABASE_ERROR`.

## 🔧 Notas Técnicas

### Reglas de negocio

- Los pagos no son reembolsables una vez que el usuario ha iniciado el viaje.
- El sistema aplica una tarifa mínima por viaje equivalente a 60 minutos de uso, independientemente de que el tiempo real de uso sea inferior.

### Base de datos (tabla `pagos`)

La tabla debe incluir las siguientes columnas:

- id: SERIAL / AUTO_INCREMENT (PK)
- reserva_id: INT, FK a reservas(id), UNIQUE NOT NULL
- usuario_id: INT, FK a usuarios(id)
- monto: DECIMAL(10,2), NOT NULL
- metodo_pago: ENUM('tarjeta_credito', 'tarjeta_debito', 'monedero_electronico'), NOT NULL
- estado: ENUM('aprobado', 'rechazado', 'reembolsado'), NOT NULL
- transaccion_id: VARCHAR(100), NOT NULL
- fecha_pago: TIMESTAMP, DEFAULT CURRENT_TIMESTAMP
- motivo_rechazo: VARCHAR(255), NULLABLE

### Integración con pasarela de pagos

- Llamar a la API de la pasarela con los datos del pago.
- Recibir respuesta con `transaccion_id` y `estado`.
- Manejar timeouts y reintentos (máximo 3 reintentos).

### Transacciones

Usar transacción para:

- Verificar estado de reserva y pagos previos.
- Llamar a la pasarela de pagos.
- Registrar el pago.
- Actualizar el estado de la reserva a `confirmada`.

### Manejo de errores

- Códigos de error sugeridos: `PAYMENT_REJECTED`, `INVALID_AMOUNT`, `INVALID_RESERVATION_STATUS`, `PAYMENT_ALREADY_EXISTS`, `RESERVATION_NOT_FOUND`, `FORBIDDEN`, `UNAUTHORIZED`, `PAYMENT_GATEWAY_ERROR`, `DATABASE_ERROR`.

## 🚀 Endpoint – Procesamiento de pago

- **Método HTTP:** `POST`
- **Ruta:** `/api/v1/pagos`
- **Headers:** `Authorization: Bearer <token>`

### 📤 Ejemplo de Request JSON

~~~json
{
  "reserva_id": 1001,
  "monto": 5000,
  "metodo_pago": "tarjeta_credito",
  "datos_tarjeta": {
    "numero": "4111111111111111",
    "expiracion": "12/25",
    "cvv": "123"
  }
}
~~~

### 📤 Ejemplo de Respuesta JSON Exitosa

~~~json
{
  "success": true,
  "statusCode": 200,
  "message": "Pago procesado exitosamente",
  "data": {
    "pago_id": 5001,
    "reserva_id": 1001,
    "monto": 5000,
    "metodo_pago": "tarjeta_credito",
    "estado": "aprobado",
    "fecha_pago": "2025-01-15T10:35:00Z",
    "transaccion_id": "tx_123456789",
    "reserva_confirmada": true
  }
}
~~~

### 📤 Ejemplo de Respuesta JSON Error (Pago rechazado)

~~~json
{
  "success": false,
  "statusCode": 400,
  "message": "Pago rechazado",
  "error": {
    "code": "PAYMENT_REJECTED",
    "details": "La transacción fue rechazada por la pasarela de pagos",
    "motivo": "Fondos insuficientes"
  }
}
~~~

### 📤 Ejemplo de Respuesta JSON Error (Monto incorrecto)

~~~json
{
  "success": false,
  "statusCode": 400,
  "message": "Monto incorrecto",
  "error": {
    "code": "INVALID_AMOUNT",
    "details": "El monto enviado no coincide con el costo estimado de la reserva",
    "esperado": 5000,
    "recibido": 4000
  }
}
~~~

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

## ✅ Caso 1: Pago exitoso con tarjeta de crédito

- **Precondición:** Reserva existe, estado `pendiente`, costo_estimado = 5000. No hay pagos previos.
- **Acción:** Ejecutar POST /api/v1/pagos con monto = 5000.
- **Resultado esperado:**
  - Código HTTP 200 OK
  - estado: "aprobado"
  - Se registra pago en tabla `pagos`
  - Reserva cambia a `confirmada`

## ❌ Caso 2: Monto incorrecto

- **Precondición:** Reserva existe, costo_estimado = 5000.
- **Acción:** Ejecutar POST /api/v1/pagos con monto = 4000.
- **Resultado esperado:**
  - Código HTTP 400 Bad Request
  - error.code: "INVALID_AMOUNT"

## ❌ Caso 3: Reserva no está pendiente

- **Precondición:** Reserva existe pero estado = `confirmada` o `cancelada`.
- **Acción:** Ejecutar POST /api/v1/pagos.
- **Resultado esperado:**
  - Código HTTP 400 Bad Request
  - error.code: "INVALID_RESERVATION_STATUS"

## ❌ Caso 4: Pago duplicado (ya existe pago aprobado)

- **Precondición:** Reserva ya tiene un pago aprobado asociado.
- **Acción:** Ejecutar POST /api/v1/pagos nuevamente.
- **Resultado esperado:**
  - Código HTTP 400 Bad Request
  - error.code: "PAYMENT_ALREADY_EXISTS"

## ❌ Caso 5: Reserva no existe

- **Precondición:** ID de reserva no existe.
- **Acción:** Ejecutar POST /api/v1/pagos con reserva_id = 99999.
- **Resultado esperado:**
  - Código HTTP 404 Not Found
  - error.code: "RESERVATION_NOT_FOUND"

## ❌ Caso 6: Usuario no es propietario de la reserva

- **Precondición:** Usuario autenticado con ID 2 intenta pagar reserva del usuario ID 1.
- **Acción:** Ejecutar POST /api/v1/pagos.
- **Resultado esperado:**
  - Código HTTP 403 Forbidden
  - error.code: "FORBIDDEN"

## ❌ Caso 7: Método de pago inválido

- **Precondición:** Ninguna.
- **Acción:** Ejecutar POST /api/v1/pagos con metodo_pago = "efectivo".
- **Resultado esperado:**
  - Código HTTP 400 Bad Request
  - error.code: "INVALID_DATA"

## ❌ Caso 8: Pago rechazado por pasarela

- **Precondición:** La pasarela de pagos retorna rechazo (fondos insuficientes, tarjeta inválida).
- **Acción:** Ejecutar POST /api/v1/pagos.
- **Resultado esperado:**
  - Código HTTP 400 Bad Request
  - error.code: "PAYMENT_REJECTED"
  - motivo contiene la razón del rechazo
  - Reserva permanece en `pendiente`

## ❌ Caso 9: Pasarela de pagos no disponible

- **Precondición:** La pasarela de pagos no responde o está caída.
- **Acción:** Ejecutar POST /api/v1/pagos.
- **Resultado esperado:**
  - Código HTTP 503 Service Unavailable
  - error.code: "PAYMENT_GATEWAY_ERROR"

## ❌ Caso 10: Token no enviado

- **Precondición:** Ninguna.
- **Acción:** Ejecutar POST /api/v1/pagos sin header Authorization.
- **Resultado esperado:**
  - Código HTTP 401 Unauthorized
  - error.code: "UNAUTHORIZED"

## ✅ Caso 11: Verificar que reserva se confirma después del pago

- **Precondición:** Pago exitoso.
- **Acción:** Consultar estado de la reserva.
- **Resultado esperado:** estado = "confirmada"

## ❌ Caso 12: Error de conexión a base de datos

- **Precondición:** La base de datos no está disponible.
- **Acción:** Ejecutar POST /api/v1/pagos bajo condiciones de fallo de BD.
- **Resultado esperado:**
  - Código HTTP 503 Service Unavailable
  - error.code: "DATABASE_ERROR"

## ✅ Definición de Hecho

### Historia: [HU-013] Procesamiento de pago

### 📦 Alcance Funcional

- [ ] El endpoint POST /api/v1/pagos está implementado.
- [ ] Se valida que el usuario sea propietario de la reserva.
- [ ] Se valida que la reserva exista y esté en estado `pendiente`.
- [ ] Se valida que el monto coincida con `costo_estimado`.
- [ ] Se valida el método de pago.
- [ ] Se verifica que no exista pago aprobado previo.
- [ ] Se integra con pasarela de pagos.
- [ ] Se registra el pago con estado `aprobado` o `rechazado`.
- [ ] Se actualiza la reserva a `confirmada` si el pago es exitoso.
- [ ] La respuesta JSON cumple con el contrato definido.

### 🧪 Pruebas Completadas

- [ ] Prueba unitaria para validación de monto.
- [ ] Prueba de integración para pago exitoso.
- [ ] Prueba de integración para monto incorrecto.
- [ ] Prueba de integración para reserva no pendiente.
- [ ] Prueba de integración para pago duplicado.
- [ ] Prueba de integración para reserva no encontrada.
- [ ] Prueba de integración para usuario no propietario.
- [ ] Prueba de integración para método de pago inválido.
- [ ] Prueba de integración para pago rechazado.
- [ ] Prueba de integración para pasarela no disponible.
- [ ] Las pruebas funcionales están documentadas y pasadas.

### 📄 Documentación Técnica

- [ ] Endpoint documentado en Swagger / OpenAPI.
- [ ] Se describe propósito, campos de entrada y salida, ejemplos.

### 🔐 Manejo de Errores

- [ ] HTTP 400 para errores de validación (INVALID_AMOUNT, INVALID_RESERVATION_STATUS, PAYMENT_ALREADY_EXISTS, PAYMENT_REJECTED).
- [ ] HTTP 403 para usuario no propietario (FORBIDDEN).
- [ ] HTTP 404 para reserva no encontrada (RESERVATION_NOT_FOUND).
- [ ] HTTP 401 para token no válido (UNAUTHORIZED).
- [ ] HTTP 503 para errores de pasarela o base de datos (PAYMENT_GATEWAY_ERROR, DATABASE_ERROR).
- [ ] Mensajes de error claros.