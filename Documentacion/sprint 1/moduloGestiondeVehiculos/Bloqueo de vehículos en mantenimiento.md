# [HU-008] Bloqueo de vehículos en mantenimiento

## 📖 Historia de Usuario

**Como** sistema de EcoMove,
**quiero** restringir automáticamente la disponibilidad de vehículos que se encuentran en estado de mantenimiento,
**para** evitar que sean reservados por los usuarios y garantizar que solo se ofrezcan vehículos operativos.

## 🔁 Flujo Esperado

- El usuario consulta vehículos disponibles mediante `GET /api/v1/vehiculos/disponibles`.
- El sistema excluye automáticamente los vehículos con estado "mantenimiento".
- Si un usuario intenta reservar un vehículo que cambió a mantenimiento entre la búsqueda y la confirmación, el sistema rechaza la reserva.
- Los administradores pueden visualizar los vehículos en mantenimiento en un panel separado mediante `GET /api/v1/vehiculos?estado=mantenimiento`.

## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [ ] El endpoint `GET /api/v1/vehiculos/disponibles` NO retorna vehículos con estado `mantenimiento`.
- [ ] El endpoint `GET /api/v1/vehiculos/disponibles` NO retorna vehículos con estado `en_uso`.
- [ ] Si un usuario intenta reservar un vehículo que está en `mantenimiento`, se rechaza la operación.
- [ ] Se expone un endpoint `GET /api/v1/vehiculos?estado=mantenimiento` para que los administradores consulten vehículos en mantenimiento.
- [ ] Se valida que el endpoint de administración solo sea accesible para usuarios con rol `administrador`.

### 2. 📆 Estructura de la información

- [ ] Se responde con la siguiente estructura en JSON para consulta de vehículos disponibles (excluyendo mantenimiento):

```json
{
  "success": true,
  "statusCode": 200,
  "message": "Vehículos disponibles encontrados",
  "data": {
    "total": 10,
    "vehiculos": [
      {
        "id": 1,
        "tipo": "moto",
        "modelo": "Scooter Eléctrica X1",
        "ubicacion": "Calle 123",
        "tarifaPorHora": 2500,
        "estado": "disponible"
      }
    ]
  }
}
```

- [ ] Si se intenta reservar un vehículo en mantenimiento, el sistema retorna:

```json
{
  "success": false,
  "statusCode": 409,
  "message": "No se puede reservar el vehículo",
  "error": {
    "code": "VEHICLE_IN_MAINTENANCE",
    "details": "El vehículo seleccionado se encuentra en mantenimiento y no está disponible para reserva"
  }
}
```
- [ ]   Para administradores, el endpoint GET /api/v1/vehiculos?estado=mantenimiento retorna:

```json
{
  "success": true,
  "statusCode": 200,
  "message": "Vehículos en mantenimiento encontrados",
  "data": {
    "total": 3,
    "vehiculos": [
      {
        "id": 5,
        "tipo": "carro",
        "modelo": "Auto Eléctrico Z3",
        "ubicacion": "Taller central",
        "tarifaPorHora": 5000,
        "estado": "mantenimiento",
        "fecha_ingreso_mantenimiento": "2025-01-10T08:00:00Z"
      }
    ]
  }
}
```

- [ ]   Si el usuario no es administrador e intenta acceder al panel de mantenimiento, el sistema retorna error FORBIDDEN.

- [ ]   Si el token no es válido o no se envía, el sistema retorna error UNAUTHORIZED.

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

### Índices para rendimiento
- Crear índice en la columna estado para acelerar consultas de vehículos disponibles.
- Índice compuesto en estado y tipo para filtros combinados.

### Seguridad
- El endpoint GET /api/v1/vehiculos/disponibles debe estar protegido con JWT (cualquier usuario autenticado).
- El endpoint GET /api/v1/vehiculos?estado=mantenimiento debe validar rol administrador.

### Validación en creación de reservas
- Al crear una reserva (HU-010), se debe verificar que el vehículo no esté en mantenimiento.
- Usar transacciones para evitar race conditions (el vehículo cambia estado mientras el usuario reserva).

### Manejo de errores
- Códigos de error sugeridos: VEHICLE_IN_MAINTENANCE, UNAUTHORIZED, FORBIDDEN, DATABASE_ERROR.

## 🚀 Endpoint 1 – Consulta de vehículos disponibles (excluye mantenimiento)

- **Método HTTP:** `GET`

- **Ruta:** `/api/v1/vehiculos/disponibles`

- **Headers:** Authorization: Bearer <token>

## 🚀 Endpoint 2 – Panel de administración (vehículos en mantenimiento)

- **Método HTTP:** `GET`

- **Ruta:** `/api/v1/vehiculos?estado=mantenimiento`

- **Headers:** Authorization: Bearer <token_administrador>

📤 Ejemplo de Request (Endpoint 1)

`GET /api/v1/vehiculos/disponibles`

📤 Ejemplo de Respuesta JSON Exitosa (Endpoint 1)

```json
{
  "success": true,
  "statusCode": 200,
  "message": "Vehículos disponibles encontrados",
  "data": {
    "total": 10,
    "vehiculos": [
      {
        "id": 1,
        "tipo": "moto",
        "modelo": "Scooter Eléctrica X1",
        "ubicacion": "Calle 123",
        "tarifaPorHora": 2500,
        "estado": "disponible"
      }
    ]
  }
}
```

📤 Ejemplo de Request (Endpoint 2)

`GET /api/v1/vehiculos?estado=mantenimiento`


📤 Ejemplo de Respuesta JSON Exitosa (Endpoint 2)

```json
{
  "success": true,
  "statusCode": 200,
  "message": "Vehículos en mantenimiento encontrados",
  "data": {
    "total": 3,
    "vehiculos": [
      {
        "id": 5,
        "tipo": "carro",
        "modelo": "Auto Eléctrico Z3",
        "ubicacion": "Taller central",
        "tarifaPorHora": 5000,
        "estado": "mantenimiento",
        "fecha_ingreso_mantenimiento": "2025-01-10T08:00:00Z"
      }
    ]
  }
}
```

📤 Ejemplo de Respuesta JSON Error (Reserva en mantenimiento)

```json
{
  "success": false,
  "statusCode": 409,
  "message": "No se puede reservar el vehículo",
  "error": {
    "code": "VEHICLE_IN_MAINTENANCE",
    "details": "El vehículo seleccionado se encuentra en mantenimiento y no está disponible para reserva"
  }
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

## ✅ Caso 1: Búsqueda de vehículos disponibles excluye mantenimiento

- **Precondición:**  Existen 5 vehículos disponibles, 3 en mantenimiento, 2 en uso.

- **Acción:** Ejecutar GET /api/v1/vehiculos/disponibles.

- **Resultado esperado:**

- Código HTTP 200 OK

- total: 5

- Ningún vehículo con estado mantenimiento o en_uso aparece en la lista

## ✅ Caso 2: Administrador consulta vehículos en mantenimiento

- **Precondición:** Existen 3 vehículos en mantenimiento.

- **Acción:** Ejecutar GET /api/v1/vehiculos?estado=mantenimiento con token de administrador.

- **Resultado esperado:**

- Código HTTP 200 OK

- total: 3

- Todos los vehículos tienen estado: "mantenimiento"

## ❌ Caso 3: Usuario no administrador intenta acceder al panel de mantenimiento

- **Precondición:** Usuario autenticado con rol usuario.

- **Acción:** Ejecutar GET /api/v1/vehiculos?estado=mantenimiento.

- **Resultado esperado:**

- Código HTTP 403 Forbidden

- error.code: "FORBIDDEN"

## ❌ Caso 4: Intentar reservar vehículo en mantenimiento

- **Precondición:** Vehículo con ID 5 está en mantenimiento.

- **Acción:** Intentar crear reserva para ese vehículo (POST /api/v1/reservas).

- **Resultado esperado:**

- Código HTTP 409 Conflict

- error.code: "VEHICLE_IN_MAINTENANCE"

## ✅ Caso 5: Race condition (vehículo cambia a mantenimiento durante reserva)

- **Precondición:** Usuario inicia reserva de vehículo disponible. Antes de confirmar, el vehículo cambia a mantenimiento.

- **Acción:** Usuario confirma la reserva.

- **Resultado esperado:**

- Código HTTP 409 Conflict

- error.code: "VEHICLE_IN_MAINTENANCE"

- La reserva no se crea

## ❌ Caso 6: Token no enviado

- **Precondición:** Ninguna.

- **Acción:** Ejecutar GET /api/v1/vehiculos/disponibles sin header Authorization.

- **Resultado esperado:**

- Código HTTP 401 Unauthorized

- error.code: "UNAUTHORIZED"

## ❌ Caso 7: Error de conexión a base de datos

- **Precondición:**  La base de datos no está disponible.

- **Acción:** Ejecutar GET /api/v1/vehiculos/disponibles bajo condiciones de fallo de BD.

- **Resultado esperado:**

- Código HTTP 503 Service Unavailable

- error.code: "DATABASE_ERROR"

## ✅ Definición de Hecho

### Historia: [HU-008] Bloqueo de vehículos en mantenimiento

### 📦 Alcance Funcional

- [ ] El endpoint GET /api/v1/vehiculos/disponibles excluye vehículos en mantenimiento y en_uso.
- [ ] El endpoint GET /api/v1/vehiculos?estado=mantenimiento está implementado para administradores.
- [ ] Solo administradores pueden acceder al panel de mantenimiento.
- [ ] Se valida que el vehículo no esté en mantenimiento al crear una reserva.
- [ ] Se manejan race conditions con transacciones.
- [ ] Las respuestas JSON cumplen con el contrato definido.

### 🧪 Pruebas Completadas

- [ ] Prueba de integración para exclusión de mantenimiento en búsqueda.
- [ ] Prueba de integración para panel de administración.
- [ ] Prueba de integración para usuario no administrador.
- [ ] Prueba de integración para reserva de vehículo en mantenimiento.
- [ ] Prueba de integración para race condition.
- [ ] Prueba de integración para token no enviado.
- [ ] Las pruebas funcionales están documentadas y pasadas.

### 📄 Documentación Técnica

- [ ] Endpoints documentados en Swagger / OpenAPI.
- [ ] Se describe propósito, parámetros de consulta, estructura de respuesta, ejemplos.

### 🔐 Manejo de Errores

- [ ] HTTP 409 para intento de reservar vehículo en mantenimiento (VEHICLE_IN_MAINTENANCE).
- [ ] HTTP 403 para permisos insuficientes (FORBIDDEN).
- [ ] HTTP 401 para token no válido (UNAUTHORIZED).
- [ ] HTTP 503 para error de conexión a base de datos (DATABASE_ERROR).
- [ ] Mensajes de error claros.