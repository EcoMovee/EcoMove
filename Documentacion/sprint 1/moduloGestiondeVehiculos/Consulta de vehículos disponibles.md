# [HU-006] Consulta de vehículos disponibles

## 📖 Historia de Usuario

**Como** usuario autenticado de EcoMove,
**quiero** consultar la lista de vehículos disponibles en tiempo real, filtrando por tipo y ubicación,
**para** seleccionar un vehículo que se ajuste a mis necesidades y ubicación actual.

## 🔁 Flujo Esperado

- El usuario envía una solicitud al endpoint `GET /api/v1/vehiculos/disponibles`.

- El sistema excluye automáticamente los vehículos con estado "en_uso" o "mantenimiento".

- El sistema aplica los filtros enviados por el usuario (tipo, ubicación).

- El sistema calcula la distancia aproximada desde la ubicación del usuario.

- El sistema retorna la lista de vehículos disponibles con su información.

## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [ ] Se expone un endpoint `GET /api/v1/vehiculos/disponibles` para consultar vehículos disponibles.

- [ ] Se excluyen automáticamente vehículos con estado `en_uso` o `mantenimiento`.

- [ ] Se permite filtrar por `tipo` (carro, moto, bicicleta).

- [ ] Se permite filtrar por `ubicacion` (radio en kilómetros desde coordenadas).

- [ ] Se calcula la distancia aproximada desde la ubicación del usuario a cada vehículo.

- [ ] La lista se ordena por distancia (más cercano primero) por defecto.

### 2. 📆 Estructura de la información

- [ ] Se responde con la siguiente estructura en JSON para consulta exitosa:

```json
{
  "success": true,
  "statusCode": 200,
  "message": "Vehículos disponibles encontrados",
  "data": {
    "total": 15,
    "filtros_aplicados": {
      "tipo": "moto",
      "latitud": 4.7110,
      "longitud": -74.0721,
      "radio_km": 5
    },
    "vehiculos": [
      {
        "id": 1,
        "tipo": "moto",
        "modelo": "Scooter Eléctrica X1",
        "ubicacion": "Calle 123",
        "tarifaPorHora": 2500,
        "distancia_km": 1.2,
        "nivel_bateria": 85
      }
    ]
  }
}
```

- [ ]  Si no hay vehículos disponibles con los filtros aplicados, el sistema retorna:

```json
{
  "success": true,
  "statusCode": 200,
  "message": "No hay vehículos disponibles con los filtros seleccionados",
  "data": {
    "total": 0,
    "vehiculos": []
  }
}
```
- [ ]   Si los parámetros de filtro son inválidos, el sistema retorna:

```json
{
  "success": false,
  "statusCode": 400,
  "message": "Parámetros de filtro inválidos",
  "error": {
    "code": "INVALID_DATA",
    "details": "El radio debe ser un número positivo"
  }
}
```

- [ ]   Si el token no es válido o no se envía, el sistema retorna:

```json
{
  "success": false,
  "statusCode": 401,
  "message": "No autenticado",
  "error": {
    "code": "UNAUTHORIZED",
    "details": "Token no válido o expirado"
  }
}
```

- [ ]   Si hay error de conexión a la base de datos, el sistema retorna:

```json
{
  "success": false,
  "statusCode": 503,
  "message": "Error de conexión con la base de datos",
  "error": {
    "code": "DATABASE_ERROR",
    "details": "Intente nuevamente más tarde"
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
  - modelo: VARCHAR(100), NOT NULL
  - ubicacion: VARCHAR(255), NOT NULL
  - latitud: DECIMAL(10,8), NULLABLE
  - longitud: DECIMAL(11,8), NULLABLE
  - tarifaPorHora: DECIMAL(10,2), NOT NULL
  - estado: ENUM('disponible', 'en_uso', 'mantenimiento'), DEFAULT 'disponible'
  - nivel_bateria: INT, DEFAULT 100
  - fecha_registro: TIMESTAMP, DEFAULT CURRENT_TIMESTAMP

### Seguridad
- El endpoint debe estar protegido con JWT.
- No se requiere rol específico (usuarios autenticados pueden consultar).

### Manejo de errores
- Códigos de error sugeridos: INVALID_DATA, UNAUTHORIZED, DATABASE_ERROR.

## 🚀 Endpoint – Consulta de vehículos disponibles

- **Método HTTP:** `GET`

- **Ruta:** `/api/v1/vehiculos/disponibles`

- **Headers:** Authorization: Bearer <token>

📤 Ejemplo de Request con parámetros

`GET /api/v1/vehiculos/disponibles?tipo=moto&latitud=4.7110&longitud=-74.0721&radio_km=5`

📤 Ejemplo de Request sin parámetros

`GET /api/v1/vehiculos/disponibles`

📤 Ejemplo de Respuesta JSON Exitosa

```json
{
  "success": true,
  "statusCode": 200,
  "message": "Vehículos disponibles encontrados",
  "data": {
    "total": 15,
    "filtros_aplicados": {
      "tipo": "moto",
      "latitud": 4.7110,
      "longitud": -74.0721,
      "radio_km": 5
    },
    "vehiculos": [
      {
        "id": 1,
        "tipo": "moto",
        "modelo": "Scooter Eléctrica X1",
        "ubicacion": "Calle 123",
        "tarifaPorHora": 2500,
        "distancia_km": 1.2,
        "nivel_bateria": 85
      }
    ]
  }
}
```
📤 Ejemplo de Respuesta JSON Sin Resultados

```json
{
  "success": true,
  "statusCode": 200,
  "message": "No hay vehículos disponibles con los filtros seleccionados",
  "data": {
    "total": 0,
    "vehiculos": []
  }
}
```
📤 Ejemplo de Respuesta JSON Error

```json
{
  "success": false,
  "statusCode": 400,
  "message": "Parámetros de filtro inválidos",
  "error": {
    "code": "INVALID_DATA",
    "details": "El radio debe ser un número positivo"
  }
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

## ✅ Caso 1: Consulta exitosa con filtros

- **Precondición:**  Existen 5 motos disponibles, 3 carros disponibles, 2 motos en uso.

- **Acción:** GET /api/v1/vehiculos/disponibles?tipo=moto&latitud=4.7110&longitud=-74.0721&radio_km=5

- **Resultado esperado:**

- Código HTTP 200 OK

- success: true

- Solo retorna motos (5 resultados)

- Cada vehículo tiene distancia_km calculada

- Lista ordenada por distancia (menor a mayor)

## ✅ Caso 2: Consulta exitosa sin filtros

- **Precondición:** Existen 8 vehículos disponibles (sin importar tipo).

- **Acción:** Ejecutar GET /api/v1/vehiculos/disponibles.

- **Resultado esperado:**

- Código HTTP 200 OK

- total: 8

- No se excluyen vehículos por tipo

- Los vehículos en en_uso o mantenimiento NO aparecen

## ✅ Caso 3: No hay vehículos disponibles

- **Precondición:** Todos los vehículos están en en_uso o mantenimiento.

- **Acción:** : Ejecutar GET /api/v1/vehiculos/disponibles.

- **Resultado esperado:**

- Código HTTP 200 OK

- total: 0

- vehiculos: []

- message: "No hay vehículos disponibles con los filtros seleccionados"

## ❌ Caso 4: Radio de búsqueda inválido

- **Precondición:** Ninguna.

- **Acción:** GET /api/v1/vehiculos/disponibles?radio_km=-5.

- **Resultado esperado:**

- Código HTTP 400 Bad Request

- error.code: "INVALID_DATA"

## ❌ Caso 5: Tipo de vehículo inválido

- **Precondición:** Ninguna.

- **Acción:** Ejecutar GET /api/v1/vehiculos/disponibles?tipo=avion.

- **Resultado esperado:**

- Código HTTP 400 Bad Request

- error.code: "INVALID_DATA"

## ❌ Caso 6: Token no enviado

- **Precondición:** Ninguna.

- **Acción:** Ejecutar GET /api/v1/vehiculos/disponibles sin header Authorization.

- **Resultado esperado:**

- Código HTTP 401 Unauthorized

- error.code: "UNAUTHORIZED"

## ❌ Caso 7: Error de conexión a base de datos

- **Precondición:** La base de datos no está disponible.

- **Acción:** Ejecutar GET /api/v1/vehiculos/disponibles bajo condiciones de fallo de BD.

- **Resultado esperado:**

- Código HTTP 503 Service Unavailable

- error.code: "DATABASE_ERROR"

## ✅ Caso 8: Validación de exclusión de vehículos no disponibles

- **Precondición:** Hay 3 vehículos en mantenimiento y 2 en en_uso.

- **Acción:** Ejecutar GET /api/v1/vehiculos/disponibles.

- **Resultado esperado:**

- Los 5 vehículos NO aparecen en los resultados.

## ✅ Definición de Hecho

### Historia: [HU-006] Consulta de vehículos disponibles

### 📦 Alcance Funcional

- [ ] El endpoint GET /api/v1/vehiculos/disponibles está implementado.
- [ ] Se excluyen automáticamente vehículos con estado en_uso o mantenimiento.
- [ ] Se permite filtrar por tipo (carro, moto, bicicleta).
- [ ] Se permite filtrar por ubicación (coordenadas + radio).
- [ ] Se calcula la distancia usando fórmula de Haversine.
- [ ] Los resultados se ordenan por distancia (más cercano primero).
- [ ] La respuesta JSON cumple con el contrato definido.

### 🧪 Pruebas Completadas

- [ ] Pruebas unitarias para el cálculo de distancia.
- [ ] Prueba de integración para consulta con filtros.
- [ ] Prueba de integración para consulta sin filtros.
- [ ] Prueba de integración para consulta sin resultados.
- [ ] Prueba de integración para filtros inválidos.
- [ ] Prueba de integración para token no enviado.
- [ ] Prueba de integración para exclusión de vehículos no disponibles.
- [ ] Las pruebas funcionales están documentadas y pasadas.

### 📄 Documentación Técnica

- [ ] Endpoint documentado en Swagger / OpenAPI.
- [ ] Se describe propósito, parámetros de consulta, estructura de respuesta, ejemplos.

### 🔐 Manejo de Errores

- [ ] HTTP 400 para parámetros de filtro inválidos (INVALID_DATA).
- [ ] HTTP 401 para token no válido o no enviado (UNAUTHORIZED).
- [ ] HTTP 503 para error de conexión a base de datos (DATABASE_ERROR).
- [ ] Mensajes de error claros.