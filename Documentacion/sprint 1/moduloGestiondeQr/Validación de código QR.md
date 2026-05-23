# [HU-018] Validación de código QR

## 📖 Historia de Usuario

**Como** usuario de EcoMove,

**quiero** validar el código QR que he escaneado en el vehículo para verificar su autenticidad y vigencia,

**para** poder desbloquear el vehículo si todo es correcto o recibir un mensaje claro si hay algún problema.

## 🔁 Flujo Esperado

- El usuario escanea el código QR del vehículo mediante la aplicación móvil.
- La aplicación envía el código escaneado al endpoint `POST /api/v1/qrs/validar`.
- El sistema verifica la autenticidad del código QR (que haya sido generado por el sistema).
- El sistema verifica la vigencia del código QR (que no haya expirado).
- El sistema verifica que la reserva asociada esté activa.
- Si todas las validaciones son exitosas, el sistema permite desbloquear el vehículo.
- Si alguna validación falla, el sistema retorna un mensaje claro indicando el problema.

## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [ ] Se expone un endpoint `POST /api/v1/qrs/validar` para validar códigos QR.
- [ ] El endpoint recibe el `codigo_qr` escaneado (string).
- [ ] El sistema decodifica y descifra el contenido del QR.
- [ ] El sistema verifica la firma digital para validar autenticidad.
- [ ] El sistema verifica que la fecha actual esté dentro del rango de validez.
- [ ] El sistema verifica que el QR no haya sido usado previamente.
- [ ] El sistema verifica que la reserva asociada esté activa (estado `confirmada` o `en_curso`).
- [ ] El sistema verifica que el usuario que escanea sea el titular de la reserva.
- [ ] Si todas las validaciones son exitosas, se marca el QR como `usado`.
- [ ] Se retorna éxito para que la app desbloquee el vehículo.

### 2. 📆 Estructura de la información

- [ ] Se responde con la siguiente estructura en JSON para validación exitosa:

~~~json
{
  "success": true,
  "statusCode": 200,
  "message": "Código QR válido. Vehículo desbloqueado",
  "data": {
    "reserva_id": 1001,
    "vehiculo_id": 1,
    "vehiculo_modelo": "Scooter Eléctrica X1",
    "valido": true
  }
}
~~~

- [ ] Si el código QR es inválido (firma incorrecta), el sistema retorna:

~~~json
{
  "success": false,
  "statusCode": 400,
  "message": "Código QR inválido",
  "error": {
    "code": "INVALID_QR_CODE",
    "details": "El código QR no ha sido generado por el sistema o ha sido alterado"
  }
}
~~~

- [ ] Si el código QR ha expirado, el sistema retorna:

~~~json
{
  "success": false,
  "statusCode": 400,
  "message": "Código QR expirado",
  "error": {
    "code": "QR_EXPIRED",
    "details": "El código QR ha expirado. Debes solicitar uno nuevo desde la aplicación"
  }
}
~~~

- [ ] Si el código QR ya fue utilizado, el sistema retorna:

~~~json
{
  "success": false,
  "statusCode": 400,
  "message": "Código QR ya utilizado",
  "error": {
    "code": "QR_ALREADY_USED",
    "details": "Este código QR ya fue utilizado para desbloquear el vehículo"
  }
}
~~~

- [ ] Si la reserva no está activa, el sistema retorna:

~~~json
{
  "success": false,
  "statusCode": 400,
  "message": "Reserva no activa",
  "error": {
    "code": "RESERVATION_NOT_ACTIVE",
    "details": "La reserva asociada no está activa. Verifica el estado de tu reserva"
  }
}
~~~

- [ ] Si el usuario no es el titular de la reserva, el sistema retorna:

~~~json
{
  "success": false,
  "statusCode": 403,
  "message": "No autorizado",
  "error": {
    "code": "NOT_RESERVATION_OWNER",
    "details": "Este código QR pertenece a otra reserva. No puedes desbloquear este vehículo"
  }
}
~~~

- [ ] Si el token no es válido o no se envía, el sistema retorna error `UNAUTHORIZED`.

## 🔧 Notas Técnicas

### Reglas de negocio

- El código QR tiene una validez de 10 minutos desde su generación; si no es escaneado en ese lapso, expira.
- Cada código QR es único por transacción y solo puede ser escaneado una vez.

### Flujo de validación

- Recibir código QR escaneado (puede venir como texto plano o como imagen Base64).
- Decodificar el contenido (si viene en Base64) y descifrar usando AES-256 (si se usó cifrado).
- Verificar firma digital: recalcular HMAC-SHA256 con la información excluyendo la firma y comparar con la firma recibida.
- Verificar expiración: comparar `exp` con `NOW()`. Si `exp < NOW()`, QR expirado.
- Verificar no uso previo: consultar tabla `qrs` con `codigo_hash`. Si `estado = 'usado'`, rechazar.
- Verificar reserva activa: el estado debe ser `confirmada` o `en_curso`.
- Verificar titularidad: comparar `usuario_id` de la reserva con `usuario_id` del token JWT.
- Marcar como usado: actualizar `estado = 'usado'` y `fecha_uso = NOW()`.
- Opcional: registrar intentos fallidos en tabla `logs_qr`.

### Base de datos (tabla `qrs`)

- Las columnas necesarias ya están definidas en HU-017.

### Manejo de errores

- Códigos de error sugeridos: `INVALID_QR_CODE`, `QR_EXPIRED`, `QR_ALREADY_USED`, `RESERVATION_NOT_ACTIVE`, `NOT_RESERVATION_OWNER`, `UNAUTHORIZED`.

## 🚀 Endpoint – Validación de código QR

- **Método HTTP:** `POST`
- **Ruta:** `/api/v1/qrs/validar`
- **Headers:** `Authorization: Bearer <token>`

### 📤 Ejemplo de Request JSON

~~~json
{
  "codigo_qr": "iVBORw0KGgoAAAANSUhEUgAA...",
  "tipo": "base64"
}
~~~

### 📤 Ejemplo de Respuesta JSON Exitosa

~~~json
{
  "success": true,
  "statusCode": 200,
  "message": "Código QR válido. Vehículo desbloqueado",
  "data": {
    "reserva_id": 1001,
    "vehiculo_id": 1,
    "vehiculo_modelo": "Scooter Eléctrica X1",
    "valido": true
  }
}
~~~

### 📤 Ejemplo de Respuesta JSON Error (QR expirado)

~~~json
{
  "success": false,
  "statusCode": 400,
  "message": "Código QR expirado",
  "error": {
    "code": "QR_EXPIRED",
    "details": "El código QR ha expirado. Debes solicitar uno nuevo desde la aplicación"
  }
}
~~~

### 📤 Ejemplo de Respuesta JSON Error (Usuario no autorizado)

~~~json
{
  "success": false,
  "statusCode": 403,
  "message": "No autorizado",
  "error": {
    "code": "NOT_RESERVATION_OWNER",
    "details": "Este código QR pertenece a otra reserva. No puedes desbloquear este vehículo"
  }
}
~~~

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

## ✅ Caso 1: Validación exitosa de QR

- **Precondición:** QR válido, no expirado, no usado, reserva activa, usuario titular.
- **Acción:** Ejecutar POST /api/v1/qrs/validar con el QR.
- **Resultado esperado:**
  - Código HTTP 200 OK
  - success: true
  - valido: true
  - QR se marca como `usado` en base de datos

## ❌ Caso 2: QR inválido (firma incorrecta)

- **Precondición:** QR alterado manualmente (firma no coincide).
- **Acción:** Ejecutar POST /api/v1/qrs/validar.
- **Resultado esperado:**
  - Código HTTP 400 Bad Request
  - error.code: "INVALID_QR_CODE"

## ❌ Caso 3: QR expirado

- **Precondición:** QR generado hace más de 10 minutos.
- **Acción:** Ejecutar POST /api/v1/qrs/validar.
- **Resultado esperado:**
  - Código HTTP 400 Bad Request
  - error.code: "QR_EXPIRED"

## ❌ Caso 4: QR ya usado

- **Precondición:** QR ya fue escaneado previamente.
- **Acción:** Intentar escanear el mismo QR nuevamente.
- **Resultado esperado:**
  - Código HTTP 400 Bad Request
  - error.code: "QR_ALREADY_USED"

## ❌ Caso 5: Reserva no activa

- **Precondición:** Reserva asociada al QR tiene estado `cancelada` o `finalizada`.
- **Acción:** Ejecutar POST /api/v1/qrs/validar.
- **Resultado esperado:**
  - Código HTTP 400 Bad Request
  - error.code: "RESERVATION_NOT_ACTIVE"

## ❌ Caso 6: Usuario no es titular de la reserva

- **Precondición:** Usuario autenticado con ID 2 escanea QR de reserva del usuario ID 1.
- **Acción:** Ejecutar POST /api/v1/qrs/validar.
- **Resultado esperado:**
  - Código HTTP 403 Forbidden
  - error.code: "NOT_RESERVATION_OWNER"

## ❌ Caso 7: QR con formato inválido

- **Precondición:** El string enviado no es un QR válido.
- **Acción:** Ejecutar POST /api/v1/qrs/validar con texto aleatorio.
- **Resultado esperado:**
  - Código HTTP 400 Bad Request
  - error.code: "INVALID_QR_CODE"

## ✅ Caso 8: Verificar que QR no puede usarse dos veces

- **Precondición:** QR validado exitosamente la primera vez.
- **Acción:** Intentar validar el mismo QR nuevamente.
- **Resultado esperado:**
  - Primer intento: exitoso
  - Segundo intento: error `QR_ALREADY_USED`

## ✅ Caso 9: Verificar que se marca como usado

- **Precondición:** QR validado exitosamente.
- **Acción:** Consultar la tabla `qrs`.
- **Resultado esperado:** `estado = 'usado'` y `fecha_uso` no es NULL.

## ❌ Caso 10: Token no enviado

- **Precondición:** Ninguna.
- **Acción:** Ejecutar POST /api/v1/qrs/validar sin header Authorization.
- **Resultado esperado:**
  - Código HTTP 401 Unauthorized
  - error.code: "UNAUTHORIZED"

## ✅ Caso 11: Validación antes del horario de inicio

- **Precondición:** QR válido, pero hora actual es 09:30 y la reserva inicia a las 10:00.
- **Acción:** Escanear QR.
- **Resultado esperado:** Depende de regla de negocio. Si se permite acceso anticipado, OK; si no, error.

## ❌ Caso 12: Error de conexión a base de datos

- **Precondición:** La base de datos no está disponible.
- **Acción:** Ejecutar POST /api/v1/qrs/validar bajo condiciones de fallo de BD.
- **Resultado esperado:**
  - Código HTTP 503 Service Unavailable
  - error.code: "DATABASE_ERROR"

## ✅ Definición de Hecho

### Historia: [HU-018] Validación de código QR

### 📦 Alcance Funcional

- [ ] Se expone un endpoint POST /api/v1/qrs/validar para validar QR.
- [ ] Se verifica la autenticidad del QR (firma digital).
- [ ] Se verifica la vigencia del QR (no expirado).
- [ ] Se verifica que el QR no haya sido usado previamente.
- [ ] Se verifica que la reserva asociada esté activa.
- [ ] Se verifica que el usuario sea el titular de la reserva.
- [ ] Si todo es correcto, se marca el QR como `usado`.
- [ ] La respuesta JSON cumple con el contrato definido.

### 🧪 Pruebas Completadas

- [ ] Prueba de integración para validación exitosa.
- [ ] Prueba de integración para QR inválido.
- [ ] Prueba de integración para QR expirado.
- [ ] Prueba de integración para QR ya usado.
- [ ] Prueba de integración para reserva no activa.
- [ ] Prueba de integración para usuario no titular.
- [ ] Prueba de integración para formato inválido.
- [ ] Prueba de integración para token no enviado.
- [ ] Las pruebas funcionales están documentadas y pasadas.

### 📄 Documentación Técnica

- [ ] Endpoint documentado en Swagger / OpenAPI.
- [ ] Se describe el proceso de validación paso a paso.

### 🔐 Manejo de Errores

- [ ] HTTP 400 para QR inválido, expirado, usado o reserva inactiva.
- [ ] HTTP 403 para usuario no titular (NOT_RESERVATION_OWNER).
- [ ] HTTP 401 para token no válido (UNAUTHORIZED).
- [ ] HTTP 503 para error de conexión a base de datos (DATABASE_ERROR).
- [ ] Mensajes de error claros.