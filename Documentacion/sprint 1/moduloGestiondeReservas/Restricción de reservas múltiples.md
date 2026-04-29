# [HU-012] Restricción de reservas múltiples

## 📖 Historia de Usuario

**Como** sistema de EcoMove,

**quiero** limitar la cantidad de reservas activas por usuario a un máximo predefinido,

**para** garantizar un uso equitativo de los vehículos entre todos los usuarios y evitar el acaparamiento de recursos.

## 🔁 Flujo Esperado

- El usuario intenta crear una nueva reserva mediante `POST /api/v1/reservas`.
- Antes de crear la reserva, el sistema cuenta cuántas reservas activas tiene actualmente el usuario.
- Se consideran reservas activas los estados: `pendiente`, `confirmada`, `en_curso`.
- NO se consideran: `finalizada`, `cancelada`.
- Si el usuario ha alcanzado el límite máximo (por defecto 3), se rechaza la nueva reserva.
- El sistema retorna un mensaje indicando el límite alcanzado y sugiriendo cancelar una reserva existente.
- El límite debe ser configurable mediante variable de entorno.

## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [ ] Se valida el límite de reservas activas antes de crear una nueva reserva (en `POST /api/v1/reservas`).
- [ ] Se cuentan las reservas con estado: `pendiente`, `confirmada`, `en_curso`.
- [ ] NO se cuentan las reservas con estado: `finalizada`, `cancelada`.
- [ ] El límite por defecto es **3 reservas activas por usuario**.
- [ ] El límite debe ser configurable mediante variable de entorno `MAX_ACTIVE_RESERVATIONS`.
- [ ] Si el usuario tiene menos del límite, se permite crear la reserva.
- [ ] Si el usuario tiene el límite o más, se rechaza la creación con mensaje claro.
- [ ] La validación se aplica solo en la creación de reservas (no afecta consultas ni cancelaciones).

### 2. 📆 Estructura de la información

- [ ] Si el usuario ha alcanzado el límite, el sistema retorna:

~~~json
{
  "success": false,
  "statusCode": 400,
  "message": "Límite de reservas activas alcanzado",
  "error": {
    "code": "MAX_ACTIVE_RESERVATIONS",
    "details": "Has alcanzado el límite de 3 reservas activas. Cancela una reserva existente para continuar",
    "reservas_activas": 3,
    "limite_maximo": 3
  }
}
~~~

- [ ] Si la creación es exitosa, se retorna la respuesta estándar de HU-010.
- [ ] Si el usuario tiene reservas activas pero no ha alcanzado el límite, la creación continúa normalmente.

## 🔧 Notas Técnicas

### Reglas de negocio

- Un usuario que acumule tres reservas canceladas por no pago o no presentación dentro de un período de 30 días será temporalmente inhabilitado para realizar nuevas reservas durante una semana (aplica después de cancelación, no en creación).
- El tiempo máximo de reserva antes de iniciar el viaje es de 15 minutos; pasado este tiempo, la reserva se cancela automáticamente.

### Base de datos (tabla `reservas`)

La columna `estado` debe tener los valores:

- `pendiente`: cuenta como activa ✅
- `confirmada`: cuenta como activa ✅
- `en_curso`: cuenta como activa ✅
- `finalizada`: NO cuenta ❌
- `cancelada`: NO cuenta ❌

### Consulta para contar reservas activas

~~~sql
SELECT COUNT(*) FROM reservas 
WHERE usuario_id = ? 
AND estado IN ('pendiente', 'confirmada', 'en_curso')
~~~

### Configuración por variable de entorno

- Variable: `MAX_ACTIVE_RESERVATIONS`
- Valor por defecto: `3`
- Ubicación: archivo `.env` o configuración del sistema

### Integración con HU-010

- Esta validación debe ejecutarse dentro del servicio de creación de reserva.
- Debe hacerse antes de validar disponibilidad del vehículo (para evitar trabajo innecesario).

### Manejo de errores

- Códigos de error sugeridos: `MAX_ACTIVE_RESERVATIONS`.

## 🚀 Endpoint – Creación de reserva (con validación)

- **Método HTTP:** `POST`
- **Ruta:** `/api/v1/reservas`
- **Headers:** `Authorization: Bearer <token>`

### 📤 Ejemplo de Request JSON

~~~json
{
  "vehiculo_id": 1,
  "fecha": "2025-01-20",
  "hora_inicio": "10:00",
  "hora_fin": "12:00"
}
~~~

### 📤 Ejemplo de Respuesta JSON Exitosa (Dentro del límite)

~~~json
{
  "success": true,
  "statusCode": 201,
  "message": "Reserva creada exitosamente",
  "data": {
    "id": 1001,
    "usuario_id": 1,
    "vehiculo_id": 1,
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

### 📤 Ejemplo de Respuesta JSON Error (Límite alcanzado)

~~~json
{
  "success": false,
  "statusCode": 400,
  "message": "Límite de reservas activas alcanzado",
  "error": {
    "code": "MAX_ACTIVE_RESERVATIONS",
    "details": "Has alcanzado el límite de 3 reservas activas. Cancela una reserva existente para continuar",
    "reservas_activas": 3,
    "limite_maximo": 3
  }
}
~~~

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

## ✅ Caso 1: Usuario con menos de 3 reservas activas

- **Precondición:** Usuario tiene 2 reservas activas (`pendiente`, `confirmada` o `en_curso`).
- **Acción:** Intentar crear una nueva reserva.
- **Resultado esperado:**
  - Código HTTP 201 Created
  - La reserva se crea exitosamente
  - El usuario ahora tiene 3 reservas activas

## ❌ Caso 2: Usuario con 3 reservas activas (límite alcanzado)

- **Precondición:** Usuario tiene 3 reservas activas.
- **Acción:** Intentar crear una nueva reserva.
- **Resultado esperado:**
  - Código HTTP 400 Bad Request
  - error.code: "MAX_ACTIVE_RESERVATIONS"
  - La reserva NO se crea

## ❌ Caso 3: Usuario con 4 reservas activas (borde superior)

- **Precondición:** Usuario tiene 4 reservas activas (caso extremo, debería ser imposible si la validación funciona).
- **Acción:** Intentar crear una nueva reserva.
- **Resultado esperado:**
  - Código HTTP 400 Bad Request
  - error.code: "MAX_ACTIVE_RESERVATIONS"

## ✅ Caso 4: Reservas finalizadas no cuentan para el límite

- **Precondición:** Usuario tiene 2 reservas activas + 5 reservas finalizadas.
- **Acción:** Intentar crear una nueva reserva.
- **Resultado esperado:**
  - Código HTTP 201 Created
  - La cuenta solo considera las 2 activas, no las 5 finalizadas

## ✅ Caso 5: Reservas canceladas no cuentan para el límite

- **Precondición:** Usuario tiene 2 reservas activas + 3 reservas canceladas.
- **Acción:** Intentar crear una nueva reserva.
- **Resultado esperado:**
  - Código HTTP 201 Created
  - La cuenta solo considera las 2 activas, no las 3 canceladas

## ✅ Caso 6: Cancelar una reserva libera cupo

- **Precondición:** Usuario tiene 3 reservas activas (límite alcanzado).
- **Acción:** Cancelar una reserva (HU-011), luego intentar crear una nueva.
- **Resultado esperado:**
  - Cancelación exitosa
  - Ahora tiene 2 reservas activas
  - Nueva reserva se crea exitosamente

## ✅ Caso 7: Límite configurable por variable de entorno

- **Precondición:** Cambiar `MAX_ACTIVE_RESERVATIONS` a 5.
- **Acción:** Usuario con 4 reservas activas intenta crear una nueva.
- **Resultado esperado:**
  - Código HTTP 201 Created (aún no alcanza el nuevo límite de 5)

## ❌ Caso 8: Usuario con 5 reservas activas (nuevo límite)

- **Precondición:** `MAX_ACTIVE_RESERVATIONS` = 5. Usuario tiene 5 reservas activas.
- **Acción:** Intentar crear una nueva reserva.
- **Resultado esperado:**
  - Código HTTP 400 Bad Request
  - error.code: "MAX_ACTIVE_RESERVATIONS"

## ✅ Caso 9: El límite no afecta a administradores (si aplica)

- **Precondición:** Usuario con rol administrador tiene 3 reservas activas.
- **Acción:** Intentar crear una nueva reserva.
- **Resultado esperado:** Depende de la regla de negocio. Si los administradores también tienen límite, debería aplicar igual.

## ✅ Caso 10: Verificar mensaje de error con detalles

- **Precondición:** Usuario con 3 reservas activas.
- **Acción:** Intentar crear nueva reserva.
- **Resultado esperado:**
  - El mensaje incluye reservas_activas: 3
  - El mensaje incluye limite_maximo: 3
  - El mensaje sugiere cancelar una reserva existente

## ❌ Caso 11: Error de conexión a base de datos

- **Precondición:** La base de datos no está disponible.
- **Acción:** Intentar crear una reserva bajo condiciones de fallo de BD.
- **Resultado esperado:**
  - Código HTTP 503 Service Unavailable
  - error.code: "DATABASE_ERROR"

## ✅ Definición de Hecho

### Historia: [HU-012] Restricción de reservas múltiples

### 📦 Alcance Funcional

- [ ] Se valida el límite de reservas activas en el servicio de creación de reservas.
- [ ] Se cuentan correctamente los estados: `pendiente`, `confirmada`, `en_curso`.
- [ ] No se cuentan `finalizada` ni `cancelada`.
- [ ] El límite por defecto es 3.
- [ ] El límite es configurable por variable de entorno `MAX_ACTIVE_RESERVATIONS`.
- [ ] Se rechaza la creación si el usuario alcanzó el límite.
- [ ] El mensaje de error incluye el número de reservas activas y el límite máximo.
- [ ] La respuesta JSON cumple con el contrato definido.

### 🧪 Pruebas Completadas

- [ ] Prueba unitaria para la consulta de conteo de reservas activas.
- [ ] Prueba de integración para usuario con menos del límite.
- [ ] Prueba de integración para usuario con límite alcanzado.
- [ ] Prueba de integración para usuario con reservas finalizadas.
- [ ] Prueba de integración para usuario con reservas canceladas.
- [ ] Prueba de integración para cancelación que libera cupo.
- [ ] Prueba de integración para límite configurable.
- [ ] Las pruebas funcionales están documentadas y pasadas.

### 📄 Documentación Técnica

- [ ] Variable de entorno `MAX_ACTIVE_RESERVATIONS` documentada.
- [ ] Endpoint documentado en Swagger / OpenAPI.
- [ ] Se describe la validación de límite en la documentación.

### 🔐 Manejo de Errores

- [ ] HTTP 400 para reservas activas excedidas (MAX_ACTIVE_RESERVATIONS).
- [ ] HTTP 503 para error de conexión a base de datos (DATABASE_ERROR).
- [ ] Mensajes de error claros con detalles del límite.