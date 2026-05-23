# [HU-003] Actualización de perfil

## 📖 Historia de Usuario

**Como** usuario autenticado de EcoMove,

**quiero** actualizar mis datos personales (nombre, teléfono y opcionalmente mi contraseña),

**para** mantener mi información actualizada y segura dentro del sistema.

## 🔁 Flujo Esperado

- El usuario autenticado envía sus nuevos datos al endpoint `PUT /api/v1/usuarios/{id}`.

- El sistema valida que el ID del usuario en la URL coincida con el ID del token JWT.

- El sistema valida que los campos enviados cumplan con los formatos requeridos.

- Si el usuario envía una nueva contraseña, el sistema verifica la contraseña actual.

- Si la contraseña actual es correcta, el sistema encripta la nueva contraseña con bcrypt.

- El sistema actualiza los datos en la tabla `usuarios`.

- El sistema registra la modificación en un historial de auditoría.

- El sistema retorna los datos actualizados del usuario.

## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [ ] Se expone un endpoint `PUT /api/v1/usuarios/{id}` para actualizar perfil.

- [ ] Se valida que el ID del usuario en la URL coincida con el `id` del token JWT (solo puede modificar su propio perfil).

- [ ] Se valida que el usuario exista y esté activo (`estado = true`).

- [ ] Se permite actualizar los campos: `nombre`, `telefono`.

- [ ] No se permite actualizar el campo `email` en este endpoint.

- [ ] Opcionalmente se permite actualizar la `password` enviando `contrasena_actual` y `nueva_contrasena`.

- [ ] Se valida que la `contrasena_actual` sea correcta usando `bcrypt.compare()`.

- [ ] La `nueva_contrasena` debe cumplir con los requisitos de seguridad.

- [ ] Si la nueva contraseña es válida, se encripta con bcrypt antes de guardar.

- [ ] Se registra cada modificación en una tabla de auditoría.

### 2. 📆 Estructura de la información

- [ ] Se responde con la siguiente estructura en JSON para actualización exitosa:

```json
{
  "success": true,
  "statusCode": 200,
  "message": "Usuario actualizado correctamente",
  "data": {
    "id": 1,
    "nombre": "Juan Carlos Perez",
    "email": "juan@example.com",
    "telefono": "+573001234567",
    "rol": "usuario"
  }
}
```

- [ ]  Si el usuario no existe, el sistema retorna:

```json
{
  "success": false,
  "statusCode": 404,
  "message": "Usuario no encontrado",
  "error": {
    "code": "USER_NOT_FOUND",
    "details": "No existe un usuario con el ID proporcionado"
  }
}
```
- [ ]   Si se intenta actualizar el email, el sistema retorna:

```json
{
  "success": false,
  "statusCode": 400,
  "message": "No se puede actualizar el email",
  "error": {
    "code": "EMAIL_UPDATE_NOT_ALLOWED",
    "details": "El email no puede ser modificado. Contacte al administrador"
  }
}
```
- [ ]   Si la contraseña actual es incorrecta, el sistema retorna:

```json
{
  "success": false,
  "statusCode": 400,
  "message": "Contraseña actual incorrecta",
  "error": {
    "code": "INVALID_CURRENT_PASSWORD",
    "details": "La contraseña actual no coincide con nuestros registros"
  }
}
```
## 3. 📝 Auditoría de cambios

- Se registra en una tabla auditoria_perfil:
  - usuario_id
  - campo_modificado (nombre, telefono, contrasena)
  - valor_anterior
  - valor_nuevo
  - fecha_modificacion (TIMESTAMP)

- Si el usuario cambia el mismo valor que ya tenía, no se registra auditoría.

## 🔧 Notas Técnicas

### Reglas de negocio
- Un usuario con una reserva en curso o con un viaje activo no puede ser dado de baja del sistema. Esto aplica para desactivación, no para actualización de perfil.

### Base de datos (tabla `usuarios`)
- Tabla usuarios (misma que HU-001 y HU-002)
- Tabla auditoria_perfil:
  - id: SERIAL (PK)
  - usuario_id: INT, FK a usuarios(id)
  - campo_modificado: VARCHAR(50)
  - valor_anterior: TEXT
  - valor_nuevo: TEXT
  - fecha_modificacion: TIMESTAMP, DEFAULT   CURRENT_TIMESTAMP

### Seguridad
- El endpoint debe estar protegido con JWT (header: Authorization: Bearer <token>).
- No se debe permitir actualizar rol, email, estado desde este endpoint.
- La contraseña actual solo se necesita si se va a cambiar la contraseña.

### Manejo de errores
- Códigos de error sugeridos: USER_NOT_FOUND, EMAIL_UPDATE_NOT_ALLOWED, INVALID_CURRENT_PASSWORD, INVALID_DATA.

## 🚀 Endpoint – Actualización de perfil

- **Método HTTP:** `PUT`

- **Ruta:** `/api/v1/usuarios/{id}`

- **Headers:** Authorization: Bearer <token>

📤 Ejemplo de Request JSON

```json
{
  "nombre": "Juan Carlos Perez",
  "telefono": "+573001234567",
  "contrasena_actual": "Pass123!",
  "nueva_contrasena": "NewPass456!"
}
```
📤 Ejemplo de Respuesta JSON Exitosa

```json
{
  "success": true,
  "statusCode": 200,
  "message": "Usuario actualizado correctamente",
  "data": {
    "id": 1,
    "nombre": "Juan Carlos Perez",
    "email": "juan@example.com",
    "telefono": "+573001234567",
    "rol": "usuario"
  }
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

## ✅ Caso 1: Actualización exitosa de nombre y teléfono

- **Precondición:**  Usuario autenticado con token válido.

- **Acción:** Ejecutar PUT /api/v1/usuarios/1 con nuevo nombre y teléfono.

- **Resultado esperado:**

- Código HTTP 200 OK

- success: true

- statusCode: 200

- Los datos se actualizan en la tabla usuarios

- Se registra auditoría


## ✅ Caso 2: Cambio de contraseña exitoso

- **Precondición:** Usuario autenticado, contrasena_actual correcta.

- **Acción:** Enviar contrasena_actual y nueva_contrasena válida.

- **Resultado esperado:**

- Código HTTP 200 OK

- La nueva contraseña se encripta con bcrypt

- Se puede iniciar sesión con la nueva contraseña

## ❌ Caso 3: Intento de cambiar email

- **Precondición:** Usuario autenticado.

- **Acción:**  Enviar campo email en el body.

- **Resultado esperado:**

- Código HTTP 400 Bad Request

- error.code: "EMAIL_UPDATE_NOT_ALLOWED"

## ❌ Caso 4: Contraseña actual incorrecta

- **Precondición:** Usuario autenticado.

- **Acción:** Enviar contrasena_actual incorrecta.

- **Resultado esperado:**

- Código HTTP 400 Bad Request

- error.code: "INVALID_CURRENT_PASSWORD"

## ❌ Caso 5: Usuario no existe

- **Precondición:** ID de usuario no existe en la base de datos.

- **Acción:** Ejecutar PUT /api/v1/usuarios/999.

- **Resultado esperado:**

- Código HTTP 404 Not Found

- error.code: "USER_NOT_FOUND"

## ❌ Caso 6: Usuario intenta modificar otro usuario

- **Precondición:** Token JWT tiene id = 1, pero URL tiene id = 2.

- **Acción:** Ejecutar PUT /api/v1/usuarios/2.

- **Resultado esperado:**

- Código HTTP 403 Forbidden

- message: "No tiene permiso para modificar este usuario"

## ✅ Caso 7: Verificar registro en auditoría

- **Precondición:** Usuario realiza actualización exitosa.

- **Acción:** Consultar tabla auditoria_perfil.

- **Resultado esperado:**

- Existe registro con campo_modificado, valor_anterior, valor_nuevo y fecha_modificacion.

## ✅ Definición de Hecho

### Historia: [HU-003] Actualización de perfil

### 📦 Alcance Funcional

- [ ] El endpoint PUT /api/v1/usuarios/{id} está implementado.
- [ ] Se valida que el ID del token coincida con el ID de la URL.
- [ ] Se permite actualizar nombre y teléfono.
- [ ] No se permite actualizar email.
- [ ] El cambio de contraseña requiere verificación de la actual.
- [ ] Las nuevas contraseñas se encriptan con bcrypt.
- [ ] La auditoría registra todos los cambios.

### 🧪 Pruebas Completadas

- [ ] Pruebas unitarias para validaciones de formato.
- [ ] Pruebas de integración para actualización exitosa.
- [ ] Pruebas de integración para cambio de contraseña.
- [ ] Pruebas de integración para casos de error.
- [ ] Verificación de registro en auditoría.

### 📄 Documentación Técnica

- [ ] Endpoint documentado en Swagger / OpenAPI.
- [ ] Se describe propósito, campos de entrada y salida, ejemplos.

### 🔐 Manejo de Errores

- [ ] HTTP 400 para errores de validación.
- [ ] HTTP 403 para intento de modificar otro usuario.
- [ ] HTTP 404 para usuario no encontrado.
- [ ] Mensajes de error claros.