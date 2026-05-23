# [HU-009] Validación de disponibilidad

## 📖 Historia de Usuario

**Como** usuario autenticado de EcoMove,  

**quiero** validar si un vehículo está disponible en una fecha y hora específica antes de hacer la reserva,  

**para** evitar conflictos con otras reservas activas y asegurar que el vehículo estará libre cuando yo lo necesite.

## 🔁 Flujo Esperado

- El usuario envía una solicitud al endpoint `GET /api/v1/reservas/disponibilidad` con el vehículo, fecha, hora de inicio y hora de fin.
- El sistema verifica si existe alguna reserva activa que se superponga con el intervalo solicitado.
- El sistema considera reservas con estado `pendiente`, `confirmada` o `en_curso`.
- Si el vehículo está disponible, el sistema retorna éxito.
- Si no está disponible, el sistema retorna los horarios alternativos sugeridos.

## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [ ] Se expone un endpoint `GET /api/v1/reservas/disponibilidad` para validar disponibilidad.

- [ ] Se validan los parámetros obligatorios: `vehiculo_id`, `fecha`, `hora_inicio`, `hora_fin`.

- [ ] Se valida que la fecha no sea anterior a la fecha actual.

- [ ] Se valida que `hora_inicio` sea menor que `hora_fin`.

- [ ] Se valida que la duración mínima sea de 30 minutos.

- [ ] Se consulta la tabla `reservas` para verificar superposición con reservas activas.

- [ ] Se consideran reservas con estado: `pendiente`, `confirmada`, `en_curso`.

- [ ] NO se consideran reservas con estado: `cancelada`, `finalizada`.

- [ ] Si no está disponible, se calculan los próximos 3 horarios disponibles.

### 2. 📆 Estructura de la información

- [ ] Se responde con la siguiente estructura en JSON cuando el vehículo está disponible:

~~~json
{
  "success": true,
  "statusCode": 200,
  "message": "Vehículo disponible",
  "data": {
    "vehiculo_id": 1,
    "fecha": "2025-01-20",
    "hora_inicio": "10:00",
    "hora_fin": "12:00",
    "disponible": true
  }
}
~~~

- [ ] Si el vehículo no está disponible, el sistema retorna:

~~~json
{
  "success": false,
  "statusCode": 409,
  "message": "Vehículo no disponible en el horario solicitado",
  "data": {
    "vehiculo_id": 1,
    "fecha": "2025-01-20",
    "hora_inicio": "10:00",
    "hora_fin": "12:00",
    "disponible": false,
    "horarios_alternativos": [
      {
        "hora_inicio": "13:00",
        "hora_fin": "15:00"
      },
      {
        "hora_inicio": "16:00",
        "hora_fin": "18:00"
      }
    ]
  }
}
~~~

- [ ] Si la fecha es anterior a la actual, el sistema retorna:

~~~json
{
  "success": false,
  "statusCode": 400,
  "message": "Fecha inválida",
  "error": {
    "code": "INVALID_DATA",
    "details": "No se puede reservar en una fecha anterior a la actual"
  }
}
~~~

- [ ] Si hora_inicio es mayor o igual a hora_fin, el sistema retorna:

~~~json
{
  "success": false,
  "statusCode": 400,
  "message": "Horario inválido",
  "error": {
    "code": "INVALID_DATA",
    "details": "La hora de inicio debe ser menor que la hora de fin"
  }
}
~~~

- [ ] Si la duración es menor a 30 minutos, el sistema retorna:

~~~json
{
  "success": false,
  "statusCode": 400,
  "message": "Duración inválida",
  "error": {
    "code": "INVALID_DATA",
    "details": "La duración mínima de reserva es de 30 minutos"
  }
}
~~~

- [ ] Si el vehículo no existe, el sistema retorna error `VEHICLE_NOT_FOUND`.

- [ ] Si el token no es válido o no se envía, el sistema retorna error `UNAUTHORIZED`.

- [ ] Si hay error de conexión a la base de datos, el sistema retorna error `DATABASE_ERROR`.

## 🔧 Notas Técnicas

### Reglas de negocio

- El tiempo máximo de reserva antes de iniciar el viaje es de 15 minutos; pasado este tiempo, la reserva se cancela automáticamente y el vehículo queda disponible nuevamente.
- Un usuario que acumule tres reservas canceladas por no pago o no presentación dentro de un período de 30 días será temporalmente inhabilitado para realizar nuevas reservas durante una semana.

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

### Lógica de superposición

~~~sql
SELECT * FROM reservas 
WHERE vehiculo_id = ? 
AND fecha = ?
AND estado IN ('pendiente', 'confirmada', 'en_curso')
AND (
  (hora_inicio < ? AND hora_fin > ?) OR
  (hora_inicio BETWEEN ? AND ?)
)
~~~

### Cálculo de horarios alternativos

- Si el vehículo no está disponible, buscar el próximo espacio libre después del horario solicitado.
- Sugerir hasta 3 horarios alternativos.
- Considerar bloques de 30 minutos como unidad mínima.

### Índices para rendimiento

- Índice compuesto en (vehiculo_id, fecha, estado).
- Índice en (vehiculo_id, fecha, hora_inicio, hora_fin).

### Manejo de errores

- Códigos de error sugeridos: INVALID_DATA, VEHICLE_NOT_FOUND, UNAUTHORIZED, DATABASE_ERROR.


## 🚀 Endpoint – Validación de disponibilidad

- **Método HTTP:** `GET`

- **Ruta:** `/api/v1/reservas/disponibilidad`

- **Headers:** `Authorization: Bearer <token>`

### 📤 Ejemplo de Request con parámetros

`http GET /api/v1/reservas/disponibilidad?vehiculo_id=1&fecha=2025-01-20&hora_inicio=10:00&hora_fin=12:00`

### 📤 Ejemplo de Respuesta JSON Exitosa (Disponible)

~~~json
{
  "success": true,
  "statusCode": 200,
  "message": "Vehículo disponible",
  "data": {
    "vehiculo_id": 1,
    "fecha": "2025-01-20",
    "hora_inicio": "10:00",
    "hora_fin": "12:00",
    "disponible": true
  }
}
~~~

### 📤 Ejemplo de Respuesta JSON Error (No disponible)

~~~json
{
  "success": false,
  "statusCode": 409,
  "message": "Vehículo no disponible en el horario solicitado",
  "data": {
    "vehiculo_id": 1,
    "fecha": "2025-01-20",
    "hora_inicio": "10:00",
    "hora_fin": "12:00",
    "disponible": false,
    "horarios_alternativos": [
      {
        "hora_inicio": "13:00",
        "hora_fin": "15:00"
      },
      {
        "hora_inicio": "16:00",
        "hora_fin": "18:00"
      }
    ]
  }
}
~~~

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

## ✅ Caso 1: Vehículo disponible sin reservas

- **Precondición:** No existen reservas para el vehículo 1 en la fecha y horario solicitados.

- **Acción:** Ejecutar GET /api/v1/reservas/disponibilidad?vehiculo_id=1&fecha=2025-01-20&hora_inicio=10:00&hora_fin=12:00.

- **Resultado esperado:**
  - Código HTTP 200 OK

  - disponible: true

## ❌ Caso 2: Vehículo no disponible por superposición exacta

- **Precondición:** Existe una reserva de 10:00 a 12:00 para el vehículo 1 en la fecha 2025-01-20.

- **Acción:** Ejecutar la misma consulta.

- **Resultado esperado:**
  - Código HTTP 409 Conflict

  - disponible: false

  - horarios_alternativos contiene opciones

## ❌ Caso 3: Vehículo no disponible por superposición parcial

- **Precondición:** Existe una reserva de 10:00 a 11:00 para el vehículo 1.

- **Acción:** Ejecutar consulta con horario 10:30 a 12:00.

- **Resultado esperado:**
  - Código HTTP 409 Conflict

  - disponible: false

## ❌ Caso 4: Fecha anterior a la actual

- **Precondición:** Ninguna.

- **Acción:** Ejecutar consulta con fecha "2020-01-01".

- **Resultado esperado:**
  - Código HTTP 400 Bad Request

  - error.code: "INVALID_DATA"

## ❌ Caso 5: Hora inicio mayor o igual a hora fin

- **Precondición:** Ninguna.

- **Acción:** Ejecutar consulta con hora_inicio=12:00 y hora_fin=10:00.

- **Resultado esperado:**
  - Código HTTP 400 Bad Request

  - error.code: "INVALID_DATA"


## ❌ Caso 6: Duración menor a 30 minutos

- **Precondición:** Ninguna.

- **Acción:** Ejecutar consulta con hora_inicio=10:00 y hora_fin=10:15.

- **Resultado esperado:**
  - Código HTTP 400 Bad Request

  - error.code: "INVALID_DATA"

## ❌ Caso 7: Vehículo no existe

- **Precondición:** El vehículo con ID 999 no existe.

- **Acción:** Ejecutar consulta con vehiculo_id=999.

- **Resultado esperado:**
  - Código HTTP 404 Not Found

  - error.code: "VEHICLE_NOT_FOUND"

## ✅ Caso 8: Reserva cancelada no afecta disponibilidad

- **Precondición:** Existe una reserva cancelada de 10:00 a 12:00 para el vehículo 1.

- **Acción:** Ejecutar consulta con horario 10:00 a 12:00.

- **Resultado esperado:**
  - Código HTTP 200 OK

  - disponible: true

## ❌ Caso 9: Token no enviado

- **Precondición:** Ninguna.

- **Acción:** Ejecutar consulta sin header Authorization.

- **Resultado esperado:**
  - Código HTTP 401 Unauthorized

  - error.code: "UNAUTHORIZED"

## ❌ Caso 10: Error de conexión a base de datos

- **Precondición:** La base de datos no está disponible.

- **Acción:** Ejecutar consulta bajo condiciones de fallo de BD.

- **Resultado esperado:**
  - Código HTTP 503 Service Unavailable

  - error.code: "DATABASE_ERROR"


## ✅ Definición de Hecho

### Historia: [HU-009] Validación de disponibilidad

### 📦 Alcance Funcional

- [ ] El endpoint GET /api/v1/reservas/disponibilidad está implementado.
- [ ] Se validan los parámetros obligatorios.
- [ ] Se valida que la fecha no sea anterior a la actual.
- [ ] Se valida que hora_inicio sea menor que hora_fin.
- [ ] Se valida duración mínima de 30 minutos.
- [ ] Se consulta correctamente la superposición con reservas activas.
- [ ] Se excluyen reservas canceladas y finalizadas.
- [ ] Se calculan horarios alternativos cuando no está disponible.
- [ ] La respuesta JSON cumple con el contrato definido.

### 🧪 Pruebas Completadas

- [ ] Prueba unitaria para la lógica de superposición.
- [ ] Prueba de integración para vehículo disponible.
- [ ] Prueba de integración para vehículo no disponible.
- [ ] Prueba de integración para fecha inválida.
- [ ] Prueba de integración para horario inválido.
- [ ] Prueba de integración para duración insuficiente.
- [ ] Prueba de integración para vehículo no encontrado.
- [ ] Prueba de integración para reserva cancelada.
- [ ] Prueba de integración para token no enviado.
- [ ] Las pruebas funcionales están documentadas y pasadas.

### 📄 Documentación Técnica

- [ ] Endpoint documentado en Swagger / OpenAPI.
- [ ] Se describe propósito, parámetros de consulta, estructura de respuesta, ejemplos.

### 🔐 Manejo de Errores

- [ ] HTTP 400 para parámetros inválidos (INVALID_DATA).
- [ ] HTTP 404 para vehículo no encontrado (VEHICLE_NOT_FOUND).
- [ ] HTTP 409 para vehículo no disponible.
- [ ] HTTP 401 para token no válido (UNAUTHORIZED).
- [ ] HTTP 503 para error de conexión a base de datos (DATABASE_ERROR).
- [ ] Mensajes de error claros.