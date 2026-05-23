# [HU-019] Expiración de código QR

## 📖 Historia de Usuario

**Como** sistema de EcoMove,

**quiero** invalidar automáticamente el código QR después de su primer uso o al finalizar el tiempo de la reserva,

**para** evitar la reutilización indebida del código QR y garantizar la seguridad del sistema.

## 🔁 Flujo Esperado

- El sistema invalida el código QR automáticamente después de **su primer uso** (cuando el usuario escanea para desbloquear el vehículo).
- El sistema invalida el código QR automáticamente al **finalizar el tiempo de la reserva** (cuando la hora actual supera la hora de fin).
- Si un usuario intenta escanear un código ya expirado o ya usado, el sistema rechaza el acceso.
- Cada intento de escaneo (exitoso o fallido) se registra en un log de auditoría.

## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [ ] El sistema invalida el QR automáticamente después del primer uso exitoso.
- [ ] El sistema invalida el QR automáticamente cuando `fecha_expiracion` (10 minutos desde generación) se cumple.
- [ ] El sistema invalida el QR automáticamente cuando la reserva finaliza (`hora_fin` superada).
- [ ] Un QR con `estado = 'usado'` no puede ser utilizado nuevamente.
- [ ] Un QR con `estado = 'expirado'` no puede ser utilizado.
- [ ] Se registra cada intento de escaneo en la tabla `logs_escaneo_qr` con:
  - `qr_id`
  - `usuario_id`
  - `fecha_intento`
  - `resultado` (exitoso, fallido)
  - `motivo` (QR_EXPIRED, QR_ALREADY_USED, RESERVATION_NOT_ACTIVE, etc.)

### 2. 📆 Estructura de la información

- [ ] Cuando un QR expira o se usa, el sistema retorna el siguiente error al intentar validarlo:

~~~json
{
  "success": false,
  "statusCode": 400,
  "message": "Código QR inválido o expirado",
  "error": {
    "code": "QR_INVALID_OR_EXPIRED",
    "details": "El código QR no es válido o ya no está activo"
  }
}
~~~

- [ ] Durante la validación exitosa, la respuesta incluye información del QR:

~~~json
{
  "success": true,
  "statusCode": 200,
  "message": "Código QR válido. Vehículo desbloqueado",
  "data": {
    "reserva_id": 1001,
    "vehiculo_id": 1,
    "vehiculo_modelo": "Scooter Eléctrica X1",
    "valido": true,
    "qr_usado": true,
    "qr_marcado_como_usado": true
  }
}
~~~

### 3. 📝 Logs de auditoría

- [ ] Se registra cada intento de escaneo en la tabla `logs_escaneo_qr`:

~~~json
{
  "id": 1,
  "qr_id": 7001,
  "usuario_id": 1,
  "fecha_intento": "2025-01-15T10:36:30Z",
  "resultado": "exitoso",
  "motivo": null
}
~~~

- [ ] Para intentos fallidos:

~~~json
{
  "id": 2,
  "qr_id": 7001,
  "usuario_id": 2,
  "fecha_intento": "2025-01-15T10:37:00Z",
  "resultado": "fallido",
  "motivo": "QR_ALREADY_USED"
}
~~~

## 🔧 Notas Técnicas

### Reglas de negocio

- El código QR tiene una validez de 10 minutos desde su generación; si no es escaneado en ese lapso, expira y se debe solicitar uno nuevo.
- Cada código QR es único por transacción y solo puede ser escaneado una vez.

### Base de datos (tabla `qrs`)

La tabla debe incluir las siguientes columnas (actualización de HU-017):

- id: SERIAL / AUTO_INCREMENT (PK)
- reserva_id: INT, FK a reservas(id), UNIQUE NOT NULL
- vehiculo_id: INT, FK a vehiculos(id), NOT NULL
- codigo_hash: VARCHAR(255), NOT NULL
- codigo_qr_base64: TEXT, NOT NULL
- estado: ENUM('activo', 'usado', 'expirado'), DEFAULT 'activo'
- fecha_generacion: TIMESTAMP, DEFAULT CURRENT_TIMESTAMP
- fecha_expiracion: TIMESTAMP, NOT NULL
- fecha_uso: TIMESTAMP, NULLABLE

### Base de datos (tabla `logs_escaneo_qr`)

Nueva tabla para auditoría:

- id: SERIAL / AUTO_INCREMENT (PK)
- qr_id: INT, FK a qrs(id)
- usuario_id: INT, FK a usuarios(id)
- fecha_intento: TIMESTAMP, DEFAULT CURRENT_TIMESTAMP
- resultado: ENUM('exitoso', 'fallido'), NOT NULL
- motivo: VARCHAR(100), NULLABLE
- ip_origen: VARCHAR(45), NULLABLE

### Procesos automáticos de expiración

**Opción 1: Job programado (Cron)**

Ejecutar cada minuto un job que actualice:

~~~sql
UPDATE qrs 
SET estado = 'expirado' 
WHERE estado = 'activo' 
AND fecha_expiracion < NOW();
~~~

**Opción 2: Validación en tiempo real**

- En el momento de la validación (HU-018), verificar `fecha_expiracion` vs `NOW()`.
- Si `fecha_expiracion < NOW()`, rechazar y actualizar estado a `expirado`.

- Recomendación: Usar ambas (job para limpieza + validación en tiempo real para seguridad).

### Marcado como usado

En el momento de la validación exitosa (HU-018):

~~~sql
UPDATE qrs 
SET estado = 'usado', fecha_uso = NOW() 
WHERE id = ?;
~~~

### Registro de logs

- Insertar registro en `logs_escaneo_qr` antes de retornar la respuesta.
- Hacerlo dentro de la misma transacción para consistencia.

### Manejo de errores

- Códigos de error sugeridos: `QR_INVALID_OR_EXPIRED`, `QR_ALREADY_USED`, `QR_EXPIRED`.

## 🚀 Endpoint – Validación de código QR (con expiración)

- **Método HTTP:** `POST`
- **Ruta:** `/api/v1/qrs/validar`
- **Headers:** `Authorization: Bearer <token>`

### 📤 Ejemplo de Respuesta JSON Error (QR expirado)

~~~json
{
  "success": false,
  "statusCode": 400,
  "message": "Código QR inválido o expirado",
  "error": {
    "code": "QR_INVALID_OR_EXPIRED",
    "details": "El código QR no es válido o ya no está activo"
  }
}
~~~

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

## ✅ Caso 1: QR se marca como usado después del primer escaneo

- **Precondición:** QR activo, reserva activa.
- **Acción:** Escanear QR exitosamente.
- **Resultado esperado:**
  - estado cambia de `activo` a `usado`
  - `fecha_uso` se setea a `NOW()`
  - Segundo escaneo del mismo QR falla

## ✅ Caso 2: QR expira después de 10 minutos (sin uso)

- **Precondición:** QR generado, no usado.
- **Acción:** Esperar 11 minutos, luego intentar escanear.
- **Resultado esperado:**
  - Validación falla con error `QR_INVALID_OR_EXPIRED`
  - estado cambia (automática o manualmente) a `expirado`

## ✅ Caso 3: QR expira al finalizar la reserva

- **Precondición:** QR válido, reserva termina a las 12:00.
- **Acción:** Intentar escanear a las 12:05.
- **Resultado esperado:**
  - Validación falla
  - estado cambia a `expirado`

## ✅ Caso 4: QR usado no puede ser reutilizado

- **Precondición:** QR con `estado = 'usado'`.
- **Acción:** Intentar escanear el QR nuevamente.
- **Resultado esperado:**
  - Código HTTP 400 Bad Request
  - error.code: "QR_INVALID_OR_EXPIRED"

## ✅ Caso 5: Registro de intento exitoso en logs

- **Precondición:** QR válido.
- **Acción:** Escanear exitosamente.
- **Resultado esperado:** Existe registro en `logs_escaneo_qr` con `resultado = 'exitoso'`.

## ✅ Caso 6: Registro de intento fallido en logs

- **Precondición:** QR expirado.
- **Acción:** Intentar escanear.
- **Resultado esperado:** Existe registro en `logs_escaneo_qr` con `resultado = 'fallido'` y `motivo = 'QR_EXPIRED'`.

## ✅ Caso 7: Job automático de expiración funciona

- **Precondición:** QR con `fecha_expiracion` pasada pero estado aún `activo`.
- **Acción:** Ejecutar job programado.
- **Resultado esperado:** estado cambia a `expirado`.

## ✅ Caso 8: QR expira exactamente a la hora de fin de reserva

- **Precondición:** Reserva de 10:00 a 12:00. QR generado a las 09:50 (expira a las 10:00).
- **Acción:** Intentar escanear a las 10:01.
- **Resultado esperado:** Validación falla (expirado).

## ✅ Caso 9: Múltiples intentos del mismo QR

- **Precondición:** QR válido.
- **Acción:**
  - Primer intento exitoso
  - Segundo intento con mismo QR
- **Resultado esperado:**
  - Primer intento: éxito
  - Segundo intento: error `QR_INVALID_OR_EXPIRED`
  - Ambos intentos registrados en logs

## ✅ Caso 10: Verificar que QR expirado no puede ser reactivado

- **Precondición:** QR con `estado = 'expirado'`.
- **Acción:** Intentar escanear.
- **Resultado esperado:** Error, estado no cambia.

## ❌ Caso 11: Error de conexión a base de datos durante marcado

- **Precondición:** QR válido, pero base de datos falla al actualizar.
- **Acción:** Escanear QR.
- **Resultado esperado:**
  - Transacción se revierte (ROLLBACK)
  - QR permanece `activo`
  - Se retorna error `DATABASE_ERROR`

## ✅ Definición de Hecho

### Historia: [HU-019] Expiración de código QR

### 📦 Alcance Funcional

- [ ] El QR se invalida automáticamente después del primer uso exitoso.
- [ ] El QR se invalida automáticamente cuando `fecha_expiracion` se cumple.
- [ ] El QR se invalida automáticamente cuando la reserva finaliza.
- [ ] Un QR con estado `usado` o `expirado` no puede ser utilizado.
- [ ] Se registra cada intento de escaneo en `logs_escaneo_qr`.
- [ ] La respuesta JSON cumple con el contrato definido.

### 🧪 Pruebas Completadas

- [ ] Prueba de integración para QR marcado como usado.
- [ ] Prueba de integración para QR expirado por tiempo.
- [ ] Prueba de integración para QR expirado por fin de reserva.
- [ ] Prueba de integración para reutilización de QR usado.
- [ ] Prueba de integración para registro de logs exitosos.
- [ ] Prueba de integración para registro de logs fallidos.
- [ ] Prueba de integración para job automático de expiración.
- [ ] Las pruebas funcionales están documentadas y pasadas.

### 📄 Documentación Técnica

- [ ] Endpoint documentado en Swagger / OpenAPI.
- [ ] Se documenta el proceso de expiración automática.
- [ ] Se documenta la tabla `logs_escaneo_qr`.

### 🔐 Manejo de Errores

- [ ] HTTP 400 para QR inválido, expirado o usado (QR_INVALID_OR_EXPIRED).
- [ ] HTTP 503 para error de conexión a base de datos (DATABASE_ERROR).
- [ ] Mensajes de error claros.