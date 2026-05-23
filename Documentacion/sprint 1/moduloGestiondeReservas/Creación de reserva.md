# [HU-010] Creación de reserva

## 📖 Historia de Usuario

**Como** usuario autenticado de EcoMove,  
**quiero** crear una reserva asociada a un vehículo específico en una fecha y horario determinados,  
**para** asegurar el uso del vehículo en el tiempo seleccionado y tener un registro formal de mi intención de uso.

---

## 🔁 Flujo Esperado

- El usuario envía una solicitud al endpoint `POST /api/v1/reservas` con los datos de la reserva.
- El sistema valida que el usuario esté autenticado y activo.
- El sistema verifica que el vehículo exista y esté disponible (no en mantenimiento).
- El sistema valida la disponibilidad del vehículo en la fecha y horario solicitados.
- El sistema calcula la duración y el costo estimado basado en la tarifa del vehículo.
- El sistema verifica que el usuario no haya alcanzado el límite de reservas activas.
- El sistema crea la reserva con estado `pendiente`.
- El sistema retorna los datos de la reserva creada.

---

## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [ ] Se expone un endpoint `POST /api/v1/reservas` para crear reservas.
- [ ] Se valida que los campos `vehiculo_id`, `fecha`, `hora_inicio`, `hora_fin` sean obligatorios.
- [ ] Se valida que el usuario esté autenticado y activo (`estado = true`).
- [ ] Se valida que el vehículo exista y no esté en `mantenimiento`.
- [ ] Se valida la disponibilidad del vehículo en el horario solicitado (sin superposición).
- [ ] Se valida que la fecha no sea anterior a la actual.
- [ ] Se valida que `hora_inicio` sea menor que `hora_fin`.
- [ ] Se valida que la duración mínima sea de 30 minutos.
- [ ] Se calcula la duración en horas: `(hora_fin - hora_inicio)`.
- [ ] Se calcula el costo estimado: `duracion * tarifaPorHora` del vehículo.
- [ ] Se verifica que el usuario no tenga más de 3 reservas activas (pendiente, confirmada, en_curso).
- [ ] La reserva se crea con estado `pendiente`.
- [ ] Se asocia automáticamente el `usuario_id` del token JWT.

---

### 2. 📆 Estructura de la información

- [ ] Se responde con la siguiente estructura en JSON para creación exitosa:

~~~json
{
  "success": true,
  "statusCode": 201,
  "message": "Reserva creada exitosamente",
  "data": {
    "id": 1001,
    "usuario_id": 1,
    "vehiculo_id": 1,
    "vehiculo": {
      "id": 1,
      "tipo": "moto",
      "modelo": "Scooter Eléctrica X1",
      "tarifaPorHora": 2500
    },
    "fecha": "2025-01-20",
    "hora_inicio": "10:00",
    "hora_fin": "12:00",
    "duracion_horas": 2,
    "costo_estimado": 5000,
    "estado": "pendiente",
    "fecha_creacion": "2025-01-15T10:30:00Z"
  }
}
~~~

- [ ] Si el vehículo no está disponible, el sistema retorna:

~~~json
{
  "success": false,
  "statusCode": 409,
  "message": "Vehículo no disponible en el horario solicitado",
  "error": {
    "code": "VEHICLE_UNAVAILABLE",
    "details": "El vehículo ya tiene una reserva en ese horario"
  }
}
~~~

- [ ] Si el vehículo está en mantenimiento, el sistema retorna:

~~~json
{
  "success": false,
  "statusCode": 409,
  "message": "Vehículo en mantenimiento",
  "error": {
    "code": "VEHICLE_IN_MAINTENANCE",
    "details": "El vehículo seleccionado se encuentra en mantenimiento"
  }
}
~~~

- [ ] Si el usuario ha alcanzado el límite de reservas activas, el sistema retorna:

~~~json
{
  "success": false,
  "statusCode": 400,
  "message": "Límite de reservas activas alcanzado",
  "error": {
    "code": "MAX_ACTIVE_RESERVATIONS",
    "details": "Has alcanzado el límite de 3 reservas activas. Cancela una reserva existente para continuar"
  }
}
~~~

- [ ] Si los datos son inválidos (fecha pasada, horario inválido, etc.), el sistema retorna error `INVALID_DATA`.

- [ ] Si el vehículo no existe, el sistema retorna error `VEHICLE_NOT_FOUND`.

- [ ] Si el usuario está desactivado, el sistema retorna error `USER_INACTIVE`.

- [ ] Si el token no es válido o no se envía, el sistema retorna error `UNAUTHORIZED`.

- [ ] Si hay error de conexión a la base de datos, el sistema retorna error `DATABASE_ERROR`.

---

## 🔧 Notas Técnicas

### Reglas de negocio

- El tiempo máximo de reserva antes de iniciar el viaje es de 15 minutos; pasado este tiempo, la reserva se cancela automáticamente.
- Un usuario que acumule tres reservas canceladas por no pago o no presentación dentro de un período de 30 días será temporalmente inhabilitado.
- Un usuario con una reserva en curso o con un viaje activo no puede ser dado de baja del sistema.

---

### Base de datos (tabla `reservas`)

- id: SERIAL / AUTO_INCREMENT (PK)
- usuario_id: INT, FK a usuarios(id)
- vehiculo_id: INT, FK a vehiculos(id)
- fecha: DATE, NOT NULL
- hora_inicio: TIME, NOT NULL
- hora_fin: TIME, NOT NULL
- duracion_horas: DECIMAL(5,2), NOT NULL
- costo_estimado: DECIMAL(10,2), NOT NULL
- estado: ENUM('pendiente', 'confirmada', 'en_curso', 'finalizada', 'cancelada'), DEFAULT 'pendiente'
- fecha_creacion: TIMESTAMP, DEFAULT CURRENT_TIMESTAMP
- fecha_cancelacion: TIMESTAMP, NULLABLE

---

### Lógica de transacciones

- Usar transacción para validar disponibilidad y crear la reserva.
- Usar `SELECT FOR UPDATE` para bloquear la fila del vehículo y evitar race conditions.

---

### Límite de reservas activas

~~~sql
SELECT COUNT(*) FROM reservas 
WHERE usuario_id = ? 
AND estado IN ('pendiente', 'confirmada', 'en_curso')
~~~

- Límite por defecto: 3 (configurable por variable de entorno).

---

### Manejo de errores

- Códigos de error sugeridos: VEHICLE_UNAVAILABLE, VEHICLE_IN_MAINTENANCE, MAX_ACTIVE_RESERVATIONS, INVALID_DATA, VEHICLE_NOT_FOUND, USER_INACTIVE, UNAUTHORIZED, DATABASE_ERROR.

---

## 🚀 Endpoint – Creación de reserva

- **Método HTTP:** `POST`
- **Ruta:** `/api/v1/reservas`
- **Headers:** `Authorization: Bearer <token>`

---

### 📤 Ejemplo de Request JSON

~~~json
{
  "vehiculo_id": 1,
  "fecha": "2025-01-20",
  "hora_inicio": "10:00",
  "hora_fin": "12:00"
}
~~~

---

### 📤 Ejemplo de Respuesta JSON Exitosa

~~~json
{
  "success": true,
  "statusCode": 201,
  "message": "Reserva creada exitosamente",
  "data": {
    "id": 1001,
    "usuario_id": 1,
    "vehiculo_id": 1,
    "vehiculo": {
      "id": 1,
      "tipo": "moto",
      "modelo": "Scooter Eléctrica X1",
      "tarifaPorHora": 2500
    },
    "fecha": "2025-01-20",
    "hora_inicio": "10:00",
    "hora_fin": "12:00",
    "duracion_horas": 2,
    "costo_estimado": 5000,
    "estado": "pendiente",
    "fecha_creacion": "2025-01-15T10:30:00Z"
  }
}
~~~

---

### 📤 Ejemplo de Respuesta JSON Error (Vehículo no disponible)

~~~json
{
  "success": false,
  "statusCode": 409,
  "message": "Vehículo no disponible en el horario solicitado",
  "error": {
    "code": "VEHICLE_UNAVAILABLE",
    "details": "El vehículo ya tiene una reserva en ese horario"
  }
}
~~~

---

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

## ✅ Caso 1: Creación exitosa de reserva

- **Precondición:** Usuario autenticado y activo. Vehículo disponible, sin reservas en el horario. Usuario tiene menos de 3 reservas activas.
- **Acción:** Ejecutar POST /api/v1/reservas con JSON válido.
- **Resultado esperado:**
  - Código HTTP 201 Created
  - success: true
  - estado: "pendiente"
  - duracion_horas y costo_estimado calculados correctamente
  - Se inserta registro en reservas

---

## ❌ Caso 2: Vehículo no disponible

- **Precondición:** Existe una reserva activa en el mismo horario.
- **Acción:** Ejecutar POST /api/v1/reservas con el mismo horario.
- **Resultado esperado:**
  - Código HTTP 409 Conflict
  - error.code: "VEHICLE_UNAVAILABLE"

---

## ❌ Caso 3: Vehículo en mantenimiento

- **Precondición:** Vehículo tiene estado = "mantenimiento".
- **Acción:** Ejecutar POST /api/v1/reservas para ese vehículo.
- **Resultado esperado:**
  - Código HTTP 409 Conflict
  - error.code: "VEHICLE_IN_MAINTENANCE"

---

## ❌ Caso 4: Usuario alcanzó límite de reservas activas

- **Precondición:** Usuario tiene 3 reservas activas (pendiente, confirmada o en_curso).
- **Acción:** Ejecutar POST /api/v1/reservas.
- **Resultado esperado:**
  - Código HTTP 400 Bad Request
  - error.code: "MAX_ACTIVE_RESERVATIONS"

---

## ❌ Caso 5: Fecha anterior a la actual

- **Precondición:** Ninguna.
- **Acción:** Ejecutar POST /api/v1/reservas con fecha "2020-01-01".
- **Resultado esperado:**
  - Código HTTP 400 Bad Request
  - error.code: "INVALID_DATA"

---

## ❌ Caso 6: Hora inicio mayor o igual a hora fin

- **Precondición:** Ninguna.
- **Acción:** Ejecutar POST /api/v1/reservas con hora_inicio=12:00 y hora_fin=10:00.
- **Resultado esperado:**
  - Código HTTP 400 Bad Request
  - error.code: "INVALID_DATA"

---

## ❌ Caso 7: Duración menor a 30 minutos

- **Precondición:** Ninguna.
- **Acción:** Ejecutar POST /api/v1/reservas con hora_inicio=10:00 y hora_fin=10:15.
- **Resultado esperado:**
  - Código HTTP 400 Bad Request
  - error.code: "INVALID_DATA"

---

## ❌ Caso 8: Vehículo no existe

- **Precondición:** El vehículo con ID 999 no existe.
- **Acción:** Ejecutar POST /api/v1/reservas con vehiculo_id=999.
- **Resultado esperado:**
  - Código HTTP 404 Not Found
  - error.code: "VEHICLE_NOT_FOUND"

---

## ❌ Caso 9: Usuario desactivado

- **Precondición:** Usuario autenticado pero estado = false.
- **Acción:** Ejecutar POST /api/v1/reservas.
- **Resultado esperado:**
  - Código HTTP 401 Unauthorized
  - error.code: "USER_INACTIVE"

---

## ❌ Caso 10: Race condition (doble reserva simultánea)

- **Precondición:** Dos usuarios intentan reservar el mismo vehículo en el mismo horario.
- **Acción:** Ejecutar dos requests simultáneos.
- **Resultado esperado:**
  - Solo una reserva se crea exitosamente (HTTP 201)
  - La otra recibe error VEHICLE_UNAVAILABLE (HTTP 409)

---

## ❌ Caso 11: Token no enviado

- **Precondición:** Ninguna.
- **Acción:** Ejecutar POST /api/v1/reservas sin header Authorization.
- **Resultado esperado:**
  - Código HTTP 401 Unauthorized
  - error.code: "UNAUTHORIZED"

---

## ✅ Caso 12: Verificar cálculo de costo estimado

- **Precondición:** Vehículo tiene tarifaPorHora = 2500. Reserva de 2 horas.
- **Acción:** Crear reserva.
- **Resultado esperado:** costo_estimado = 5000

---

## ❌ Caso 13: Error de conexión a base de datos

- **Precondición:** La base de datos no está disponible.
- **Acción:** Ejecutar POST /api/v1/reservas bajo condiciones de fallo de BD.
- **Resultado esperado:**
  - Código HTTP 503 Service Unavailable
  - error.code: "DATABASE_ERROR"

---

## ✅ Definición de Hecho

### Historia: [HU-010] Creación de reserva

### 📦 Alcance Funcional

- [ ] El endpoint POST /api/v1/reservas está implementado.
- [ ] Se validan los parámetros obligatorios.
- [ ] Se valida que el usuario esté activo.
- [ ] Se valida que el vehículo exista y no esté en mantenimiento.
- [ ] Se valida la disponibilidad del vehículo en el horario.
- [ ] Se valida que la fecha no sea pasada.
- [ ] Se valida que hora_inicio < hora_fin.
- [ ] Se valida duración mínima de 30 minutos.
- [ ] Se calcula duración y costo estimado correctamente.
- [ ] Se verifica el límite de reservas activas del usuario.
- [ ] La reserva se crea con estado pendiente.
- [ ] Se manejan race conditions con transacciones.
- [ ] La respuesta JSON cumple con el contrato definido.

---

### 🧪 Pruebas Completadas

- [ ] Pruebas unitarias para cálculo de duración y costo.
- [ ] Prueba de integración para creación exitosa.
- [ ] Prueba de integración para vehículo no disponible.
- [ ] Prueba de integración para vehículo en mantenimiento.
- [ ] Prueba de integración para límite de reservas activas.
- [ ] Prueba de integración para fecha/horario inválido.
- [ ] Prueba de integración para vehículo no encontrado.
- [ ] Prueba de integración para usuario desactivado.
- [ ] Prueba de integración para race condition.
- [ ] Prueba de integración para token no enviado.
- [ ] Las pruebas funcionales están documentadas y pasadas.

---

### 📄 Documentación Técnica

- [ ] Endpoint documentado en Swagger / OpenAPI.
- [ ] Se describe propósito, campos de entrada y salida, ejemplos.

---

### 🔐 Manejo de Errores

- [ ] HTTP 400 para datos inválidos (INVALID_DATA, MAX_ACTIVE_RESERVATIONS).
- [ ] HTTP 404 para vehículo no encontrado (VEHICLE_NOT_FOUND).
- [ ] HTTP 409 para conflicto de disponibilidad (VEHICLE_UNAVAILABLE, VEHICLE_IN_MAINTENANCE).
- [ ] HTTP 401 para usuario inactivo o no autenticado (USER_INACTIVE, UNAUTHORIZED).
- [ ] HTTP 503 para error de conexión a base de datos (DATABASE_ERROR).
- [ ] Mensajes de error claros.