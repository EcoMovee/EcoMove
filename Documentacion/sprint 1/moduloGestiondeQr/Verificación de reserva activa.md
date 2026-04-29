# [HU-020] Verificación de reserva activa

## 📖 Historia de Usuario

**Como** sistema de EcoMove,

**quiero** verificar que la reserva asociada al código QR esté activa antes de permitir el acceso al vehículo,

**para** garantizar que solo el usuario legítimo pueda acceder al vehículo correcto en el momento adecuado.

## 🔁 Flujo Esperado

- El usuario escanea el código QR del vehículo mediante la aplicación móvil.
- El sistema valida el código QR (autenticidad, vigencia, no uso previo).
- El sistema verifica que la reserva asociada tenga estado `confirmada` o `en_curso`.
- El sistema verifica que la reserva no haya sido cancelada por el usuario o administrador.
- El sistema verifica que el usuario que escanea sea el mismo usuario titular de la reserva.
- El sistema verifica que el vehículo asociado a la reserva coincida con el vehículo físico en el que se está escaneando.
- Si todas las condiciones se cumplen, se permite el acceso y se desbloquea el vehículo.

## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [ ] Se verifica que la reserva asociada al QR exista en la tabla `reservas`.
- [ ] Se verifica que el estado de la reserva sea `confirmada` o `en_curso`.
- [ ] Si el estado es `cancelada` o `finalizada`, se rechaza el acceso.
- [ ] Se verifica que el usuario autenticado sea el `usuario_id` de la reserva.
- [ ] Se verifica que el `vehiculo_id` de la reserva coincida con el `vehiculo_id` del QR.
- [ ] Si el vehículo no coincide, se rechaza el acceso.
- [ ] Si la reserva está en estado `confirmada`, se puede actualizar a `en_curso` al momento del desbloqueo.
- [ ] Se retorna éxito para que la aplicación desbloquee el vehículo.

### 2. 📆 Estructura de la información

- [ ] Se responde con la siguiente estructura en JSON para verificación exitosa:

~~~json
{
  "success": true,
  "statusCode": 200,
  "message": "Reserva activa. Vehículo desbloqueado",
  "data": {
    "reserva_id": 1001,
    "vehiculo_id": 1,
    "vehiculo_modelo": "Scooter Eléctrica X1",
    "estado_reserva": "en_curso",
    "inicio_reserva": "2025-01-20T10:00:00Z",
    "fin_reserva": "2025-01-20T12:00:00Z"
  }
}
~~~

- [ ] Si la reserva fue cancelada, el sistema retorna:

~~~json
{
  "success": false,
  "statusCode": 400,
  "message": "Reserva cancelada",
  "error": {
    "code": "RESERVATION_CANCELLED",
    "details": "Esta reserva ha sido cancelada y no permite acceso al vehículo"
  }
}
~~~

- [ ] Si la reserva ya finalizó, el sistema retorna:

~~~json
{
  "success": false,
  "statusCode": 400,
  "message": "Reserva finalizada",
  "error": {
    "code": "RESERVATION_FINISHED",
    "details": "Esta reserva ya ha finalizado. No se puede acceder al vehículo"
  }
}
~~~

- [ ] Si el vehículo no coincide, el sistema retorna:

~~~json
{
  "success": false,
  "statusCode": 400,
  "message": "Vehículo incorrecto",
  "error": {
    "code": "VEHICLE_MISMATCH",
    "details": "El código QR no corresponde al vehículo que estás intentando desbloquear"
  }
}
~~~

- [ ] Si el usuario no es el titular, el sistema retorna error `NOT_RESERVATION_OWNER`.

## 🔧 Notas Técnicas

### Reglas de negocio

- Un usuario con una reserva en curso o con un viaje activo no puede ser dado de baja del sistema.
- El tiempo máximo de reserva antes de iniciar el viaje es de 15 minutos; pasado este tiempo, la reserva se cancela automáticamente.

### Base de datos (tabla `reservas`)

La tabla debe incluir las siguientes columnas:

- id: SERIAL / AUTO_INCREMENT (PK)
- usuario_id: INT, FK a usuarios(id)
- vehiculo_id: INT, FK a vehiculos(id)
- fecha: DATE, NOT NULL
- hora_inicio: TIME, NOT NULL
- hora_fin: TIME, NOT NULL
- estado: ENUM('pendiente', 'confirmada', 'en_curso', 'finalizada', 'cancelada'), DEFAULT 'pendiente'
- fecha_creacion: TIMESTAMP, DEFAULT CURRENT_TIMESTAMP
- fecha_confirmacion: TIMESTAMP, NULLABLE
- fecha_inicio_viaje: TIMESTAMP, NULLABLE
- fecha_fin_viaje: TIMESTAMP, NULLABLE

### Flujo de verificación

- Obtener datos del QR validado (después de HU-018).
- Consultar la reserva en la tabla `reservas`.
- Verificar estado:
  - `confirmada` → OK (se puede actualizar a `en_curso`)
  - `en_curso` → OK
  - `cancelada` → Error `RESERVATION_CANCELLED`
  - `finalizada` → Error `RESERVATION_FINISHED`
  - `pendiente` → Error (debería estar pagada)
- Verificar titularidad: comparar `reserva.usuario_id` con `token.usuario_id`.
- Verificar coincidencia del vehículo: comparar `reserva.vehiculo_id` con `qr.vehiculo_id`.
- Opcional: recibir `vehiculo_id` desde la app para validación extra.

### Actualización de estado a `en_curso`

Si la reserva está en `confirmada`, actualizar a `en_curso`:

~~~sql
UPDATE reservas 
SET estado = 'en_curso', fecha_inicio_viaje = NOW() 
WHERE id = ?;
~~~

### Transacciones

Usar transacción para:

- Verificar reserva.
- Actualizar estado a `en_curso`.
- Marcar QR como usado (HU-019).
- Registrar log de acceso.

### Manejo de errores

- Códigos de error sugeridos: `RESERVATION_CANCELLED`, `RESERVATION_FINISHED`, `VEHICLE_MISMATCH`, `NOT_RESERVATION_OWNER`.

## 🚀 Endpoint – Validación de código QR (con verificación de reserva)

- **Método HTTP:** `POST`
- **Ruta:** `/api/v1/qrs/validar`
- **Headers:** `Authorization: Bearer <token>`

### 📤 Ejemplo de Respuesta JSON Exitosa (Reserva confirmada → en_curso)

~~~json
{
  "success": true,
  "statusCode": 200,
  "message": "Reserva activa. Vehículo desbloqueado",
  "data": {
    "reserva_id": 1001,
    "vehiculo_id": 1,
    "vehiculo_modelo": "Scooter Eléctrica X1",
    "estado_reserva": "en_curso",
    "inicio_reserva": "2025-01-20T10:00:00Z",
    "fin_reserva": "2025-01-20T12:00:00Z"
  }
}
~~~

### 📤 Ejemplo de Respuesta JSON Error (Reserva cancelada)

~~~json
{
  "success": false,
  "statusCode": 400,
  "message": "Reserva cancelada",
  "error": {
    "code": "RESERVATION_CANCELLED",
    "details": "Esta reserva ha sido cancelada y no permite acceso al vehículo"
  }
}
~~~

### 📤 Ejemplo de Respuesta JSON Error (Vehículo no coincide)

~~~json
{
  "success": false,
  "statusCode": 400,
  "message": "Vehículo incorrecto",
  "error": {
    "code": "VEHICLE_MISMATCH",
    "details": "El código QR no corresponde al vehículo que estás intentando desbloquear"
  }
}
~~~

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

## ✅ Caso 1: Reserva confirmada - acceso exitoso

- **Precondición:** QR válido, reserva existe, estado `confirmada`, usuario titular, vehículo coincide.
- **Acción:** Escanear QR.
- **Resultado esperado:**
  - Código HTTP 200 OK
  - `estado_reserva` cambia a `en_curso`
  - `fecha_inicio_viaje` se setea a `NOW()`
  - Vehículo desbloqueado

## ✅ Caso 2: Reserva en curso - acceso exitoso

- **Precondición:** Reserva con estado `en_curso`, usuario ya está usando el vehículo.
- **Acción:** Escanear QR nuevamente (por si acaso).
- **Resultado esperado:**
  - Código HTTP 200 OK
  - Estado permanece `en_curso`
  - Acceso permitido

## ❌ Caso 3: Reserva cancelada - acceso denegado

- **Precondición:** Reserva con estado `cancelada`.
- **Acción:** Escanear QR.
- **Resultado esperado:**
  - Código HTTP 400 Bad Request
  - error.code: "RESERVATION_CANCELLED"

## ❌ Caso 4: Reserva finalizada - acceso denegado

- **Precondición:** Reserva con estado `finalizada`.
- **Acción:** Escanear QR.
- **Resultado esperado:**
  - Código HTTP 400 Bad Request
  - error.code: "RESERVATION_FINISHED"

## ❌ Caso 5: Reserva pendiente (sin pago) - acceso denegado

- **Precondición:** Reserva con estado `pendiente`.
- **Acción:** Escanear QR.
- **Resultado esperado:**
  - Código HTTP 400 Bad Request
  - Mensaje indicando que debe pagar la reserva

## ❌ Caso 6: Vehículo no coincide

- **Precondición:** QR contiene vehiculo_id = 1, pero el vehículo físico tiene vehiculo_id = 2.
- **Acción:** Escanear QR.
- **Resultado esperado:**
  - Código HTTP 400 Bad Request
  - error.code: "VEHICLE_MISMATCH"

## ❌ Caso 7: Usuario no es titular de la reserva

- **Precondición:** Usuario autenticado con ID 2 escanea QR de reserva del usuario ID 1.
- **Acción:** Escanear QR.
- **Resultado esperado:**
  - Código HTTP 403 Forbidden
  - error.code: "NOT_RESERVATION_OWNER"

## ✅ Caso 8: Verificar actualización de estado a en_curso

- **Precondición:** Reserva `confirmada`.
- **Acción:** Escaneo exitoso.
- **Resultado esperado:** En la base de datos, `estado = 'en_curso'` y `fecha_inicio_viaje` no es NULL.

## ❌ Caso 9: Acceso después de la hora de fin

- **Precondición:** Reserva `confirmada`, pero `NOW() > hora_fin`.
- **Acción:** Escanear QR.
- **Resultado esperado:**
  - Código HTTP 400 Bad Request
  - error.code: "RESERVATION_FINISHED" o similar

## ✅ Caso 10: Verificar que se registra el inicio del viaje

- **Precondición:** Acceso exitoso.
- **Acción:** Consultar la tabla `reservas`.
- **Resultado esperado:** `fecha_inicio_viaje` es la fecha y hora del escaneo.

## ❌ Caso 11: Error de conexión a base de datos

- **Precondición:** La base de datos no está disponible.
- **Acción:** Escanear QR bajo condiciones de fallo de BD.
- **Resultado esperado:**
  - Código HTTP 503 Service Unavailable
  - error.code: "DATABASE_ERROR"

## ✅ Definición de Hecho

### Historia: [HU-020] Verificación de reserva activa

### 📦 Alcance Funcional

- [ ] Se verifica que la reserva asociada al QR exista.
- [ ] Se verifica que el estado de la reserva sea `confirmada` o `en_curso`.
- [ ] Se rechaza acceso si estado es `cancelada` o `finalizada`.
- [ ] Se verifica que el usuario sea el titular de la reserva.
- [ ] Se verifica que el vehículo asociado coincida.
- [ ] Si la reserva está en `confirmada`, se actualiza a `en_curso`.
- [ ] Se registra `fecha_inicio_viaje`.
- [ ] La respuesta JSON cumple con el contrato definido.

### 🧪 Pruebas Completadas

- [ ] Prueba de integración para reserva `confirmada` → acceso exitoso.
- [ ] Prueba de integración para reserva `en_curso` → acceso exitoso.
- [ ] Prueba de integración para reserva `cancelada`.
- [ ] Prueba de integración para reserva `finalizada`.
- [ ] Prueba de integración para reserva `pendiente`.
- [ ] Prueba de integración para vehículo no coincide.
- [ ] Prueba de integración para usuario no titular.
- [ ] Prueba de integración para acceso después de hora de fin.
- [ ] Las pruebas funcionales están documentadas y pasadas.

### 📄 Documentación Técnica

- [ ] Endpoint documentado en Swagger / OpenAPI.
- [ ] Se describe el flujo completo de verificación.

### 🔐 Manejo de Errores

- [ ] HTTP 400 para reserva cancelada, finalizada, vehículo no coincide.
- [ ] HTTP 403 para usuario no titular (NOT_RESERVATION_OWNER).
- [ ] HTTP 503 para error de conexión a base de datos (DATABASE_ERROR).
- [ ] Mensajes de error claros.