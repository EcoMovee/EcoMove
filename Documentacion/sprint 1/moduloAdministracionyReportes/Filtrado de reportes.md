# [HU-024] Filtrado de Reportes

## 📖 Historia de Usuario

> **Como** administrador de EcoMove,
> **quiero** aplicar filtros combinados en todos los reportes disponibles (reservas, pagos, uso de vehículos) para obtener información específica,
> **para** obtener información relevante según mis necesidades del momento sin tener que revisar datos no deseados.

---

## 🔁 Flujo Esperado

1. El administrador accede a cualquiera de los endpoints de reporte: `/api/v1/reportes/reservas`, `/api/v1/reportes/pagos` o `/api/v1/reportes/vehiculos-top`.
2. El administrador aplica filtros combinados según el tipo de reporte.
3. Los filtros se pueden aplicar en cualquier orden y combinación.
4. Al cambiar un filtro, el reporte se actualiza dinámicamente (el backend procesa los nuevos parámetros).
5. El sistema valida la combinación de filtros y retorna los datos correspondientes.

---

## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y Lógica del Servicio

#### Reporte de Reservas (`/api/v1/reportes/reservas`) — HU-021

| Parámetro | Tipo | Valores permitidos |
|---|---|---|
| `fecha_inicio` | DATE | Cualquier fecha válida |
| `fecha_fin` | DATE | Cualquier fecha válida |
| `estados` | Array | `pendiente`, `confirmada`, `en_curso`, `finalizada`, `cancelada` |
| `usuario_id` | INT | ID de usuario existente |
| `vehiculo_id` | INT | ID de vehículo existente |

- [ ] Todos los filtros son opcionales y combinables.
- [ ] Los filtros se pueden aplicar en cualquier orden.

#### Reporte de Pagos (`/api/v1/reportes/pagos`) — HU-022

| Parámetro | Tipo | Valores permitidos |
|---|---|---|
| `fecha_inicio` | DATE | Cualquier fecha válida |
| `fecha_fin` | DATE | Cualquier fecha válida |
| `metodo_pago` | String | `tarjeta_credito`, `tarjeta_debito`, `monedero_electronico` |
| `estado` | String | `aprobado`, `rechazado`, `reembolsado` |
| `usuario_id` | INT | ID de usuario existente |
| `rango_monto_min` | DECIMAL | ≥ 0 |
| `rango_monto_max` | DECIMAL | > `rango_monto_min` |

- [ ] Todos los filtros son opcionales y combinables.

#### Ranking de Vehículos (`/api/v1/reportes/vehiculos-top`) — HU-023

| Parámetro | Tipo | Valores permitidos |
|---|---|---|
| `periodo` | String | `dia`, `semana`, `mes`, `rango` |
| `fecha_inicio` | DATE | Requerido si `periodo=rango` |
| `fecha_fin` | DATE | Requerido si `periodo=rango` |
| `tipo_vehiculo` | String | `carro`, `moto`, `bicicleta` |
| `ubicacion` | String | Filtro parcial por texto |
| `limite` | INT | Número máximo de vehículos (default `10`) |

- [ ] Todos los filtros son opcionales y combinables.

---

### 2. 📆 Estructura de la Información

#### Respuesta exitosa con filtros aplicados

```json
{
  "success": true,
  "statusCode": 200,
  "message": "Reporte generado exitosamente",
  "data": {
    "filtros_aplicados": {
      "fecha_inicio": "2025-01-01",
      "fecha_fin": "2025-01-31",
      "estados": ["confirmada", "finalizada"],
      "usuario_id": 123,
      "vehiculo_id": 5
    },
    "total_registros": 15,
    "reporte": [...]
  }
}
```

#### Sin resultados con los filtros aplicados

```json
{
  "success": true,
  "statusCode": 200,
  "message": "No hay datos con los filtros seleccionados",
  "data": {
    "filtros_aplicados": {...},
    "total_registros": 0,
    "reporte": []
  }
}
```

#### Tabla de errores

| Situación | Código HTTP | Código de error |
|---|---|---|
| Filtros inválidos o incompatibles | `400 Bad Request` | `INVALID_DATA` |
| Rango de fechas inválido | `400 Bad Request` | `INVALID_DATE_RANGE` |
| Usuario no administrador | `403 Forbidden` | `FORBIDDEN` |
| Token inválido o no enviado | `401 Unauthorized` | `UNAUTHORIZED` |
| Error de conexión a BD | `503 Service Unavailable` | `DATABASE_ERROR` |

---

## 🔧 Notas Técnicas

### Reglas de Negocio

> Todo cambio en las tarifas de alquiler debe ser aprobado por un administrador con nivel de privilegio superior.
> Un vehículo que presenta reportes de daño o mantenimiento recurrente debe ser **retirado temporalmente** de la flota.

### Construcción de Consultas Dinámicas

```sql
-- Ejemplo base para reporte de reservas
SELECT r.*, u.nombre as usuario_nombre, v.tipo as vehiculo_tipo
FROM reservas r
JOIN usuarios u ON r.usuario_id = u.id
JOIN vehiculos v ON r.vehiculo_id = v.id
WHERE 1=1
-- Condiciones agregadas dinámicamente según filtros presentes:
-- AND r.fecha BETWEEN :fecha_inicio AND :fecha_fin
-- AND r.estado IN (:estados)
-- AND r.usuario_id = :usuario_id
-- AND r.vehiculo_id = :vehiculo_id
```

### Validación de Filtros Especiales

| Filtro | Tipo | Validación |
|---|---|---|
| `estados` | Array | Cada valor debe ser un estado válido |
| `rango_monto_min` | Decimal | Debe ser ≥ 0 |
| `rango_monto_max` | Decimal | Debe ser > `rango_monto_min` |
| `fecha_inicio` | DATE | No puede ser posterior a `fecha_fin` |
| `fecha_fin` | DATE | No puede ser anterior a `fecha_inicio` |

### Índices Recomendados para Rendimiento

- `reservas`: índice en `(fecha_creacion, estado, usuario_id, vehiculo_id)`
- `pagos`: índice en `(fecha_pago, estado, metodo_pago, usuario_id)`
- `vehiculos`: índice en `(tipo, ubicacion)`

### Seguridad

- Los endpoints deben estar protegidos con **JWT**.
- Validar rol `administrador` en el middleware.

---

## 🚀 Endpoints

| Endpoint | Método | Ruta | Headers |
|---|---|---|---|
| Reporte de reservas | `GET` | `/api/v1/reportes/reservas` | `Authorization: Bearer <token_administrador>` |
| Reporte de pagos | `GET` | `/api/v1/reportes/pagos` | `Authorization: Bearer <token_administrador>` |
| Ranking de vehículos | `GET` | `/api/v1/reportes/vehiculos-top` | `Authorization: Bearer <token_administrador>` |

### 📤 Ejemplos de Request con Filtros Combinados

```http
GET /api/v1/reportes/reservas?fecha_inicio=2025-01-01&fecha_fin=2025-01-31&estados=confirmada,finalizada&usuario_id=123&vehiculo_id=5

GET /api/v1/reportes/pagos?metodo_pago=tarjeta_credito&estado=aprobado&rango_monto_min=1000&rango_monto_max=10000

GET /api/v1/reportes/vehiculos-top?periodo=rango&fecha_inicio=2025-01-01&fecha_fin=2025-01-31&tipo_vehiculo=moto&ubicacion=Centro&limite=20
```

---

## 🧪 Casos de Prueba

### ✅ Casos Exitosos

| # | Caso | Acción | Resultado Esperado |
|---|---|---|---|
| 1 | Filtros combinados en reservas | `GET ...?fecha_inicio=2025-01-01&fecha_fin=2025-01-31&estados=confirmada&usuario_id=123` | HTTP 200, solo reservas del usuario 123, enero 2025, estado `confirmada` |
| 2 | Filtros combinados en pagos | `GET ...?metodo_pago=tarjeta_credito&estado=aprobado&rango_monto_min=1000&rango_monto_max=10000` | HTTP 200, solo pagos con tarjeta crédito, aprobados, monto entre 1000 y 10000 |
| 3 | Filtros combinados en vehículos top | `GET ...?periodo=mes&tipo_vehiculo=moto&ubicacion=Centro` | HTTP 200, solo motos cuya ubicación contiene "Centro" en el último mes |
| 4 | Filtros sin resultados | Filtros que no coinciden con ningún registro | HTTP 200, `total_registros=0`, `reporte=[]` |
| 5 | Filtros en cualquier orden | `GET ...?vehiculo_id=5&usuario_id=123&estados=finalizada&fecha_inicio=2025-01-01&fecha_fin=2025-01-31` | Mismo resultado independiente del orden de los parámetros |
| 6 | Filtro de rango de montos correcto | `GET ...?rango_monto_min=1000&rango_monto_max=5000` | HTTP 200, pagos con monto entre 1000 y 5000 |
| 10 | Sin filtros (todos los datos) | `GET /api/v1/reportes/reservas` sin parámetros | HTTP 200, retorna todas las reservas |

### ❌ Casos de Error

| # | Caso | Acción | Resultado Esperado |
|---|---|---|---|
| 7 | Rango de montos inválido (`min > max`) | `GET ...?rango_monto_min=5000&rango_monto_max=1000` | HTTP 400, `error.code: "INVALID_DATA"` |
| 8 | `fecha_inicio` posterior a `fecha_fin` | `GET ...?fecha_inicio=2025-01-31&fecha_fin=2025-01-01` | HTTP 400, `error.code: "INVALID_DATE_RANGE"` |
| 9 | Estado inválido en filtro | `GET ...?estados=aprobado` (no es estado de reserva) | HTTP 400, `error.code: "INVALID_DATA"` |
| 11 | Usuario no administrador | Cualquier endpoint con token de rol `usuario` | HTTP 403, `error.code: "FORBIDDEN"` |
| 12 | Token no enviado | Cualquier endpoint sin header `Authorization` | HTTP 401, `error.code: "UNAUTHORIZED"` |
| 13 | Error de conexión a BD | Ejecutar bajo condiciones de fallo de BD | HTTP 503, `error.code: "DATABASE_ERROR"` |

---

## ✅ Definición de Hecho

### 📦 Alcance Funcional

- [ ] Los endpoints de reporte aceptan filtros combinados.
- [ ] Reporte de reservas: filtros por fecha, estados, `usuario_id`, `vehiculo_id`.
- [ ] Reporte de pagos: filtros por fecha, `metodo_pago`, estado, `usuario_id`, rango de monto.
- [ ] Ranking de vehículos: filtros por período, `tipo_vehiculo`, `ubicacion`, `limite`.
- [ ] Los filtros son opcionales y combinables en cualquier orden.
- [ ] Los filtros inválidos retornan error `INVALID_DATA`.
- [ ] La respuesta incluye `filtros_aplicados` para confirmación.
- [ ] La respuesta JSON cumple con el contrato definido.

### 🧪 Pruebas Completadas

- [ ] Prueba de integración para filtros combinados en reservas.
- [ ] Prueba de integración para filtros combinados en pagos.
- [ ] Prueba de integración para filtros combinados en ranking.
- [ ] Prueba de integración para sin resultados.
- [ ] Prueba de integración para cualquier orden de filtros.
- [ ] Prueba de integración para rango de montos inválido.
- [ ] Prueba de integración para fechas inválidas.
- [ ] Prueba de integración para estado inválido.
- [ ] Prueba de integración para sin filtros.
- [ ] Prueba de integración para usuario no administrador.
- [ ] Las pruebas funcionales están documentadas y pasadas.

### 📄 Documentación Técnica

- [ ] Endpoints documentados en Swagger / OpenAPI.
- [ ] Se documentan todos los filtros disponibles para cada reporte.
- [ ] Se documentan los tipos de datos y valores permitidos.

### 🔐 Manejo de Errores

- [ ] HTTP 400 para filtros inválidos (`INVALID_DATA`, `INVALID_DATE_RANGE`).
- [ ] HTTP 403 para permisos insuficientes (`FORBIDDEN`).
- [ ] HTTP 401 para token no válido (`UNAUTHORIZED`).
- [ ] HTTP 503 para error de conexión a base de datos (`DATABASE_ERROR`).
- [ ] Mensajes de error claros.