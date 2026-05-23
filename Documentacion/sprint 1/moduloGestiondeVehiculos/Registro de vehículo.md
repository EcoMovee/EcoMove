# [HU-005] Registro de vehículo

## 📖 Historia de Usuario

**Como** administrador de EcoMove,
**quiero** registrar nuevos vehículos en la plataforma proporcionando su tipo, modelo, ubicación y tarifa por hora,
**para** garantizar que la información almacenada sea completa, consistente y sin duplicidades.

## 🔁 Flujo Esperado

- El administrador envía los datos del vehículo (tipo, modelo, ubicacion, tarifaPorHora) al endpoint `POST /api/v1/vehiculos`.
- El sistema valida que todos los campos requeridos estén presentes y tengan el formato correcto.
- El sistema verifica que el vehículo no exista previamente en la tabla `vehiculos`.
- Si es válido, el sistema inserta un nuevo registro en la tabla `vehiculos` con estado "disponible".
- El sistema retorna los datos del vehículo creado.

## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [ ] Se expone un endpoint `POST /api/v1/vehiculos` para el registro de vehículos.
- [ ] Se valida que los campos `tipo`, `modelo`, `ubicacion` y `tarifaPorHora` sean obligatorios.
- [ ] Se valida que el campo `tipo` sea uno de los valores permitidos: "carro", "moto", "bicicleta".
- [ ] Se valida que `tarifaPorHora` sea un número decimal mayor a 0.
- [ ] Se valida que el vehículo no exista previamente en la tabla `vehiculos`.
- [ ] El estado inicial del vehículo debe ser "disponible".

### 2. 📆 Estructura de la información

- [ ] Se responde con la siguiente estructura en JSON para registro exitoso:

```json
{
  "success": true,
  "statusCode": 201,
  "message": "Vehículo creado correctamente",
  "data": {
    "id": 1,
    "tipo": "moto",
    "modelo": "Scooter Eléctrica X1",
    "ubicacion": "Centro comercial Unicentro",
    "tarifaPorHora": 2500,
    "estado": "disponible"
  }
}
```

- [ ]  RSi el vehículo ya existe, el sistema retorna:

```json
{
  "success": false,
  "statusCode": 400,
  "message": "El vehículo ya está registrado",
  "error": {
    "code": "VEHICLE_ALREADY_EXISTS",
    "details": "El vehículo con modelo Scooter Eléctrica X1 ya existe en el sistema"
  }
}
```
- [ ]   Si los datos son inválidos, el sistema retorna:

```json
{
  "success": false,
  "statusCode": 400,
  "message": "Datos inválidos",
  "error": {
    "code": "INVALID_DATA",
    "details": "La tarifa por hora debe ser mayor a 0"
  }
}
```
## 🔧 Notas Técnicas

### Reglas de negocio
- Los vehículos eléctricos solo pueden ser ofrecidos en alquiler si cuentan con un nivel de batería suficiente para garantizar la autonomía mínima establecida por la empresa (15 km o 60 minutos de uso).
- Un vehículo que presenta reportes de daño o mantenimiento recurrente debe ser retirado temporalmente de la flota hasta su revisión técnica.

### Base de datos (tabla `vehiculos`)
- La tabla debe incluir las siguientes columnas:
  - id: SERIAL / AUTO_INCREMENT (PK)
  - tipo: ENUM('carro', 'moto', 'bicicleta'), NOT NULL
  - modelo: VARCHAR(100), NOT NULL, UNIQUE
  - ubicacion: VARCHAR(255), NOT NULL
  - tarifaPorHora: DECIMAL(10,2), NOT NULL
  - estado: ENUM('disponible', 'en_uso', 'mantenimiento'), DEFAULT 'disponible'
  - fecha_registro: TIMESTAMP, DEFAULT CURRENT_TIMESTAMP
  - nivel_bateria: INT, DEFAULT 100 (porcentaje)

### Seguridad
- El endpoint debe estar protegido con JWT.
- Se debe validar el rol administrador desde el middleware.
- Solo administradores pueden registrar vehículos.

### Manejo de errores
- Códigos de error sugeridos: VEHICLE_ALREADY_EXISTS, INVALID_DATA, UNAUTHORIZED.

## 🚀 Endpoint – Registro de vehiculo

- **Método HTTP:** `POST`

- **Ruta:** `/api/v1/vehiculos`

- **Headers:** Authorization: Bearer <token_administrador>

📤 Ejemplo de Request JSON

```json
{
  "tipo": "moto",
  "modelo": "Scooter Eléctrica X1",
  "ubicacion": "Centro comercial Unicentro",
  "tarifaPorHora": 2500
}
```
📤 Ejemplo de Respuesta JSON Exitosa

```json
{
  "success": true,
  "statusCode": 201,
  "message": "Vehículo creado correctamente",
  "data": {
    "id": 1,
    "tipo": "moto",
    "modelo": "Scooter Eléctrica X1",
    "ubicacion": "Centro comercial Unicentro",
    "tarifaPorHora": 2500,
    "estado": "disponible"
  }
}
```
📤 Ejemplo de Respuesta JSON Error

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

## ✅ Caso 1: Registro exitoso de vehículo

- **Precondición:**  El vehículo con modelo Scooter Eléctrica X1 no existe en la tabla vehiculos.

- **Acción:** Ejecutar POST /api/v1/vehiculos con el JSON de ejemplo.

- **Resultado esperado:**

- Código HTTP 201 Created

- success: true

- statusCode: 201

- data.estado: "disponible"

## ❌ Caso 2: Vehículo ya registrado

- **Precondición:** El vehículo con modelo Scooter Eléctrica X1 ya existe.

- **Acción:** Ejecutar POST /api/v1/vehiculos con el mismo modelo.

- **Resultado esperado:**

- Código HTTP 400 Bad Request

- error.code: "VEHICLE_ALREADY_EXISTS"

## ❌ Caso 3: Tarifa por hora inválida

- **Precondición:** Ninguna.

- **Acción:** Ejecutar POST /api/v1/vehiculos con tarifaPorHora = 0.

- **Resultado esperado:**

- Código HTTP 400 Bad Request

- error.code: "INVALID_DATA"

## ❌ Caso 4: Tipo de vehículo inválido

- **Precondición:** Ninguna.

- **Acción:** Ejecutar POST /api/v1/vehiculos con tipo = "avion".

- **Resultado esperado:**

- Código HTTP 400 Bad Request

- error.code: "INVALID_DATA"

## ❌ Caso 5: Usuario no administrador intenta registrar

- **Precondición:** Usuario autenticado con rol usuario.

- **Acción:** Ejecutar POST /api/v1/vehiculos.

- **Resultado esperado:**

- Código HTTP 403 Forbidden

- message: "Acceso denegado. Se requieren privilegios de administrador"

## ❌ Caso 6: Error de conexión a base de datos

- **Precondición:** La base de datos no está disponible.

- **Acción:** Ejecutar POST /api/v1/vehiculos bajo condiciones de fallo de BD.

- **Resultado esperado:**

- Código HTTP 503 Service Unavailable

- success: false

## ✅ Definición de Hecho

### Historia: [HU-005] Registro de vehículo

### 📦 Alcance Funcional

- [ ] El endpoint POST /api/v1/vehiculos está implementado.
- [ ] Solo administradores pueden registrar vehículos.
- [ ] Se valida que el vehículo no exista previamente.
- [ ] Se valida que tipo sea un valor permitido.
- [ ] Se valida que tarifaPorHora sea mayor a 0.
- [ ] El estado inicial del vehículo es "disponible".
- [ ] La respuesta JSON cumple con el contrato definido.

### 🧪 Pruebas Completadas

- [ ] Pruebas unitarias para validaciones de formato.
- [ ] Prueba de integración para registro exitoso.
- [ ] Prueba de integración para vehículo duplicado.
- [ ] Prueba de integración para datos inválidos.
- [ ] Prueba de integración para usuario no administrador.
- [ ] Las pruebas funcionales están documentadas y pasadas.

### 📄 Documentación Técnica

- [ ] Endpoint documentado en Swagger / OpenAPI.
- [ ] Se describe propósito, campos de entrada y salida, ejemplos.

### 🔐 Manejo de Errores

- [ ] HTTP 400 para errores de validación.
- [ ] HTTP 403 para permisos insuficientes.
- [ ] HTTP 503 cuando no hay conexión a la base de datos.
- [ ] Mensajes de error claros.