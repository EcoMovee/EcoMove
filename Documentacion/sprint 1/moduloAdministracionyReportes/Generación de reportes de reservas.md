# [HU-021] Generación de Reportes de Reservas

## 📖 Historia de Usuario

> **Como** administrador de EcoMove,
> **quiero** generar reportes de reservas aplicando filtros por fecha y estado,
> **para** analizar el uso del sistema, identificar patrones de demanda y tomar decisiones basadas en datos.

---

## 🔁 Flujo Esperado

1. El administrador envía una solicitud al endpoint `GET /api/v1/reportes/reservas` con los filtros deseados.
2. El sistema valida que el usuario autenticado tenga rol `administrador`.
3. El sistema aplica los filtros enviados: rango de fechas y estado de reserva.
4. El sistema consulta la base de datos y genera el reporte.
5. El reporte incluye: ID de reserva, usuario, vehículo, fechas, duración, costo y estado.
6. El reporte puede exportarse en formato PDF, Excel o CSV.
7. El reporte puede visualizarse en pantalla antes de exportar.

---

## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y Lógica del Servicio

- [ ] Se expone un endpoint `GET /api/v1/reportes/reservas` para generar reportes.
- [ ] Se valida que el usuario autenticado tenga rol `administrador`.
- [ ] Se permite filtrar por rango de fechas: `fecha_inicio` y `fecha_fin`.
- [ ] Se permite filtrar por estado de reserva: `pendiente`, `confirmada`, `en_curso`, `finalizada`, `cancelada`.
- [ ] Los filtros son opcionales (si no se envían, se incluyen todas las reservas).
- [ ] El reporte incluye los siguientes campos:

| Campo | Descripción |
|---|---|
| `id` | ID de reserva |
| `usuario_nombre` | Nombre del usuario |
| `usuario_email` | Correo electrónico del usuario |
| `vehiculo_tipo` | Tipo de vehículo |
| `vehiculo_modelo` | Modelo del vehículo |
| `fecha` | Fecha de la reserva |
| `hora_inicio` | Hora de inicio |
| `hora_fin` | Hora de fin |
| `duracion_horas` | Duración en horas |
| `costo_estimado` | Costo estimado |
| `estado` | Estado de la reserva |
| `fecha_creacion` | Fecha de creación del registro |

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
      "estados": ["confirmada", "finalizada"]
    },
    "total_registros": 150,
    "resumen": {
      "total_reservas": 150,
      "total_ingresos": 750000,
      "duracion_promedio_horas": 1.5
    },
    "reporte": [
      {
        "id": 1001,
        "usuario_nombre": "Juan Perez",
        "usuario_email": "juan@example.com",
        "vehiculo_tipo": "moto",
        "vehiculo_modelo": "Scooter Eléctrica X1",
        "fecha": "2025-01-15",
        "hora_inicio": "10:00",
        "hora_fin": "12:00",
        "duracion_horas": 2,
        "costo_estimado": 5000,
        "estado": "finalizada",
        "fecha_creacion": "2025-01-10T08:00:00Z"
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
  "message": "No hay reservas con los filtros seleccionados",
  "data": {
    "total_registros": 0,
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
| Formato de exportación inválido | `400 Bad Request` | `INVALID_FORMAT` |

---

## 🔧 Notas Técnicas

### Reglas de Negocio

> Todo cambio en las tarifas de alquiler debe ser aprobado por un administrador con nivel de privilegio superior y quedar registrado en el historial del sistema.

### Base de Datos

- Consulta principal entre tablas: `reservas`, `usuarios`, `vehiculos`.
- Usar `LEFT JOIN` para no perder registros.
- Índices en `fecha_creacion`, `estado` y `vehiculo_id` para optimizar consultas.

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
| `estados` | Array | No | `confirmada,finalizada` |
| `formato` | String | No (default: `json`) | `csv`, `xlsx`, `pdf` |

### Resumen Estadístico

- `total_reservas`: cantidad total de reservas.
- `total_ingresos`: suma de `costo_estimado` (solo reservas `confirmadas` / `finalizadas`).
- `duracion_promedio_horas`: promedio de `duracion_horas`.

### Seguridad

- El endpoint debe estar protegido con **JWT**.
- Validar rol `administrador` en el middleware.

---

## 🚀 Endpoint

| Propiedad | Valor |
|---|---|
| **Método HTTP** | `GET` |
| **Ruta** | `/api/v1/reportes/reservas` |
| **Headers** | `Authorization: Bearer <token_administrador>` |

### 📤 Ejemplo de Request

```http
GET /api/v1/reportes/reservas?fecha_inicio=2025-01-01&fecha_fin=2025-01-31&estados=confirmada,finalizada&formato=json
```

---

## 🧪 Casos de Prueba

### ✅ Casos Exitosos

| # | Caso | Acción | Resultado Esperado |
|---|---|---|---|
| 1 | Reporte con filtros de fecha y estado | `GET ...?fecha_inicio=2025-01-01&fecha_fin=2025-01-31&estados=finalizada` | HTTP 200, `total_registros` correcto, solo reservas del período y estado solicitado |
| 2 | Reporte sin filtros | `GET /api/v1/reportes/reservas` | HTTP 200, incluye todas las reservas del sistema |
| 3 | Resumen estadístico correcto | Generar reporte con 10 reservas finalizadas, costo total 50000, duración 1.5h | `total_reservas=10`, `total_ingresos=50000`, `duracion_promedio_horas=1.5` |
| 4 | Exportar a CSV | `GET ...?formato=csv` | HTTP 200, `Content-Type: text/csv` |
| 5 | Exportar a Excel | `GET ...?formato=xlsx` | HTTP 200, Content-Type Excel, archivo descargable |
| 6 | Exportar a PDF | `GET ...?formato=pdf` | HTTP 200, `Content-Type: application/pdf`, archivo descargable |
| 7 | Sin datos con filtros aplicados | Consulta con fechas sin datos | HTTP 200, `total_registros=0`, `reporte=[]` |

### ❌ Casos de Error

| # | Caso | Acción | Resultado Esperado |
|---|---|---|---|
| 8 | Rango de fechas inválido | `GET ...?fecha_inicio=2025-01-31&fecha_fin=2025-01-01` | HTTP 400, `error.code: "INVALID_DATE_RANGE"` |
| 9 | Usuario no administrador | `GET` con token de rol `usuario` | HTTP 403, `error.code: "FORBIDDEN"` |
| 10 | Token no enviado | `GET` sin header `Authorization` | HTTP 401, `error.code: "UNAUTHORIZED"` |
| 11 | Formato de exportación inválido | `GET ...?formato=xml` | HTTP 400, `error.code: "INVALID_FORMAT"` |
| 12 | Error de conexión a BD | `GET` con BD no disponible | HTTP 503, `error.code: "DATABASE_ERROR"` |

---

## ✅ Definición de Hecho

### 📦 Alcance Funcional

- [ ] El endpoint `GET /api/v1/reportes/reservas` está implementado.
- [ ] Solo administradores pueden generar reportes.
- [ ] Se permite filtrar por rango de fechas.
- [ ] Se permite filtrar por estado de reserva.
- [ ] El reporte incluye todos los campos requeridos.
- [ ] Se incluye resumen estadístico (total, ingresos, duración promedio).
- [ ] Se permite exportar en JSON, CSV, Excel y PDF.
- [ ] La respuesta JSON cumple con el contrato definido.

### 🧪 Pruebas Completadas

- [ ] Prueba de integración para reporte con filtros.
- [ ] Prueba de integración para reporte sin filtros.
- [ ] Prueba de integración para resumen estadístico.
- [ ] Prueba de integración para exportación CSV.
- [ ] Prueba de integración para exportación Excel.
- [ ] Prueba de integración para exportación PDF.
- [ ] Prueba de integración para sin datos.
- [ ] Prueba de integración para rango de fechas inválido.
- [ ] Prueba de integración para usuario no administrador.
- [ ] Las pruebas funcionales están documentadas y pasadas.

### 📄 Documentación Técnica

- [ ] Endpoint documentado en Swagger / OpenAPI.
- [ ] Se describen los parámetros de consulta.
- [ ] Se documentan los formatos de exportación.

### 🔐 Manejo de Errores

- [ ] HTTP 400 para filtros inválidos (`INVALID_DATE_RANGE`, `INVALID_FORMAT`).
- [ ] HTTP 403 para permisos insuficientes (`FORBIDDEN`).
- [ ] HTTP 401 para token no válido (`UNAUTHORIZED`).
- [ ] HTTP 503 para error de conexión a base de datos (`DATABASE_ERROR`).
- [ ] Mensajes de error claros.