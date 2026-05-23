# [HU-011] Cancelación de reserva

## 📖 Historia de Usuario

**Como** usuario autenticado de EcoMove,

**quiero** cancelar una reserva activa que ya no voy a utilizar,

**para** liberar el vehículo para otros usuarios, evitar penalizaciones innecesarias y mantener un historial transparente de mis acciones.

## 🔁 Flujo Esperado

- El usuario envía una solicitud al endpoint `POST /api/v1/reservas/{id}/cancelar` para cancelar una reserva.
- El sistema valida que el usuario esté autenticado y sea el propietario de la reserva.
- El sistema verifica que la reserva exista y esté activa (estado `pendiente` o `confirmada`).
- El sistema calcula la anticipación de la cancelación respecto a la hora de inicio.
- Si la cancelación se realiza con al menos 2 horas de anticipación, no hay penalización.
- Si la cancelación se realiza con menos de 2 horas de anticipación, se aplica penalización del 20%.
- El sistema cambia el estado de la reserva a `cancelada`.
- El sistema libera el vehículo automáticamente.
- Si la reserva ya tenía un pago asociado, se procesa la devolución correspondiente.
- El sistema registra la cancelación en el historial de la reserva.

## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [ ] Se expone un endpoint `POST /api/v1/reservas/{id}/cancelar` para cancelar reservas.
- [ ] Se valida que el usuario autenticado sea el propietario de la reserva (rol `usuario` solo puede cancelar sus propias reservas).
- [ ] Se valida que la reserva exista en la tabla `reservas`.
- [ ] Se valida que la reserva tenga estado `pendiente` o `confirmada`.
- [ ] No se permite cancelar reservas con estado `en_curso`, `finalizada` o `cancelada`.
- [ ] Se calcula la anticipación: `(hora_inicio - NOW())` en horas.
- [ ] Si `anticipacion >= 2 horas`: sin penalización, reembolso total.
- [ ] Si `anticipacion < 2 horas`: penalización del 20%, reembolso parcial.
- [ ] Se actualiza el estado de la reserva a `cancelada`.
- [ ] Se registra `fecha_cancelacion` y `penalizacion_aplicada`.
- [ ] Se libera el vehículo automáticamente.
- [ ] Si existe un pago aprobado asociado, se procesa reembolso a través de la pasarela.

### 2. 📆 Estructura de la información

- [ ] Se responde con la siguiente estructura en JSON para cancelación exitosa sin penalización:

~~~json
{
  "success": true,
  "statusCode": 200,
  "message": "Reserva cancelada exitosamente",
  "data": {
    "reserva_id": 1001,
    "estado_anterior": "confirmada",
    "estado_nuevo": "cancelada",
    "fecha_cancelacion": "2025-01-20T08:00:00Z",
    "anticipacion_horas": 2,
    "penalizacion_aplicada": false,
    "penalizacion_monto": 0,
    "reembolso_procesado": 5000
  }
}
~~~

- [ ] Si la cancelación tiene penalización, el sistema retorna:

~~~json
{
  "success": true,
  "statusCode": 200,
  "message": "Reserva cancelada con penalización del 20%",
  "data": {
    "reserva_id": 1001,
    "estado_anterior": "confirmada",
    "estado_nuevo": "cancelada",
    "fecha_cancelacion": "2025-01-20T09:30:00Z",
    "anticipacion_horas": 0.5,
    "penalizacion_aplicada": true,
    "penalizacion_monto": 1000,
    "reembolso_procesado": 4000
  }
}
~~~

- [ ] Si la reserva no existe, el sistema retorna:

~~~json
{
  "success": false,
  "statusCode": 404,
  "message": "Reserva no encontrada",
  "error": {
    "code": "RESERVATION_NOT_FOUND",
    "details": "No existe una reserva con el ID proporcionado"
  }
}
~~~

- [ ] Si la reserva no puede cancelarse (estado incorrecto), el sistema retorna:

~~~json
{
  "success": false,
  "statusCode": 400,
  "message": "No se puede cancelar la reserva",
  "error": {
    "code": "INVALID_RESERVATION_STATUS",
    "details": "La reserva ya está finalizada o cancelada y no puede cancelarse nuevamente"
  }
}
~~~

- [ ] Si el usuario no es el propietario de la reserva, el sistema retorna error `FORBIDDEN`.
- [ ] Si el token no es válido o no se envía, el sistema retorna error `UNAUTHORIZED`.
- [ ] Si hay error de conexión a la base de datos, el sistema retorna error `DATABASE_ERROR`.

## 🔧 Notas Técnicas

### Reglas de negocio

- El tiempo máximo de reserva antes de iniciar el viaje es de 15 minutos; pasado este tiempo, la reserva se cancela automáticamente y el vehículo queda disponible nuevamente.
- Un usuario que acumule tres reservas canceladas por no pago o no presentación dentro de un período de 30 días será temporalmente inhabilitado para realizar nuevas reservas durante una semana.
- Los pagos no son reembolsables una vez que el usuario ha iniciado el viaje.

### Base de datos (tabla `reservas`)

La tabla debe incluir las siguientes columnas adicionales:

- fecha_cancelacion: TIMESTAMP, NULLABLE
- penalizacion_aplicada: BOOLEAN, DEFAULT FALSE
- penalizacion_monto: DECIMAL(10,2), DEFAULT 0
- reembolso_procesado: DECIMAL(10,2), DEFAULT 0

### Lógica de anticipación

- Calcular: `anticipacion_horas = (hora_inicio - NOW())` en horas (usar TIMESTAMPDIFF).
- Si `anticipacion_horas >= 2` → sin penalización.
- Si `anticipacion_horas < 2` → penalización = `costo_estimado * 0.20`.

### Integración con pagos

- Al cancelar, consultar si existe un pago aprobado para esta reserva.
- Si existe, llamar a la pasarela de pagos para procesar el reembolso.
- Registrar el reembolso en la tabla `pagos` con estado `reembolsado`.

### Transacciones

Usar transacción para:

- Verificar estado y anticipación.
- Actualizar estado de la reserva.
- Liberar el vehículo (implícito al cancelar).
- Procesar reembolso si aplica.

### Manejo de errores

- Códigos de error sugeridos: `RESERVATION_NOT_FOUND`, `INVALID_RESERVATION_STATUS`, `FORBIDDEN`, `UNAUTHORIZED`, `DATABASE_ERROR`.

## 🚀 Endpoint – Cancelación de reserva

- **Método HTTP:** `POST`

- **Ruta:** `/api/v1/reservas/{id}/cancelar`

- **Headers:** `Authorization: Bearer <token>`

### 📤 Ejemplo de Request

`http POST /api/v1/reservas/1001/cancelar`

### 📤 Ejemplo de Respuesta JSON Exitosa (Sin penalización)

~~~json
{
  "success": true,
  "statusCode": 200,
  "message": "Reserva cancelada exitosamente",
  "data": {
    "reserva_id": 1001,
    "estado_anterior": "confirmada",
    "estado_nuevo": "cancelada",
    "fecha_cancelacion": "2025-01-20T08:00:00Z",
    "anticipacion_horas": 2,
    "penalizacion_aplicada": false,
    "penalizacion_monto": 0,
    "reembolso_procesado": 5000
  }
}
~~~

### 📤 Ejemplo de Respuesta JSON Exitosa (Con penalización)

~~~json
{
  "success": true,
  "statusCode": 200,
  "message": "Reserva cancelada con penalización del 20%",
  "data": {
    "reserva_id": 1001,
    "estado_anterior": "confirmada",
    "estado_nuevo": "cancelada",
    "fecha_cancelacion": "2025-01-20T09:30:00Z",
    "anticipacion_horas": 0.5,
    "penalizacion_aplicada": true,
    "penalizacion_monto": 1000,
    "reembolso_procesado": 4000
  }
}
~~~

### 📤 Ejemplo de Respuesta JSON Error (Reserva no encontrada)

~~~json
{
  "success": false,
  "statusCode": 404,
  "message": "Reserva no encontrada",
  "error": {
    "code": "RESERVATION_NOT_FOUND",
    "details": "No existe una reserva con el ID proporcionado"
  }
}
~~~

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

## ✅ Caso 1: Cancelación anticipada sin penalización

- **Precondición:** Reserva para las 10:00, cancelación a las 08:00 (2 horas antes). Estado `confirmada`. Costo = 5000.

- **Acción:** Ejecutar POST /api/v1/reservas/1001/cancelar.

- **Resultado esperado:**
  - Código HTTP 200 OK

  - penalizacion_aplicada: false

  - penalizacion_monto: 0

  - reembolso_procesado: 5000

  - Estado cambia a `cancelada`

  - Vehículo liberado

## ⚠️ Caso 2: Cancelación tardía con penalización

- **Precondición:** Reserva para las 10:00, cancelación a las 09:30 (0.5 horas antes). Estado `confirmada`. Costo = 5000.

- **Acción:** Ejecutar POST /api/v1/reservas/1001/cancelar.

- **Resultado esperado:**
  - Código HTTP 200 OK

  - penalizacion_aplicada: true

  - penalizacion_monto: 1000

  - reembolso_procesado: 4000

  - Estado cambia a `cancelada`

## ❌ Caso 3: Cancelar reserva en curso

- **Precondición:** Reserva con estado `en_curso`.

- **Acción:** Ejecutar POST /api/v1/reservas/1001/cancelar.

- **Resultado esperado:**
  - Código HTTP 400 Bad Request

  - error.code: "INVALID_RESERVATION_STATUS"

## ❌ Caso 4: Cancelar reserva ya cancelada

- **Precondición:** Reserva con estado `cancelada`.

- **Acción:** Ejecutar POST /api/v1/reservas/1001/cancelar.

- **Resultado esperado:**
  - Código HTTP 400 Bad Request

  - error.code: "INVALID_RESERVATION_STATUS"

## ❌ Caso 5: Cancelar reserva finalizada

- **Precondición:** Reserva con estado `finalizada`.

- **Acción:** Ejecutar POST /api/v1/reservas/1001/cancelar.

- **Resultado esperado:**
  - Código HTTP 400 Bad Request

  - error.code: "INVALID_RESERVATION_STATUS"

## ❌ Caso 6: Usuario no propietario intenta cancelar

- **Precondición:** Usuario autenticado con ID 2 intenta cancelar reserva del usuario ID 1.

- **Acción:** Ejecutar POST /api/v1/reservas/1001/cancelar.

- **Resultado esperado:**
  - Código HTTP 403 Forbidden

  - error.code: "FORBIDDEN"

## ❌ Caso 7: Reserva no existe

- **Precondición:** ID de reserva no existe en la base de datos.

- **Acción:** Ejecutar POST /api/v1/reservas/99999/cancelar.

- **Resultado esperado:**
  - Código HTTP 404 Not Found

  - error.code: "RESERVATION_NOT_FOUND"

## ✅ Caso 8: Verificar liberación del vehículo

- **Precondición:** Reserva cancelada.

- **Acción:** Consultar disponibilidad del vehículo en el mismo horario.

- **Resultado esperado:** El vehículo está disponible.

## ✅ Caso 9: Cancelación con pago asociado

- **Precondición:** Reserva tiene un pago aprobado de 5000.

- **Acción:** Cancelar reserva con anticipación suficiente.

- **Resultado esperado:** Se procesa reembolso de 5000.

## ✅ Caso 10: Cancelación sin pago asociado

- **Precondición:** Reserva no tiene pago asociado (estado `pendiente`).

- **Acción:** Cancelar reserva.

- **Resultado esperado:** No hay reembolso que procesar. Solo se cancela la reserva.

## ❌ Caso 11: Token no enviado

- **Precondición:** Ninguna.

- **Acción:** Ejecutar POST /api/v1/reservas/1001/cancelar sin header Authorization.

- **Resultado esperado:**
  - Código HTTP 401 Unauthorized

  - error.code: "UNAUTHORIZED"

## ❌ Caso 12: Error de conexión a base de datos

- **Precondición:** La base de datos no está disponible.

- **Acción:** Ejecutar POST /api/v1/reservas/1001/cancelar bajo condiciones de fallo de BD.

- **Resultado esperado:**
  - Código HTTP 503 Service Unavailable

  - error.code: "DATABASE_ERROR"

## ✅ Definición de Hecho

### Historia: [HU-011] Cancelación de reserva

### 📦 Alcance Funcional

- [ ] El endpoint POST /api/v1/reservas/{id}/cancelar está implementado.
- [ ] Se valida que el usuario sea el propietario de la reserva.
- [ ] Se valida que la reserva exista y tenga estado `pendiente` o `confirmada`.
- [ ] Se calcula correctamente la anticipación de cancelación.
- [ ] Se aplica penalización del 20% si anticipación < 2 horas.
- [ ] No hay penalización si anticipación ≥ 2 horas.
- [ ] Se actualiza el estado a `cancelada`.
- [ ] Se libera el vehículo automáticamente.
- [ ] Se procesa reembolso si existe pago asociado.
- [ ] La respuesta JSON cumple con el contrato definido.

### 🧪 Pruebas Completadas

- [ ] Pruebas unitarias para cálculo de anticipación y penalización.
- [ ] Prueba de integración para cancelación sin penalización.
- [ ] Prueba de integración para cancelación con penalización.
- [ ] Prueba de integración para reserva en curso.
- [ ] Prueba de integración para reserva ya cancelada.
- [ ] Prueba de integración para reserva finalizada.
- [ ] Prueba de integración para usuario no propietario.
- [ ] Prueba de integración para reserva no encontrada.
- [ ] Prueba de integración para cancelación con pago.
- [ ] Prueba de integración para cancelación sin pago.
- [ ] Las pruebas funcionales están documentadas y pasadas.

### 📄 Documentación Técnica

- [ ] Endpoint documentado en Swagger / OpenAPI.
- [ ] Se describe propósito, parámetros, estructura de respuesta, ejemplos.

### 🔐 Manejo de Errores

- [ ] HTTP 400 para estado inválido (INVALID_RESERVATION_STATUS).
- [ ] HTTP 403 para usuario no propietario (FORBIDDEN).
- [ ] HTTP 404 para reserva no encontrada (RESERVATION_NOT_FOUND).
- [ ] HTTP 401 para token no válido (UNAUTHORIZED).
- [ ] HTTP 503 para error de conexión a base de datos (DATABASE_ERROR).
- [ ] Mensajes de error claros.