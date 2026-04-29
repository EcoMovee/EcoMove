# [HU-007] Actualización del estado del vehículo

## 📖 Historia de Usuario

**Como** administrador de EcoMove,
**quiero** actualizar el estado de un vehículo (disponible, en_uso, mantenimiento) validando las transiciones permitidas,
**para** reflejar correctamente su disponibilidad en el sistema y mantener un historial confiable de los cambios.

## 🔁 Flujo Esperado

- El administrador envía una solicitud al endpoint `PATCH /api/v1/vehiculos/estado/{id}` con el nuevo estado.

- El sistema valida que el usuario autenticado tenga rol `administrador`.

- El sistema verifica que el vehículo exista en la tabla `vehiculos`.

- El sistema valida que la transición de estado sea permitida según las reglas.

- Si el nuevo estado es "mantenimiento" y el vehículo tiene reservas futuras, el sistema muestra una advertencia.

- El sistema actualiza el estado del vehículo.

- El sistema registra el cambio en la tabla `historial_estado_vehiculo`.

- El sistema retorna los datos actualizados del vehículo.

## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [ ] Se expone un endpoint `PATCH /api/v1/vehiculos/estado/{id}` para actualizar el estado del vehículo.

- [ ] Se valida que el usuario autenticado tenga rol `administrador`.

- [ ] Se valida que el vehículo exista en la tabla `vehiculos`.

- [ ] Se validan las transiciones de estado permitidas:
  - `disponible` → `en_uso` (permitido)
  - `disponible` → `mantenimiento` (permitido)
  - `en_uso` → `disponible` (permitido)
  - `en_uso` → `mantenimiento` (NO permitido)
  - `mantenimiento` → `disponible` (permitido)
  - `mantenimiento` → `en_uso` (NO permitido)

- [ ] Si el nuevo estado es `mantenimiento`, se verifica si el vehículo tiene reservas futuras.

- [ ] Si tiene reservas futuras, se muestra advertencia (pero se permite continuar con confirmación).

- [ ] Se registra cada cambio de estado en la tabla `historial_estado_vehiculo`.

### 2. 📆 Estructura de la información

- [ ] Se responde con la siguiente estructura en JSON para actualización exitosa:

```json
{
  "success": true,
  "statusCode": 200,
  "message": "Estado del vehículo actualizado correctamente",
  "data": {
    "id": 1,
    "tipo": "moto",
    "modelo": "Scooter Eléctrica X1",
    "estado_anterior": "disponible",
    "estado_nuevo": "mantenimiento",
    "fecha_cambio": "2025-01-15T10:30:00Z",
    "reservas_afectadas": 2
  }
}
```

- [ ] Si la transición no está permitida, el sistema retorna:

```json
{
  "success": false,
  "statusCode": 400,
  "message": "Transición de estado no permitida",
  "error": {
    "code": "INVALID_STATE_TRANSITION",
    "details": "No se puede cambiar de 'en_uso' a 'mantenimiento'. Debe pasar primero a 'disponible'"
  }
}
```
- [ ]   Si el vehículo no existe, el sistema retorna:

```json
{
  "success": false,
  "statusCode": 404,
  "message": "Vehículo no encontrado",
  "error": {
    "code": "VEHICLE_NOT_FOUND",
    "details": "No existe un vehículo con el ID proporcionado"
  }
}
```

- [ ]   Si el vehículo tiene reservas futuras y se confirma el cambio a mantenimiento, el sistema retorna advertencia:

```json
{
  "success": true,
  "statusCode": 200,
  "message": "Estado actualizado con advertencia: El vehículo tiene reservas futuras que serán afectadas",
  "data": {
    "id": 1,
    "estado_anterior": "disponible",
    "estado_nuevo": "mantenimiento",
    "reservas_afectadas": 2
  }
}
```

- [ ]   Si el token no es válido o no se envía, el sistema retorna error UNAUTHORIZED.

- [ ]   Si el usuario no es administrador, el sistema retorna error FORBIDDEN.

- [ ]   Si hay error de conexión a la base de datos, el sistema retorna error DATABASE_ERROR.

## 🔧 Notas Técnicas

### Reglas de negocio
- Un vehículo que presenta reportes de daño o mantenimiento recurrente por parte de los usuarios debe ser retirado temporalmente de la flota hasta su revisión técnica, priorizando la seguridad y experiencia del cliente.
- Los vehículos eléctricos solo pueden ser ofrecidos en alquiler si cuentan con un nivel de batería suficiente.

### Base de datos (tabla `vehiculos`)
- La tabla debe incluir las siguientes columnas:
  - id: SERIAL / AUTO_INCREMENT (PK)
  - tipo: ENUM('carro', 'moto', 'bicicleta'), NOT NULL
  - modelo: VARCHAR(100), NOT NULL
  - ubicacion: VARCHAR(255), NOT NULL
  - tarifaPorHora: DECIMAL(10,2), NOT NULL
  - estado: ENUM('disponible', 'en_uso', 'mantenimiento'), DEFAULT 'disponible'
  - nivel_bateria: INT, DEFAULT 100
  - fecha_registro: TIMESTAMP, DEFAULT CURRENT_TIMESTAMP

### Base de datos (tabla historial_estado_vehiculo)
- La tabla debe incluir las siguientes columnas:
  - id: SERIAL / AUTO_INCREMENT (PK)
  - vehiculo_id: INT, FK a vehiculos(id)
  - estado_anterior: ENUM('disponible', 'en_uso', 'mantenimiento')
  - estado_nuevo: ENUM('disponible', 'en_uso', 'mantenimiento')
  - administrador_id: INT, FK a usuarios(id)
  - fecha_cambio: TIMESTAMP, DEFAULT CURRENT_TIMESTAMP
  - reservas_afectadas: INT, DEFAULT 0

### Seguridad
- El endpoint debe estar protegido con JWT.
- Se debe validar el rol administrador desde el middleware.
- Solo administradores pueden actualizar el estado de los vehículos.

### Validación de reservas futuras
- Consultar la tabla reservas para verificar si existen reservas con fecha_inicio > NOW() y vehiculo_id = id.
- Si existen, mostrar advertencia con el número de reservas afectadas.

### Manejo de errores
- Códigos de error sugeridos: INVALID_STATE_TRANSITION, VEHICLE_NOT_FOUND, UNAUTHORIZED, FORBIDDEN, DATABASE_ERROR.

## 🚀 Endpoint – Registro de usuario

- **Método HTTP:** `PATCH`

- **Ruta:** `/api/v1/vehiculos/estado/{id}`

- **Headers:** Authorization: Bearer <token_administrador>

📤 Ejemplo de Request JSON

```json
{
  "nuevo_estado": "mantenimiento",
  "confirmar_reservas_futuras": true
}
```

📤 Ejemplo de Respuesta JSON Exitosa

```json
{
  "success": true,
  "statusCode": 200,
  "message": "Estado del vehículo actualizado correctamente",
  "data": {
    "id": 1,
    "tipo": "moto",
    "modelo": "Scooter Eléctrica X1",
    "estado_anterior": "disponible",
    "estado_nuevo": "mantenimiento",
    "fecha_cambio": "2025-01-15T10:30:00Z",
    "reservas_afectadas": 2
  }
}
```

📤 Ejemplo de Respuesta JSON Error (Transición no permitida)

```json
{
  "success": false,
  "statusCode": 400,
  "message": "Transición de estado no permitida",
  "error": {
    "code": "INVALID_STATE_TRANSITION",
    "details": "No se puede cambiar de 'en_uso' a 'mantenimiento'. Debe pasar primero a 'disponible'"
  }
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

## ✅ Caso 1: Transición válida disponible → mantenimiento

- **Precondición:**  Vehículo existe, estado actual = "disponible", no tiene reservas futuras.

- **Acción:** Ejecutar PATCH /api/v1/vehiculos/estado/1 con nuevo_estado: "mantenimiento".

- **Resultado esperado:**

- Código HTTP 200 OK

- success: true

- estado_nuevo: "mantenimiento"

- Se registra en historial_estado_vehiculo

## ✅ Caso 2: Transición válida en_uso → disponible

- **Precondición:** Vehículo existe, estado actual = "en_uso".

- **Acción:** Ejecutar PATCH /api/v1/vehiculos/estado/1 con nuevo_estado: "disponible"..

- **Resultado esperado:**

- Código HTTP 200 OK

- success: true

- estado_nuevo: "disponible"

- Se registra en historial_estado_vehiculo

## ❌ Caso 3: Transición inválida en_uso → mantenimiento

- **Precondición:** Vehículo existe, estado actual = "en_uso".

- **Acción:** : Ejecutar PATCH /api/v1/vehiculos/estado/1 con nuevo_estado: "mantenimiento".

- **Resultado esperado:**

- Código HTTP 400 Bad Request

- error.code: "INVALID_STATE_TRANSITION"

## ⚠️ Caso 4: Mantenimiento con reservas futuras (con confirmación)

- **Precondición:** Vehículo tiene 2 reservas futuras, estado actual = "disponible".

- **Acción:** Ejecutar PATCH /api/v1/vehiculos/estado/1 con nuevo_estado: "mantenimiento" y confirmar_reservas_futuras: true.

- **Resultado esperado:**

- Código HTTP 200 OK

- reservas_afectadas: 2

- message incluye advertencia

## ❌ Caso 5: Mantenimiento con reservas futuras (sin confirmación)

- **Precondición:** Vehículo tiene reservas futuras..

- **Acción:** Ejecutar PATCH /api/v1/vehiculos/estado/1 solo con nuevo_estado: "mantenimiento".

- **Resultado esperado:**

- Código HTTP 400 Bad Request

- message pidiendo confirmación

## ❌ Caso 6: Vehículo no existe

- **Precondición:** ID de vehículo no existe en la base de datos.

- **Acción:** Ejecutar PATCH /api/v1/vehiculos/estado/999.

- **Resultado esperado:**

- Código HTTP 404 Not Found

- error.code: "VEHICLE_NOT_FOUND"

## ❌ Caso 7: Usuario no administrador intenta actualizar

- **Precondición:** Usuario autenticado con rol usuario.

- **Acción:** Ejecutar PATCH /api/v1/vehiculos/estado/1.

- **Resultado esperado:**

- Código HTTP 403 Forbidden

- error.code: "FORBIDDEN"

## ❌ Caso 8: Token no enviado

- **Precondición:** Ninguna.

- **Acción:** Ejecutar PATCH /api/v1/vehiculos/estado/1 sin header Authorization.

- **Resultado esperado:**

- Código HTTP 401 Unauthorized

- error.code: "UNAUTHORIZED"

## ✅ Caso 9: Verificar historial de cambios

- **Precondición:** Se realizó una actualización de estado exitosa.

- **Acción:** Consultar tabla historial_estado_vehiculo.

- **Resultado esperado:**

-  Existe registro con vehiculo_id, estado_anterior, estado_nuevo, administrador_id, fecha_cambio.

## ❌ Caso 10: Error de conexión a base de datos

- **Precondición:**La base de datos no está disponible.

- **Acción:** Ejecutar PATCH /api/v1/vehiculos/estado/1 bajo condiciones de fallo de BD.

- **Resultado esperado:**

-  Código HTTP 503 Service Unavailable

- error.code: "DATABASE_ERROR"

## ✅ Definición de Hecho

### Historia: [HU-007] Actualización del estado del vehículo

### 📦 Alcance Funcional

- [ ] El endpoint PATCH /api/v1/vehiculos/estado/{id} está implementado.
- [ ] Solo administradores pueden actualizar el estado.
- [ ] Se validan las transiciones de estado permitidas.
- [ ] Se verifica si el vehículo tiene reservas futuras antes de pasar a mantenimiento.
- [ ] Se requiere confirmación explícita si hay reservas futuras.
- [ ] Se registra cada cambio en historial_estado_vehiculo.
- [ ] La respuesta JSON cumple con el contrato definido.

### 🧪 Pruebas Completadas

- [ ] Pruebas unitarias para las transiciones de estado.
- [ ] Prueba de integración para transición válida.
- [ ] Prueba de integración para transición inválida.
- [ ] Prueba de integración para mantenimiento con reservas futuras.
- [ ] Prueba de integración para vehículo no encontrado.
- [ ] Prueba de integración para usuario no administrador.
- [ ] Prueba de integración para token no enviado.
- [ ] Verificación de registro en historial.
- [ ] Las pruebas funcionales están documentadas y pasadas.

### 📄 Documentación Técnica

- [ ] EEndpoint documentado en Swagger / OpenAPI.
- [ ] Se describe propósito, campos de entrada y salida, ejemplos.

### 🔐 Manejo de Errores

- [ ] HTTP 400 para transición no permitida (INVALID_STATE_TRANSITION).
- [ ] HTTP 404 para vehículo no encontrado (VEHICLE_NOT_FOUND).
- [ ] HTTP 403 para permisos insuficientes (FORBIDDEN).
- [ ] HTTP 401 para token no válido (UNAUTHORIZED).
- [ ] HTTP 503 para error de conexión a base de datos (DATABASE_ERROR).
- [ ] Mensajes de error claros.