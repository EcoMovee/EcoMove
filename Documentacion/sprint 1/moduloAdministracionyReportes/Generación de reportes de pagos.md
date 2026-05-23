# [HU-022] Generación de Reportes de Pagos

## 📖 Historia de Usuario

> **Como** administrador de EcoMove,
> **quiero** generar reportes de pagos realizados, incluyendo información detallada y totales calculados,
> **para** controlar los ingresos del sistema, realizar conciliaciones financieras y detectar posibles anomalías.

---

## 🔁 Flujo Esperado

1. El administrador envía una solicitud al endpoint `GET /api/v1/reportes/pagos` con los filtros deseados.
2. El sistema valida que el usuario autenticado tenga rol `administrador`.
3. El sistema aplica los filtros enviados: rango de fechas, método de pago y estado de la transacción.
4. El sistema consulta la base de datos y genera el reporte.
5. El reporte incluye: fecha y hora del pago, monto, método de pago, estado, reserva asociada y usuario.
6. El sistema calcula automáticamente totales: suma de montos aprobados, cantidad de transacciones, etc.
7. El reporte puede exportarse en formato PDF, Excel o CSV.

---

## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y Lógica del Servicio

- [ ] Se expone un endpoint `GET /api/v1/reportes/pagos` para generar reportes.
- [ ] Se valida que el usuario autenticado tenga rol `administrador`.
- [ ] Se permite filtrar por rango de fechas: `fecha_inicio` y `fecha_fin`.
- [ ] Se permite filtrar por `metodo_pago`: `tarjeta_credito`, `tarjeta_debito`, `monedero_electronico`.
- [ ] Se permite filtrar por `estado`: `aprobado`, `rechazado`, `reembolsado`.
- [ ] Los filtros son opcionales (si no se envían, se incluyen todos los pagos).
- [ ] El reporte incluye los siguientes campos:

| Campo | Descripción |
|---|---|
| `id` | ID del pago |
| `fecha_pago` | Fecha y hora del pago |
| `monto` | Monto de la transacción |
| `metodo_pago` | Método de pago utilizado |
| `estado` | Estado de la transacción |
| `reserva_id` | ID de la reserva asociada |
| `usuario_nombre` | Nombre del usuario |
| `usuario_email` | Correo electrónico del usuario |
| `transaccion_id` | ID externo de la transacción |
| `motivo_rechazo` | Motivo del rechazo (si aplica) |

- [ ] Se calculan totales automáticos:

| Campo | Descripción |
|---|---|
| `total_transacciones` | Cantidad total de pagos |
| `total_aprobados` | Suma de montos con estado `aprobado` |
| `total_rechazados` | Suma de montos con estado `rechazado` |
| `total_reembolsados` | Suma de montos con estado `reembolsado` |

- [ ] Se permite exportar en formatos: `json`, `csv`, `xlsx`, `pdf`.

---

### 2. 📆 Estructura de la Información

#### Respuesta exitosa con datos

```json
{
  "success": true,
  "statusCode": 200,
  "message": "Reporte generado exitosamente",
  "data": {
    "filtros_aplicados": {
      "fecha_inicio": "2025-01-01",
      "fecha_fin": "2025-01-31",
      "metodo_pago": "tarjeta_credito",
      "estado": "aprobado"
    },
    "total_registros": 120,
    "totales": {
      "total_transacciones": 120,
      "total_aprobados": 600000,
      "total_rechazados": 0,
      "total_reembolsados": 0
    },
    "reporte": [
      {
        "id": 5001,
        "fecha_pago": "2025-01-15T10:35:00Z",
        "monto": 5000,
        "metodo_pago": "tarjeta_credito",
        "estado": "aprobado",
        "reserva_id": 1001,
        "usuario_nombre": "Juan Perez",
        "usuario_email": "juan@example.com",
        "transaccion_id": "tx_123456789",
        "motivo_rechazo": null
      }
    ]
  }
}
```

#### Sin datos con los filtros aplicados

```json
{
  "success": true,
  "statusCode": 200,
  "message": "No hay pagos con los filtros seleccionados",
  "data": {
    "total_registros": 0,
    "totales": {
      "total_transacciones": 0,
      "total_aprobados": 0,
      "total_rechazados": 0,
      "total_reembolsados": 0
    },
    "reporte": []
  }
}
```

#### Tabla de errores

| Situación | Código HTTP | Código de error |
|---|---|---|
| Usuario no administrador | `403 Forbidden` | `FORBIDDEN` |
| Token inválido o no enviado | `401 Unauthorized` | `UNAUTHORIZED` |
| Error de conexión a BD | `503 Service Unavailable` | `DATABASE_ERROR` |
| Rango de fechas inválido | `400 Bad Request` | `INVALID_DATE_RANGE` |
| Método de pago o estado inválido | `400 Bad Request` | `INVALID_DATA` |
| Formato de exportación inválido | `400 Bad Request` | `INVALID_FORMAT` |

---

## 🔧 Notas Técnicas

### Reglas de Negocio

> Los pagos no son reembolsables una vez que el usuario ha iniciado el viaje.
> El sistema aplica una tarifa mínima por viaje equivalente a **60 minutos** de uso.

### Base de Datos

- Consulta principal entre tablas: `pagos`, `usuarios`, `reservas`.
- Usar `LEFT JOIN` para no perder registros.
- Índices en `fecha_pago`, `estado` y `metodo_pago` para optimizar consultas.

### Cálculo de Totales

```sql
SELECT 
  COUNT(*) as total_transacciones,
  SUM(CASE WHEN estado = 'aprobado' THEN monto ELSE 0 END) as total_aprobados,
  SUM(CASE WHEN estado = 'rechazado' THEN monto ELSE 0 END) as total_rechazados,
  SUM(CASE WHEN estado = 'reembolsado' THEN monto ELSE 0 END) as total_reembolsados
FROM pagos
WHERE fecha_pago BETWEEN ? AND ?
```

### Formatos de Exportación

| Formato | Librería sugerida | Content-Type |
|---|---|---|
| JSON | N/A (respuesta nativa) | `application/json` |
| CSV | `csv-writer`, `fast-csv` | `text/csv` |
| Excel | `exceljs`, `xlsx` | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` |
| PDF | `pdfkit`, `jspdf` | `application/pdf` |

### Parámetros de Consulta

| Parámetro | Tipo | Obligatorio | Ejemplo |
|---|---|---|---|
| `fecha_inicio` | DATE | No | `2025-01-01` |
| `fecha_fin` | DATE | No | `2025-01-31` |
| `metodo_pago` | String | No | `tarjeta_credito` |
| `estado` | String | No | `aprobado` |
| `formato` | String | No (default: `json`) | `csv`, `xlsx`, `pdf` |

### Seguridad

- El endpoint debe estar protegido con **JWT**.
- Validar rol `administrador` en el middleware.

---

## 🚀 Endpoint

| Propiedad | Valor |
|---|---|
| **Método HTTP** | `GET` |
| **Ruta** | `/api/v1/reportes/pagos` |
| **Headers** | `Authorization: Bearer <token_administrador>` |

### 📤 Ejemplo de Request

```http
GET /api/v1/reportes/pagos?fecha_inicio=2025-01-01&fecha_fin=2025-01-31&estado=aprobado&formato=json
```

---

## 🧪 Casos de Prueba

### ✅ Casos Exitosos

| # | Caso | Acción | Resultado Esperado |
|---|---|---|---|
| 1 | Reporte con filtros de fecha y estado | `GET ...?fecha_inicio=2025-01-01&fecha_fin=2025-01-31&estado=aprobado` | HTTP 200, `total_registros` correcto, solo pagos del período y estado solicitado |
| 2 | Reporte con filtro de método de pago | `GET ...?metodo_pago=tarjeta_credito` | HTTP 200, solo pagos con `metodo_pago = "tarjeta_credito"` |
| 3 | Cálculo de totales correcto | Reporte con 100 aprobados (500000), 10 rechazados (5000), 5 reembolsados (2500) | `total_transacciones=115`, `total_aprobados=500000`, `total_rechazados=5000`, `total_reembolsados=2500` |
| 4 | Reporte sin filtros | `GET /api/v1/reportes/pagos` | HTTP 200, incluye todos los pagos del sistema |
| 5 | Exportar a CSV | `GET ...?formato=csv` | HTTP 200, `Content-Type: text/csv` |
| 6 | Exportar a Excel | `GET ...?formato=xlsx` | HTTP 200, Content-Type Excel, archivo descargable |
| 7 | Exportar a PDF | `GET ...?formato=pdf` | HTTP 200, `Content-Type: application/pdf`, archivo descargable |
| 8 | Sin datos con filtros aplicados | Consulta con fechas sin datos | HTTP 200, `total_registros=0`, todos los totales en 0, `reporte=[]` |

### ❌ Casos de Error

| # | Caso | Acción | Resultado Esperado |
|---|---|---|---|
| 9 | Rango de fechas inválido | `GET ...?fecha_inicio=2025-01-31&fecha_fin=2025-01-01` | HTTP 400, `error.code: "INVALID_DATE_RANGE"` |
| 10 | Usuario no administrador | `GET` con token de rol `usuario` | HTTP 403, `error.code: "FORBIDDEN"` |
| 11 | Método de pago inválido | `GET ...?metodo_pago=efectivo` | HTTP 400, `error.code: "INVALID_DATA"` |
| 12 | Estado inválido | `GET ...?estado=pendiente` | HTTP 400, `error.code: "INVALID_DATA"` |
| 13 | Token no enviado | `GET` sin header `Authorization` | HTTP 401, `error.code: "UNAUTHORIZED"` |
| 14 | Error de conexión a BD | `GET` con BD no disponible | HTTP 503, `error.code: "DATABASE_ERROR"` |

---

## ✅ Definición de Hecho

### 📦 Alcance Funcional

- [ ] El endpoint `GET /api/v1/reportes/pagos` está implementado.
- [ ] Solo administradores pueden generar reportes.
- [ ] Se permite filtrar por rango de fechas.
- [ ] Se permite filtrar por método de pago.
- [ ] Se permite filtrar por estado de transacción.
- [ ] El reporte incluye todos los campos requeridos.
- [ ] Se calculan totales automáticos.
- [ ] Se permite exportar en JSON, CSV, Excel y PDF.
- [ ] La respuesta JSON cumple con el contrato definido.

### 🧪 Pruebas Completadas

- [ ] Prueba de integración para reporte con filtros.
- [ ] Prueba de integración para reporte sin filtros.
- [ ] Prueba de integración para cálculo de totales.
- [ ] Prueba de integración para filtro por método de pago.
- [ ] Prueba de integración para exportación CSV.
- [ ] Prueba de integración para exportación Excel.
- [ ] Prueba de integración para exportación PDF.
- [ ] Prueba de integración para sin datos.
- [ ] Prueba de integración para fecha inválida.
- [ ] Prueba de integración para usuario no administrador.
- [ ] Las pruebas funcionales están documentadas y pasadas.

### 📄 Documentación Técnica

- [ ] Endpoint documentado en Swagger / OpenAPI.
- [ ] Se describen los parámetros de consulta.
- [ ] Se documentan los formatos de exportación.

### 🔐 Manejo de Errores

- [ ] HTTP 400 para filtros inválidos (`INVALID_DATE_RANGE`, `INVALID_DATA`, `INVALID_FORMAT`).
- [ ] HTTP 403 para permisos insuficientes (`FORBIDDEN`).
- [ ] HTTP 401 para token no válido (`UNAUTHORIZED`).
- [ ] HTTP 503 para error de conexión a base de datos (`DATABASE_ERROR`).
- [ ] Mensajes de error claros.