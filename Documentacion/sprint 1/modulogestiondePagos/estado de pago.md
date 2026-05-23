# [HU-016] Notificación del estado de pago

## 📖 Historia de Usuario

**Como** usuario de EcoMove,

**quiero** recibir una notificación del resultado del pago que acabo de realizar,

**para** saber si puedo continuar con el uso del servicio o si debo realizar alguna acción adicional.

## 🔁 Flujo Esperado

- Después de procesar un pago (exitoso o rechazado), el sistema genera una notificación.
- El usuario recibe un mensaje visible en la misma interfaz (respuesta síncrona).
- El sistema envía una notificación al correo electrónico registrado del usuario.
- La notificación incluye los detalles de la transacción: monto, fecha, reserva asociada y estado.
- Si el pago es rechazado, la notificación indica el motivo del rechazo y ofrece la opción de reintentar.

## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [ ] Después de procesar un pago, el sistema genera una notificación.
- [ ] La notificación síncrona se entrega en la respuesta HTTP inmediata (JSON).
- [ ] El sistema envía una notificación asíncrona al correo electrónico del usuario.
- [ ] La notificación incluye: estado del pago, monto, fecha, reserva_id, método de pago.
- [ ] Si el pago es rechazado, la notificación incluye motivo del rechazo.
- [ ] Si el pago es rechazado, se sugiere reintentar con otro método de pago.
- [ ] El envío del correo no debe bloquear la respuesta HTTP (procesamiento asíncrono).

### 2. 📆 Estructura de la información

- [ ] Para pago exitoso, la respuesta incluye notificación en `data`:

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
    "notificacion": {
      "enviada": true,
      "mensaje": "Tu pago ha sido aprobado. Ya puedes acceder al vehículo."
    }
  }
}
~~~

- [ ] Para pago rechazado, el sistema retorna:

~~~json
{
  "success": false,
  "statusCode": 400,
  "message": "Pago rechazado",
  "error": {
    "code": "PAYMENT_REJECTED",
    "details": "La transacción fue rechazada por la pasarela de pagos",
    "motivo": "Fondos insuficientes"
  },
  "notificacion": {
    "enviada": true,
    "mensaje": "Tu pago fue rechazado. Puedes reintentar con otro método de pago."
  }
}
~~~

### 3. 📧 Notificación por correo electrónico

- [ ] El correo debe enviarse a la dirección registrada del usuario.
- [ ] El correo debe incluir:
  - Asunto: "Resultado de tu pago en EcoMove"
  - Cuerpo: detalles de la transacción (monto, fecha, reserva, estado)
  - Si es rechazado: motivo y enlace para reintentar
- [ ] El envío del correo es asíncrono (no bloquea la respuesta HTTP).
- [ ] Si el envío falla, se registra en logs pero no afecta la respuesta al usuario.

## 🔧 Notas Técnicas

### Reglas de negocio

- Los pagos no son reembolsables una vez que el usuario ha iniciado el viaje.
- El sistema aplica una tarifa mínima por viaje equivalente a 60 minutos de uso.

### Notificación síncrona (respuesta HTTP)

- La notificación debe incluirse en la misma respuesta del endpoint `POST /api/v1/pagos`.
- No requiere infraestructura adicional.

### Notificación asíncrona (correo electrónico)

- Usar un sistema de colas (RabbitMQ, Redis, o similar) para no bloquear la respuesta.
- O implementar un worker en segundo plano (background job).
- Usar un servicio de envío de correos (SendGrid, AWS SES, Nodemailer, etc.).

### Estructura del correo electrónico

- **Asunto:** `EcoMove - Resultado de tu pago #{pago_id}`

- **Cuerpo (pago exitoso):**

~~~text
Hola {nombre_usuario},

Tu pago ha sido procesado exitosamente.

Detalles de la transacción:
- Reserva ID: {reserva_id}
- Monto: ${monto}
- Fecha: {fecha_pago}
- Método de pago: {metodo_pago}
- Estado: APROBADO

Ya puedes acceder al vehículo escaneando el código QR.

Gracias por usar EcoMove.
~~~

- **Cuerpo (pago rechazado):**

~~~text
Hola {nombre_usuario},

Tu pago ha sido rechazado.

Detalles de la transacción:
- Reserva ID: {reserva_id}
- Monto: ${monto}
- Fecha: {fecha_pago}
- Método de pago: {metodo_pago}
- Estado: RECHAZADO
- Motivo: {motivo_rechazo}

Puedes reintentar el pago desde la aplicación.

Gracias por usar EcoMove.
~~~

### Manejo de errores en envío de correos

- Si falla el envío, registrar error en logs.
- No reintentar automáticamente (puede implementarse después).
- La respuesta al usuario no debe fallar por errores de correo.

### Manejo de errores

- Códigos de error sugeridos: `EMAIL_SEND_FAILED` (solo para logs, no para respuesta).

## 🚀 Endpoint – Procesamiento de pago (con notificación)

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

### 📤 Ejemplo de Respuesta JSON Exitosa (con notificación)

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
    "notificacion": {
      "enviada": true,
      "mensaje": "Tu pago ha sido aprobado. Ya puedes acceder al vehículo."
    }
  }
}
~~~

### 📤 Ejemplo de Respuesta JSON Error (Pago rechazado con notificación)

~~~json
{
  "success": false,
  "statusCode": 400,
  "message": "Pago rechazado",
  "error": {
    "code": "PAYMENT_REJECTED",
    "details": "La transacción fue rechazada por la pasarela de pagos",
    "motivo": "Fondos insuficientes"
  },
  "notificacion": {
    "enviada": true,
    "mensaje": "Tu pago fue rechazado. Puedes reintentar con otro método de pago."
  }
}
~~~

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

## ✅ Caso 1: Notificación síncrona en pago exitoso

- **Precondición:** Pago procesado exitosamente.
- **Acción:** Ejecutar POST /api/v1/pagos.
- **Resultado esperado:**
  - La respuesta incluye `notificacion` con `enviada: true`
  - `notificacion.mensaje` indica que el pago fue aprobado

## ✅ Caso 2: Notificación síncrona en pago rechazado

- **Precondición:** Pago procesado con rechazo.
- **Acción:** Ejecutar POST /api/v1/pagos.
- **Resultado esperado:**
  - La respuesta incluye `notificacion` con `enviada: true`
  - `notificacion.mensaje` sugiere reintentar

## ✅ Caso 3: Envío de correo para pago exitoso

- **Precondición:** Pago procesado exitosamente. Usuario tiene email registrado.
- **Acción:** Procesar pago.
- **Resultado esperado:**
  - Se envía correo al email del usuario
  - El correo contiene los detalles de la transacción
  - El estado del correo es "aprobado"

## ✅ Caso 4: Envío de correo para pago rechazado

- **Precondición:** Pago procesado con rechazo.
- **Acción:** Procesar pago.
- **Resultado esperado:**
  - Se envía correo al email del usuario
  - El correo incluye el motivo del rechazo
  - El correo sugiere reintentar

## ✅ Caso 5: El envío de correo no bloquea la respuesta

- **Precondición:** El servicio de correo tarda 5 segundos en responder.
- **Acción:** Procesar pago.
- **Resultado esperado:**
  - La respuesta HTTP se recibe en menos de 1 segundo
  - El correo se envía en segundo plano (asíncrono)

## ❌ Caso 6: Error en envío de correo (no afecta respuesta)

- **Precondición:** El servicio de correo falla.
- **Acción:** Procesar pago.
- **Resultado esperado:**
  - La respuesta HTTP es exitosa (200 o 400 según el pago)
  - El error se registra en logs
  - El usuario no recibe correo (se puede reintentar después)

## ✅ Caso 7: Verificar contenido del correo

- **Precondición:** Pago exitoso con monto = 5000, reserva_id = 1001.
- **Acción:** Procesar pago y revisar correo enviado.
- **Resultado esperado:**
  - Asunto contiene "EcoMove - Resultado de tu pago"
  - Cuerpo contiene "Monto: 5000"
  - Cuerpo contiene "Reserva ID: 1001"
  - Cuerpo contiene "Estado: APROBADO"

## ✅ Caso 8: Verificar contenido del correo para pago rechazado

- **Precondición:** Pago rechazado con motivo "Fondos insuficientes".
- **Acción:** Procesar pago y revisar correo enviado.
- **Resultado esperado:**
  - Cuerpo contiene "Estado: RECHAZADO"
  - Cuerpo contiene "Motivo: Fondos insuficientes"
  - Cuerpo contiene "Puedes reintentar el pago"

## ❌ Caso 9: Usuario sin email registrado (borde)

- **Precondición:** Usuario no tiene email en su perfil (caso extremo).
- **Acción:** Procesar pago.
- **Resultado esperado:**
  - La respuesta HTTP es exitosa
  - Se registra error en logs indicando que no se pudo enviar el correo por falta de email

## ✅ Caso 10: Notificación incluye método de pago

- **Precondición:** Pago con `metodo_pago = "tarjeta_credito"`.
- **Acción:** Procesar pago y revisar respuesta.
- **Resultado esperado:** La notificación (respuesta y correo) incluye el método de pago.

## ✅ Definición de Hecho

### Historia: [HU-016] Notificación del estado de pago

### 📦 Alcance Funcional

- [ ] Después de procesar un pago, se genera notificación síncrona en la respuesta HTTP.
- [ ] La notificación incluye estado, monto, fecha, reserva_id.
- [ ] Si el pago es rechazado, la notificación incluye motivo.
- [ ] Si el pago es rechazado, se sugiere reintentar.
- [ ] Se envía notificación asíncrona al correo del usuario.
- [ ] El correo incluye todos los detalles de la transacción.
- [ ] El envío del correo no bloquea la respuesta HTTP.
- [ ] La respuesta JSON cumple con el contrato definido.

### 🧪 Pruebas Completadas

- [ ] Prueba de integración para notificación síncrona en pago exitoso.
- [ ] Prueba de integración para notificación síncrona en pago rechazado.
- [ ] Prueba de integración para envío de correo en pago exitoso.
- [ ] Prueba de integración para envío de correo en pago rechazado.
- [ ] Prueba de integración para asincronía del envío de correo.
- [ ] Prueba de integración para error en envío de correo (logs).
- [ ] Las pruebas funcionales están documentadas y pasadas.

### 📄 Documentación Técnica

- [ ] Endpoint documentado en Swagger / OpenAPI.
- [ ] Se documenta la estructura de la notificación.
- [ ] Se documenta el servicio de correo y su configuración.

### 🔐 Manejo de Errores

- [ ] El error en envío de correo no afecta la respuesta HTTP.
- [ ] Los errores de correo se registran en logs.
- [ ] Mensajes de notificación claros y útiles para el usuario.