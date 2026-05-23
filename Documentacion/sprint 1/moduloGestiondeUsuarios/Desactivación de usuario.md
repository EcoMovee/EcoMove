# [HU-004] Desactivación de usuario

## 📖 Historia de Usuario

**Como** administrador de EcoMove,

**quiero** desactivar usuarios que hayan violado las políticas del sistema o que ya no utilicen la plataforma,

**para** restringir accesos no autorizados, mantener la seguridad del sistema y conservar un historial de acciones administrativas.

## 🔁 Flujo Esperado

- El administrador envía una solicitud al endpoint `PATCH /api/v1/usuarios/estado/{id}` para desactivar un usuario.

- El sistema valida que el usuario autenticado tenga rol `administrador`.

- El sistema verifica que el usuario a desactivar exista y esté activo (`estado = true`).

- El sistema verifica que el usuario a desactivar no sea el único administrador activo del sistema.

- Si las validaciones son exitosas, el sistema cambia `estado = false` en la tabla `usuarios`.

- El sistema registra la acción en la tabla `log_administrativo`.

- El usuario desactivado no puede iniciar sesión ni crear nuevas reservas.

- Las reservas pasadas del usuario se conservan en el historial.

## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [ ] Se expone un endpoint `PATCH /api/v1/usuarios/estado/{id}` para desactivar usuarios.

- [ ] Se valida que el usuario autenticado tenga rol `administrador`.

- [ ] Se valida que el usuario a desactivar exista en la tabla `usuarios`.

- [ ] Se valida que el usuario a desactivar tenga `estado = true`.

- [ ] Si el usuario ya está inactivo, retorna mensaje de error.

- [ ] Se valida que el usuario a desactivar no sea el único administrador activo del sistema.

- [ ] Si es el único administrador activo, se rechaza la operación.

- [ ] Se cambia el estado del usuario a `estado = false`.

- [ ] Se registra la acción en la tabla `log_administrativo`.

### 2. 📆 Estructura de la información

- [ ] Se responde con la siguiente estructura en JSON para desactivación exitosa:

```json
{
  "success": true,
  "statusCode": 200,
  "message": "Usuario desactivado exitosamente",
  "data": {
    "usuario_id": 2,
    "nombre": "Maria Lopez",
    "email": "maria@example.com",
    "estado_anterior": true,
    "estado_nuevo": false,
    "fecha_desactivacion": "2025-01-15T10:30:00Z"
  }
}
```

- [ ]  Si el usuario ya está inactivo, el sistema retorna:

```json
{
  "success": false,
  "statusCode": 400,
  "message": "El usuario ya está inactivo",
  "error": {
    "code": "USER_ALREADY_INACTIVE",
    "details": "El usuario con ID 2 ya se encuentra desactivado"
  }
}
```

- [ ]   Si se intenta desactivar al último administrador, el sistema retorna:

```json
{
  "success": false,
  "statusCode": 403,
  "message": "No se puede desactivar al único administrador activo",
  "error": {
    "code": "LAST_ADMIN_CANNOT_BE_DEACTIVATED",
    "details": "El sistema debe tener al menos un administrador activo"
  }
}
```
- [ ]   Si el usuario no existe, el sistema retorna:

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

## 3. 📝 Auditoría de cambios

- Se registra en una tabla log_administrativo:
  - administrador_id: ID del administrador que realiza la acción
  - usuario_afectado_id: ID del usuario desactivado
  - accion: "DESACTIVAR_USUARIO"
  - motivo: texto opcional (si se envía en el body)
  - fecha: TIMESTAMP
  - ip_origen: VARCHAR(45) (opcional)

## 4. 🚫 Restricciones posteriores a la desactivación

- El usuario desactivado (estado = false) no puede iniciar sesión.
- El usuario desactivado no puede crear nuevas reservas.
- Las reservas pasadas del usuario siguen siendo visibles en consultas de historial.

## 🔧 Notas Técnicas

### Reglas de negocio
- Un usuario con una reserva en curso o con un viaje activo no puede ser dado de baja del sistema.
- Ninguna empresa puede ser eliminada del sistema si mantiene vehículos activos.

### Base de datos (tabla `usuarios`)
- Tabla usuarios (misma que HU-001, HU-002, HU-003)
- Tabla log_administrativo:
  - id: SERIAL (PK)
  - administrador_id: INT, FK a usuarios(id)
  - usuario_afectado_id: INT, FK a usuarios(id)
  - accion: VARCHAR(100)
  - motivo: TEXT, NULLABLE
  - fecha: TIMESTAMP, DEFAULT CURRENT_TIMESTAMP
  - ip_origen: VARCHAR(45), NULLABLE

### Seguridad
- El endpoint debe estar protegido con JWT.
- Se debe validar el rol administrador desde el middleware.
- No se permite que un administrador se desactive a sí mismo.

### Validaciones adicionales
- Antes de desactivar, verificar que el usuario no tenga reservas activas (estado "pendiente" o "confirmada" o "en_curso").
- Antes de desactivar, verificar que no sea el único administrador activo.

### Manejo de errores
- Códigos de error sugeridos: USER_NOT_FOUND, USER_ALREADY_INACTIVE, LAST_ADMIN_CANNOT_BE_DEACTIVATED, USER_HAS_ACTIVE_RESERVATIONS.Códigos de error sugeridos: USER_NOT_FOUND, EMAIL_UPDATE_NOT_ALLOWED, INVALID_CURRENT_PASSWORD, INVALID_DATA.

## 🚀 Endpoint – Desactivación de usuario

- **Método HTTP:** `PATCH`

- **Ruta:** `/api/v1/usuarios/estado/{id}`

- **Headers:** AAuthorization: Bearer <token_administrador>

📤 Ejemplo de Request JSON

```json
{
  "motivo": "Usuario reportado por comportamiento inapropiado"
}
```
📤 Ejemplo de Respuesta JSON Exitosa

```json
{
  "success": true,
  "statusCode": 200,
  "message": "Usuario desactivado exitosamente",
  "data": {
    "usuario_id": 2,
    "nombre": "Maria Lopez",
    "email": "maria@example.com",
    "estado_anterior": true,
    "estado_nuevo": false,
    "fecha_desactivacion": "2025-01-15T10:30:00Z"
  }
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

## ✅ Caso 1: Desactivación exitosa de usuario normal

- **Precondición:**  Usuario autenticado con rol administrador. Usuario a desactivar existe, estado = true, no es administrador, no tiene reservas activas.

- **Acción:** Ejecutar PATCH /api/v1/usuarios/estado/2.

- **Resultado esperado:**

- Código HTTP 200 OK

- success: true

- stado cambia a false

- Se registra en log_administrativo

## ❌ Caso 2: Usuario ya inactivo

- **Precondición:** Usuario a desactivar tiene estado = false.

- **Acción:** Ejecutar PATCH /api/v1/usuarios/estado/2.

- **Resultado esperado:**

- Código HTTP 400 Bad Request

- error.code: "USER_ALREADY_INACTIVE"

## ❌ Caso 3: Intentar desactivar al último administrador

- **Precondición:** Solo existe un administrador activo en el sistema (el que hace la solicitud).

- **Acción:**  Intentar desactivarse a sí mismo o al último administrador.

- **Resultado esperado:**

- Código HTTP 403 Forbidden

- error.code: "LAST_ADMIN_CANNOT_BE_DEACTIVATED"

## ❌ Caso 4: Usuario no existe

- **Precondición:** ID de usuario no existe en la base de datos.

- **Acción:** Ejecutar PATCH /api/v1/usuarios/estado/999.

- **Resultado esperado:**

- Código HTTP 404 Not Found

- error.code: "USER_NOT_FOUND"

## ⚠️ Caso 5: Usuario con reservas activas

- **Precondición:** Usuario tiene una reserva en curso o confirmada.

- **Acción:**  Intentar desactivar al usuario.

- **Resultado esperado:**

- Código HTTP 400 Bad Request

- error.code: "USER_HAS_ACTIVE_RESERVATIONS"

- message: "No se puede desactivar un usuario con reservas activas"

## ❌ Caso 6: Usuario no administrador intenta desactivar

- **Precondición:** Usuario autenticado tiene rol usuario.

- **Acción:** Ejecutar PATCH /api/v1/usuarios/estado/2.

- **Resultado esperado:**

- Código HTTP 403 Forbidden

- message: "Acceso denegado. Se requieren privilegios de administrador"

## ✅ Caso 7: Usuario desactivado no puede iniciar sesión

- **Precondición:** Usuario con estado = false.

- **Acción:** Intentar POST /api/v1/usuarios/login con sus credenciales.

- **Resultado esperado:**

- Código HTTP 401 Unauthorized

- message: "Usuario desactivado. Contacte al administrador"

## ✅ Definición de Hecho

### Historia: [HU-004] Desactivación de usuario

### 📦 Alcance Funcional

- [ ] El endpoint PATCH /api/v1/usuarios/estado/{id} está implementado.
- [ ] Solo administradores pueden ejecutar esta acción.
- [ ] Se valida que el usuario a desactivar exista y esté activo.
- [ ] Se valida que no sea el último administrador activo.
- [ ] Se valida que no tenga reservas activas.
- [ ] Se cambia el estado del usuario a false.
- [ ] Se registra la acción en log_administrativo.
- [ ] El usuario desactivado no puede iniciar sesión.

### 🧪 Pruebas Completadas

- [ ] Prueba de integración para desactivación exitosa.
- [ ] Prueba de integración para usuario ya inactivo.
- [ ] Prueba de integración para último administrador.
- [ ] Prueba de integración para usuario con reservas activas.
- [ ] Prueba de integración para usuario no administrador.
- [ ] Verificación de que el usuario desactivado no puede iniciar sesión.

### 📄 Documentación Técnica

- [ ] Endpoint documentado en Swagger / OpenAPI.
- [ ] Se describe propósito, campos de entrada y salida, ejemplos.

### 🔐 Manejo de Errores

- [ ] HTTP 400 para errores de validación.
- [ ] HTTP 403 para permisos insuficientes.
- [ ] HTTP 404 para usuario no encontrado.
- [ ] Mensajes de error claros.