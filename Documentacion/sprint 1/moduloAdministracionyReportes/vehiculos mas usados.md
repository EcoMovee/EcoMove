# [HU-023] Identificación de Vehículos Más Utilizados

## 📖 Historia de Usuario

> **Como** administrador de EcoMove,
> **quiero** identificar los vehículos con mayor cantidad de reservas en un período determinado, mostrando un ranking ordenado con métricas de uso e ingresos,
> **para** optimizar la gestión de recursos, decidir qué vehículos adquirir o retirar, y planificar el mantenimiento preventivo basado en el nivel de uso.

---

## 🔁 Flujo Esperado

1. El administrador envía una solicitud al endpoint `GET /api/v1/reportes/vehiculos-top` con el período deseado.
2. El sistema valida que el usuario autenticado tenga rol `administrador`.
3. El sistema aplica el filtro de período (día, semana, mes, rango personalizado).
4. El sistema consulta la base de datos y genera un ranking de vehículos ordenado de mayor a menor uso.
5. El ranking incluye para cada vehículo: tipo, modelo, ubicación, cantidad de reservas, horas totales de uso e ingresos generados.
6. El sistema permite visualizar la información en gráficos (datos para frontend).
7. El reporte puede exportarse en formato PDF, Excel o CSV.

---

## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y Lógica del Servicio

- [ ] Se expone un endpoint `GET /api/v1/reportes/vehiculos-top` para generar el ranking.
- [ ] Se valida que el usuario autenticado tenga rol `administrador`.
- [ ] Se permite seleccionar el período mediante `periodo`: `dia`, `semana`, `mes`, `rango`.
- [ ] Si `periodo = rango`, se requieren `fecha_inicio` y `fecha_fin`.
- [ ] El ranking se ordena de mayor a menor por `cantidad_reservas`.
- [ ] El ranking incluye para cada vehículo:

| Campo | Descripción |
|---|---|
| `id` | ID del vehículo |
| `tipo` | Tipo de vehículo |
| `modelo` | Modelo del vehículo |
| `ubicacion` | Ubicación del vehículo |
| `cantidad_reservas` | Total de reservas en el período |
| `horas_totales_uso` | Suma de horas de uso |
| `ingresos_generados` | Suma de ingresos generados |

- [ ] Se incluye un resumen con los totales del período.
- [ ] Se permite exportar en formatos: `json`, `csv`, `xlsx`, `pdf`.

---

### 2. 📆 Estructura de la Información

#### Respuesta exitosa con datos

```json
{
  "success": true,
  "statusCode": 200,
  "message": "Ranking generado exitosamente",
  "data": {
    "periodo": {
      "tipo": "mes",
      "fecha_inicio": "2025-01-01",
      "fecha_fin": "2025-01-31"
    },
    "resumen": {
      "total_vehiculos_en_ranking": 10,
      "total_reservas_periodo": 500,
      "total_horas_uso": 750,
      "total_ingresos": 2500000
    },
    "ranking": [
      {
        "posicion": 1,
        "id": 5,
        "tipo": "moto",
        "modelo": "Scooter Eléctrica X1",
        "ubicacion": "Centro comercial Unicentro",
        "cantidad_reservas": 120,
        "horas_totales_uso": 180,
        "ingresos_generados": 450000
      },
      {
        "posicion": 2,
        "id": 3,
        "tipo": "bicicleta",
        "modelo": "EcoBike Pro",
        "ubicacion": "Parque 93",
        "cantidad_reservas": 95,
        "horas_totales_uso": 142.5,
        "ingresos_generados": 285000
      }
    ]
  }
}
```

#### Sin reservas en el período

```json
{
  "success": true,
  "statusCode": 200,
  "message": "No hay reservas en el período seleccionado",
  "data": {
    "periodo": {
      "tipo": "mes",
      "fecha_inicio": "2025-01-01",
      "fecha_fin": "2025-01-31"
    },
    "resumen": {
      "total_vehiculos_en_ranking": 0,
      "total_reservas_periodo": 0,
      "total_horas_uso": 0,
      "total_ingresos": 0
    },
    "ranking": []
  }
}
```

#### Tabla de errores

| Situación | Código HTTP | Código de error |
|---|---|---|
| Usuario no administrador | `403 Forbidden` | `FORBIDDEN` |
| Token inválido o no enviado | `401 Unauthorized` | `UNAUTHORIZED` |
| Error de conexión a BD | `503 Service Unavailable` | `DATABASE_ERROR` |
| Período inválido | `400 Bad Request` | `INVALID_PERIOD` |
| Rango sin fechas o fechas inválidas | `400 Bad Request` | `INVALID_DATE_RANGE` |

---

## 🔧 Notas Técnicas

### Reglas de Negocio

> Un vehículo que presenta reportes de daño o mantenimiento recurrente debe ser retirado temporalmente de la flota hasta su revisión técnica.
> Los vehículos eléctricos solo pueden ser ofrecidos en alquiler si cuentan con un **nivel de batería suficiente**.

### Base de Datos

- Consulta principal entre tablas: `reservas`, `vehiculos`.
- Filtrar por `fecha_creacion` o `fecha_inicio_viaje` según regla de negocio.
- Agrupar por `vehiculo_id`.

### Consulta SQL para Ranking

```sql
SELECT 
  v.id,
  v.tipo,
  v.modelo,
  v.ubicacion,
  COUNT(r.id) as cantidad_reservas,
  SUM(r.duracion_horas) as horas_totales_uso,
  SUM(r.costo_estimado) as ingresos_generados
FROM reservas r
JOIN vehiculos v ON r.vehiculo_id = v.id
WHERE r.fecha_creacion BETWEEN ? AND ?
  AND r.estado IN ('finalizada', 'en_curso')
GROUP BY v.id, v.tipo, v.modelo, v.ubicacion
ORDER BY cantidad_reservas DESC
LIMIT 50;
```

### Parámetros de Consulta

| Parámetro | Tipo | Obligatorio | Ejemplo |
|---|---|---|---|
| `periodo` | String | Sí | `dia`, `semana`, `mes`, `rango` |
| `fecha_inicio` | DATE | Solo si `periodo=rango` | `2025-01-01` |
| `fecha_fin` | DATE | Solo si `periodo=rango` | `2025-01-31` |
| `formato` | String | No (default: `json`) | `csv`, `xlsx`, `pdf` |

### Cálculo de Períodos Predefinidos

| Período | Rango aplicado |
|---|---|
| `dia` | Fecha actual |
| `semana` | Últimos 7 días |
| `mes` | Últimos 30 días |
| `rango` | `fecha_inicio` y `fecha_fin` requeridos |

### Formatos de Exportación

| Formato | Librería sugerida | Content-Type |
|---|---|---|
| JSON | N/A (respuesta nativa) | `application/json` |
| CSV | `csv-writer`, `fast-csv` | `text/csv` |
| Excel | `exceljs`, `xlsx` | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` |
| PDF | `pdfkit`, `jspdf` | `application/pdf` |

### Gráficos

> La respuesta incluye datos estructurados que el frontend puede usar para gráficos de barras o circulares. La generación de imágenes de gráficos **no es responsabilidad del backend**.

### Seguridad

- El endpoint debe estar protegido con **JWT**.
- Validar rol `administrador` en el middleware.

---

## 🚀 Endpoint

| Propiedad | Valor |
|---|---|
| **Método HTTP** | `GET` |
| **Ruta** | `/api/v1/reportes/vehiculos-top` |
| **Headers** | `Authorization: Bearer <token_administrador>` |

### 📤 Ejemplos de Request

```http
GET /api/v1/reportes/vehiculos-top?periodo=mes&formato=json

GET /api/v1/reportes/vehiculos-top?periodo=rango&fecha_inicio=2025-01-01&fecha_fin=2025-01-31&formato=json
```

---

## 🧪 Casos de Prueba

### ✅ Casos Exitosos

| # | Caso | Acción | Resultado Esperado |
|---|---|---|---|
| 1 | Ranking por mes | `GET ...?periodo=mes` | HTTP 200, ranking ordenado por `cantidad_reservas DESC`, resumen con totales correctos |
| 2 | Ranking por rango personalizado | `GET ...?periodo=rango&fecha_inicio=2025-01-01&fecha_fin=2025-01-15` | HTTP 200, solo reservas entre las fechas indicadas |
| 3 | Ranking por día | `GET ...?periodo=dia` | HTTP 200, solo reservas del día actual |
| 4 | Ranking por semana | `GET ...?periodo=semana` | HTTP 200, solo reservas de los últimos 7 días |
| 5 | Cálculo de horas totales de uso | Vehículo con reservas de 2h, 1.5h y 3h | `horas_totales_uso = 6.5` |
| 6 | Cálculo de ingresos generados | Vehículo con costos 5000, 2500 y 7500 | `ingresos_generados = 15000` |
| 7 | Sin reservas en el período | Consulta con rango sin datos | HTTP 200, `total_vehiculos_en_ranking=0`, `ranking=[]`, todos los totales en 0 |
| 8 | Exportar a CSV | `GET ...?periodo=mes&formato=csv` | HTTP 200, `Content-Type: text/csv` |
| 9 | Exportar a Excel | `GET ...?periodo=mes&formato=xlsx` | HTTP 200, Content-Type Excel, archivo descargable |
| 10 | Exportar a PDF | `GET ...?periodo=mes&formato=pdf` | HTTP 200, `Content-Type: application/pdf`, archivo descargable |

### ❌ Casos de Error

| # | Caso | Acción | Resultado Esperado |
|---|---|---|---|
| 11 | Período inválido | `GET ...?periodo=anio` | HTTP 400, `error.code: "INVALID_PERIOD"` |
| 12 | Rango sin fechas | `GET ...?periodo=rango` (sin `fecha_inicio`/`fecha_fin`) | HTTP 400, `error.code: "INVALID_DATE_RANGE"` |
| 13 | Usuario no administrador | `GET` con token de rol `usuario` | HTTP 403, `error.code: "FORBIDDEN"` |
| 14 | Token no enviado | `GET` sin header `Authorization` | HTTP 401, `error.code: "UNAUTHORIZED"` |
| 15 | Error de conexión a BD | `GET` con BD no disponible | HTTP 503, `error.code: "DATABASE_ERROR"` |

---

## ✅ Definición de Hecho

### 📦 Alcance Funcional

- [ ] El endpoint `GET /api/v1/reportes/vehiculos-top` está implementado.
- [ ] Solo administradores pueden generar el ranking.
- [ ] Se permite seleccionar período: día, semana, mes, rango personalizado.
- [ ] El ranking se ordena de mayor a menor por cantidad de reservas.
- [ ] El ranking incluye tipo, modelo, ubicación, cantidad reservas, horas uso e ingresos.
- [ ] Se incluye resumen con totales del período.
- [ ] Se permite exportar en JSON, CSV, Excel y PDF.
- [ ] La respuesta JSON cumple con el contrato definido.

### 🧪 Pruebas Completadas

- [ ] Prueba de integración para ranking por mes.
- [ ] Prueba de integración para ranking por rango.
- [ ] Prueba de integración para ranking por día.
- [ ] Prueba de integración para ranking por semana.
- [ ] Prueba de integración para cálculo de horas e ingresos.
- [ ] Prueba de integración para sin reservas.
- [ ] Prueba de integración para exportación CSV, Excel y PDF.
- [ ] Prueba de integración para período inválido.
- [ ] Prueba de integración para usuario no administrador.
- [ ] Las pruebas funcionales están documentadas y pasadas.

### 📄 Documentación Técnica

- [ ] Endpoint documentado en Swagger / OpenAPI.
- [ ] Se describen los parámetros de consulta.
- [ ] Se documentan los formatos de exportación.

### 🔐 Manejo de Errores

- [ ] HTTP 400 para período inválido (`INVALID_PERIOD`, `INVALID_DATE_RANGE`).
- [ ] HTTP 403 para permisos insuficientes (`FORBIDDEN`).
- [ ] HTTP 401 para token no válido (`UNAUTHORIZED`).
- [ ] HTTP 503 para error de conexión a base de datos (`DATABASE_ERROR`).
- [ ] Mensajes de error claros.