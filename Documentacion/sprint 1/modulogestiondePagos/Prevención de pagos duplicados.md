# [HU-015] Prevención de pagos duplicados

## 📖 Historia de Usuario

**Como** sistema de EcoMove,

**quiero** prevenir que se procesen pagos duplicados para una misma reserva,

**para** evitar cobros duplicados al usuario y mantener la integridad financiera del sistema.

## 🔁 Flujo Esperado

- El usuario intenta procesar un pago para una reserva mediante `POST /api/v1/pagos`.
- Antes de procesar el pago, el sistema verifica si la reserva ya tiene un pago asociado con estado `aprobado`.
- Si ya existe un pago aprobado, el sistema rechaza el nuevo intento.
- Si existe un pago rechazado previamente, el sistema permite reintentar el pago.
- El sistema utiliza mecanismos de control de concurrencia (bloqueos optimistas o transacciones atómicas) para evitar que dos solicitudes simultáneas generen pagos duplicados.

## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [ ] Antes de procesar un pago, se verifica si la reserva tiene un pago con estado `aprobado`.
- [ ] Si existe un pago aprobado, se rechaza el nuevo intento.
- [ ] Si existe un pago rechazado, se permite reintentar el pago.
- [ ] Se implementan mecanismos de control de concurrencia para evitar pagos duplicados en solicitudes simultáneas.
- [ ] La verificación se realiza dentro de una transacción con bloqueo.

### 2. 📆 Estructura de la información

- [ ] Si la reserva ya tiene un pago aprobado, el sistema retorna:

~~~json
{
  "success": false,
  "statusCode": 400,
  "message": "Esta reserva ya ha sido pagada",
  "error": {
    "code": "PAYMENT_ALREADY_EXISTS",
    "details": "La reserva ya tiene un pago aprobado asociado",
    "pago_id": 5001,
    "fecha_pago": "2025-01-15T10:35:00Z"
  }
}
~~~

- [ ] Si se intentan dos pagos simultáneos para la misma reserva, solo uno debe ser exitoso:

  - Primer request (exitoso):

~~~json
{
  "success": true,
  "statusCode": 200,
  "message": "Pago procesado exitosamente"
}
~~~

  - Segundo request (rechazado):

~~~json
{
  "success": false,
  "statusCode": 400,
  "message": "Esta reserva ya ha sido pagada",
  "error": {
    "code": "PAYMENT_ALREADY_EXISTS",
    "details": "La reserva ya tiene un pago aprobado asociado"
  }
}
~~~

## 🔧 Notas Técnicas

### Reglas de negocio

- Los pagos no son reembolsables una vez que el usuario ha iniciado el viaje.
- El sistema aplica una tarifa mínima por viaje equivalente a 60 minutos de uso.

### Base de datos (tabla `pagos`)

- La columna `reserva_id` debe tener constraint UNIQUE para evitar múltiples pagos aprobados por reserva.
- Opcional: agregar un índice único condicional para permitir solo un `aprobado` por reserva.

~~~sql
CREATE UNIQUE INDEX idx_unique_approved_payment 
ON pagos (reserva_id) 
WHERE estado = 'aprobado';
~~~

### Control de concurrencia

**Opción 1: Bloqueo pesimista (recomendada)**

~~~sql
SELECT * FROM reservas WHERE id = ? FOR UPDATE;
SELECT * FROM pagos WHERE reserva_id = ? AND estado = 'aprobado' FOR UPDATE;
-- Si no existe, procesar pago
INSERT INTO pagos (reserva_id, ...) VALUES (...);
COMMIT;
~~~

**Opción 2: Bloqueo optimista**

- Usar un campo `version` en la tabla `reservas`.
- Incrementar la versión al actualizar el estado.
- Si la versión cambió durante el proceso, reintentar o fallar.

**Opción 3: Unique constraint en combinación con lógica de aplicación**

- La base de datos rechaza el segundo INSERT si ya existe un pago aprobado.

### Flujo de validación

- Iniciar transacción.
- Bloquear la fila de la reserva (`SELECT FOR UPDATE`).
- Verificar estado de la reserva (debe estar `pendiente`).
- Verificar si existe pago aprobado para esta reserva.
- Si no existe, procesar el pago con la pasarela.
- Si el pago es exitoso, insertar registro en `pagos` con estado `aprobado`.
- Actualizar reserva a `confirmada`.
- Confirmar transacción (`COMMIT`).
- Si el pago es rechazado, insertar registro con estado `rechazado` (la reserva sigue `pendiente`).

### Manejo de reintentos

- Si existe un pago rechazado, se permite reintentar.
- No hay límite de reintentos definido (puede añadirse después).

### Manejo de errores

- Códigos de error sugeridos: `PAYMENT_ALREADY_EXISTS`, `CONCURRENT_PAYMENT_ERROR`.

## 🚀 Endpoint – Procesamiento de pago (con validación)

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

### 📤 Ejemplo de Respuesta JSON Error (Pago ya existe)

~~~json
{
  "success": false,
  "statusCode": 400,
  "message": "Esta reserva ya ha sido pagada",
  "error": {
    "code": "PAYMENT_ALREADY_EXISTS",
    "details": "La reserva ya tiene un pago aprobado asociado",
    "pago_id": 5001,
    "fecha_pago": "2025-01-15T10:35:00Z"
  }
}
~~~

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

## ✅ Caso 1: Pago exitoso sin pagos previos

- **Precondición:** Reserva existe, estado `pendiente`, no hay pagos asociados.
- **Acción:** Ejecutar POST /api/v1/pagos.
- **Resultado esperado:**
  - Código HTTP 200 OK
  - Se crea pago con estado `aprobado`
  - Reserva cambia a `confirmada`

## ❌ Caso 2: Intento de pago cuando ya existe pago aprobado

- **Precondición:** Reserva ya tiene un pago aprobado asociado.
- **Acción:** Ejecutar POST /api/v1/pagos nuevamente.
- **Resultado esperado:**
  - Código HTTP 400 Bad Request
  - error.code: "PAYMENT_ALREADY_EXISTS"
  - No se procesa nuevo pago
  - Reserva permanece `confirmada`

## ✅ Caso 3: Reintento después de pago rechazado

- **Precondición:** Reserva tiene un pago rechazado asociado.
- **Acción:** Ejecutar POST /api/v1/pagos nuevamente.
- **Resultado esperado:**
  - Se permite el reintento
  - Si el nuevo pago es exitoso, se crea nuevo pago con estado `aprobado`
  - Reserva cambia a `confirmada`

## ❌ Caso 4: Dos pagos simultáneos para la misma reserva

- **Precondición:** Reserva existe, estado `pendiente`, sin pagos.
- **Acción:** Ejecutar dos requests POST /api/v1/pagos simultáneamente.
- **Resultado esperado:**
  - Solo un request es exitoso (HTTP 200)
  - El otro recibe error PAYMENT_ALREADY_EXISTS (HTTP 400)
  - Solo se crea un pago en la base de datos
  - Solo se realiza un cargo en la pasarela de pagos

## ✅ Caso 5: Verificar que pago rechazado no bloquea futuros intentos

- **Precondición:** Reserva tiene pago rechazado.
- **Acción:** Verificar que el sistema permite un nuevo intento.
- **Resultado esperado:** La validación solo bloquea cuando `estado = 'aprobado'`.

## ❌ Caso 6: Intento de pago con reserva ya confirmada por otro medio

- **Precondición:** Reserva ya tiene estado `confirmada` (por ejemplo, por un pago previo).
- **Acción:** Ejecutar POST /api/v1/pagos.
- **Resultado esperado:**
  - Código HTTP 400 Bad Request
  - error.code: "INVALID_RESERVATION_STATUS"

## ❌ Caso 7: Race condition con bloqueo pesimista

- **Precondición:** Dos requests simultáneos.
- **Acción:** Usar `SELECT FOR UPDATE` en la transacción.
- **Resultado esperado:** El segundo request espera a que el primero complete y luego detecta que el pago ya existe.

## ❌ Caso 8: Error de conexión a base de datos durante validación

- **Precondición:** La base de datos no está disponible.
- **Acción:** Ejecutar POST /api/v1/pagos bajo condiciones de fallo de BD.
- **Resultado esperado:**
  - Código HTTP 503 Service Unavailable
  - error.code: "DATABASE_ERROR"

## ❌ Caso 9: Pasarela de pagos rechaza pero se registró como aprobado (consistencia)

- **Precondición:** La pasarela retorna error después de que la base de datos ya registró el pago.
- **Acción:** Usar transacción para garantizar consistencia.
- **Resultado esperado:** Si la pasarela falla, la transacción se revierte (ROLLBACK).

## ✅ Definición de Hecho

### Historia: [HU-015] Prevención de pagos duplicados

### 📦 Alcance Funcional

- [ ] Se verifica si la reserva tiene pago aprobado antes de procesar.
- [ ] Si existe pago aprobado, se rechaza el nuevo intento.
- [ ] Si existe pago rechazado, se permite reintentar.
- [ ] Se implementan mecanismos de control de concurrencia.
- [ ] Se usa `SELECT FOR UPDATE` o unique constraint en la base de datos.
- [ ] Se manejan correctamente los pagos simultáneos.
- [ ] La respuesta JSON cumple con el contrato definido.

### 🧪 Pruebas Completadas

- [ ] Prueba de integración para pago sin pagos previos.
- [ ] Prueba de integración para pago con pago aprobado existente.
- [ ] Prueba de integración para reintento después de pago rechazado.
- [ ] Prueba de concurrencia para pagos simultáneos.
- [ ] Prueba de integración para reserva ya confirmada.
- [ ] Las pruebas funcionales están documentadas y pasadas.

### 📄 Documentación Técnica

- [ ] Endpoint documentado en Swagger / OpenAPI.
- [ ] Se documenta la estrategia de control de concurrencia.

### 🔐 Manejo de Errores

- [ ] HTTP 400 para pago ya existente (PAYMENT_ALREADY_EXISTS).
- [ ] HTTP 503 para error de conexión a base de datos (DATABASE_ERROR).
- [ ] Mensajes de error claros con detalles del pago existente.