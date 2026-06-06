from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from fastapi.responses import Response
from app.service.reporte_service import ReporteService
from app.core.security import verify_admin

router = APIRouter(prefix="/reportes", tags=["Reportes"])

service = ReporteService()


# ==================== REPORTE DE RESERVAS ====================

@router.get("/reservas", status_code=status.HTTP_200_OK)
def generar_reporte_reservas(
    fecha_inicio: Optional[str] = Query(None, description="Fecha de inicio (YYYY-MM-DD)"),
    fecha_fin: Optional[str] = Query(None, description="Fecha de fin (YYYY-MM-DD)"),
    estados: Optional[str] = Query(None, description="Estados separados por coma"),
    usuario_id: Optional[int] = Query(None, description="ID del usuario"),
    vehiculo_id: Optional[int] = Query(None, description="ID del vehículo"),
    formato: str = Query("json", description="Formato: json, csv, xlsx, pdf"),
    admin: dict = Depends(verify_admin)
):
    from datetime import date as date_type
    
    try:
        fecha_inicio_obj = None
        fecha_fin_obj = None
        
        if fecha_inicio:
            fecha_inicio_obj = date_type.fromisoformat(fecha_inicio)
        if fecha_fin:
            fecha_fin_obj = date_type.fromisoformat(fecha_fin)
        
        estados_list = None
        if estados:
            estados_list = [e.strip() for e in estados.split(",")]
        
        filtros = {
            "fecha_inicio": fecha_inicio_obj,
            "fecha_fin": fecha_fin_obj,
            "estados": estados_list,
            "usuario_id": usuario_id,
            "vehiculo_id": vehiculo_id,
            "formato": formato
        }
        
        resultado = service.generar_reporte_reservas(filtros)
        total = resultado["total_registros"]
        reporte_data = resultado["reporte"]
        
        if total == 0:
            return {
                "success": True,
                "statusCode": 200,
                "message": "No hay reservas con los filtros seleccionados",
                "data": {"total_registros": 0, "reporte": []}
            }
        
        if formato == "csv":
            return Response(
                content=service.exportar_csv(reporte_data),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=reporte_reservas.csv"}
            )
        if formato == "xlsx":
            return Response(
                content=service.exportar_excel(reporte_data),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": "attachment; filename=reporte_reservas.xlsx"}
            )
        if formato == "pdf":
            return Response(
                content=service.exportar_pdf(reporte_data),
                media_type="application/pdf",
                headers={"Content-Disposition": "attachment; filename=reporte_reservas.pdf"}
            )
        
        return {
            "success": True,
            "statusCode": 200,
            "message": "Reporte generado exitosamente",
            "data": resultado
        }
    
    except ValueError as e:
        error_msg = str(e)
        if error_msg == "INVALID_DATE_RANGE":
            raise HTTPException(status_code=400, detail={"success": False, "statusCode": 400, "message": "Rango de fechas inválido", "error": {"code": "INVALID_DATE_RANGE"}})
        if error_msg == "INVALID_STATUS":
            raise HTTPException(status_code=400, detail={"success": False, "statusCode": 400, "message": "Estado inválido", "error": {"code": "INVALID_DATA"}})
        if error_msg == "INVALID_FORMAT":
            raise HTTPException(status_code=400, detail={"success": False, "statusCode": 400, "message": "Formato inválido", "error": {"code": "INVALID_FORMAT"}})
        raise HTTPException(status_code=500, detail={"success": False, "statusCode": 500, "message": error_msg})
    except Exception:
        raise HTTPException(status_code=503, detail={"success": False, "statusCode": 503, "message": "Error de conexión con la base de datos", "error": {"code": "DATABASE_ERROR"}})


# ==================== REPORTE DE PAGOS ====================

@router.get("/pagos", status_code=status.HTTP_200_OK)
def generar_reporte_pagos(
    fecha_inicio: Optional[str] = Query(None, description="Fecha de inicio (YYYY-MM-DD)"),
    fecha_fin: Optional[str] = Query(None, description="Fecha de fin (YYYY-MM-DD)"),
    metodo_pago: Optional[str] = Query(None, description="Método de pago"),
    estado: Optional[str] = Query(None, description="Estado: aprobado, rechazado, reembolsado"),
    usuario_id: Optional[int] = Query(None, description="ID del usuario"),
    rango_monto_min: Optional[float] = Query(None, ge=0, description="Monto mínimo"),
    rango_monto_max: Optional[float] = Query(None, ge=0, description="Monto máximo"),
    formato: str = Query("json", description="Formato: json, csv, xlsx, pdf"),
    admin: dict = Depends(verify_admin)
):
    from datetime import date as date_type
    
    try:
        fecha_inicio_obj = None
        fecha_fin_obj = None
        
        if fecha_inicio:
            fecha_inicio_obj = date_type.fromisoformat(fecha_inicio)
        if fecha_fin:
            fecha_fin_obj = date_type.fromisoformat(fecha_fin)
        
        filtros = {
            "fecha_inicio": fecha_inicio_obj,
            "fecha_fin": fecha_fin_obj,
            "metodo_pago": metodo_pago,
            "estado": estado,
            "usuario_id": usuario_id,
            "rango_monto_min": rango_monto_min,
            "rango_monto_max": rango_monto_max,
            "formato": formato
        }
        
        resultado = service.generar_reporte_pagos(filtros)
        total = resultado["total_registros"]
        reporte_data = resultado["reporte"]
        
        if total == 0:
            return {
                "success": True,
                "statusCode": 200,
                "message": "No hay pagos con los filtros seleccionados",
                "data": {"total_registros": 0, "totales": {"total_transacciones": 0, "total_aprobados": 0, "total_rechazados": 0, "total_reembolsados": 0}, "reporte": []}
            }
        
        if formato == "csv":
            return Response(
                content=service.exportar_csv(reporte_data),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=reporte_pagos.csv"}
            )
        if formato == "xlsx":
            return Response(
                content=service.exportar_excel(reporte_data),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": "attachment; filename=reporte_pagos.xlsx"}
            )
        if formato == "pdf":
            return Response(
                content=service.exportar_pdf(reporte_data),
                media_type="application/pdf",
                headers={"Content-Disposition": "attachment; filename=reporte_pagos.pdf"}
            )
        
        return {
            "success": True,
            "statusCode": 200,
            "message": "Reporte generado exitosamente",
            "data": resultado
        }
    
    except ValueError as e:
        error_msg = str(e)
        if error_msg == "INVALID_DATE_RANGE":
            raise HTTPException(status_code=400, detail={"success": False, "statusCode": 400, "message": "Rango de fechas inválido", "error": {"code": "INVALID_DATE_RANGE"}})
        if error_msg == "INVALID_DATA":
            raise HTTPException(status_code=400, detail={"success": False, "statusCode": 400, "message": "Parámetro inválido", "error": {"code": "INVALID_DATA"}})
        if error_msg == "INVALID_FORMAT":
            raise HTTPException(status_code=400, detail={"success": False, "statusCode": 400, "message": "Formato inválido", "error": {"code": "INVALID_FORMAT"}})
        raise HTTPException(status_code=500, detail={"success": False, "statusCode": 500, "message": error_msg})
    except Exception:
        raise HTTPException(status_code=503, detail={"success": False, "statusCode": 503, "message": "Error de conexión con la base de datos", "error": {"code": "DATABASE_ERROR"}})


# ==================== RANKING DE VEHÍCULOS ====================

@router.get("/vehiculos-top", status_code=status.HTTP_200_OK)
def ranking_vehiculos_mas_usados(
    periodo: str = Query(..., description="Período: dia, semana, mes, rango"),
    fecha_inicio: Optional[str] = Query(None, description="Fecha inicio (requerido si periodo=rango)"),
    fecha_fin: Optional[str] = Query(None, description="Fecha fin (requerido si periodo=rango)"),
    tipo_vehiculo: Optional[str] = Query(None, description="Tipo: carro, moto, bicicleta"),
    ubicacion: Optional[str] = Query(None, description="Filtro por ubicación"),
    limite: int = Query(10, ge=1, le=100, description="Límite de resultados"),
    formato: str = Query("json", description="Formato: json, csv, xlsx, pdf"),
    admin: dict = Depends(verify_admin)
):
    from datetime import date as date_type
    
    try:
        fecha_inicio_obj = None
        fecha_fin_obj = None
        
        if fecha_inicio:
            fecha_inicio_obj = date_type.fromisoformat(fecha_inicio)
        if fecha_fin:
            fecha_fin_obj = date_type.fromisoformat(fecha_fin)
        
        filtros = {
            "periodo": periodo,
            "fecha_inicio": fecha_inicio_obj,
            "fecha_fin": fecha_fin_obj,
            "tipo_vehiculo": tipo_vehiculo,
            "ubicacion": ubicacion,
            "limite": limite,
            "formato": formato
        }
        
        resultado = service.generar_ranking_vehiculos(filtros)
        ranking = resultado.get("ranking", [])
        
        if len(ranking) == 0:
            return {
                "success": True,
                "statusCode": 200,
                "message": "No hay reservas en el período seleccionado",
                "data": resultado
            }
        
        if formato == "csv":
            return Response(
                content=service.exportar_csv(ranking),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=ranking_vehiculos.csv"}
            )
        if formato == "xlsx":
            return Response(
                content=service.exportar_excel(ranking),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": "attachment; filename=ranking_vehiculos.xlsx"}
            )
        if formato == "pdf":
            return Response(
                content=service.exportar_pdf(ranking),
                media_type="application/pdf",
                headers={"Content-Disposition": "attachment; filename=ranking_vehiculos.pdf"}
            )
        
        return {
            "success": True,
            "statusCode": 200,
            "message": "Ranking generado exitosamente",
            "data": resultado
        }
    
    except ValueError as e:
        error_msg = str(e)
        if error_msg == "INVALID_PERIOD":
            raise HTTPException(status_code=400, detail={"success": False, "statusCode": 400, "message": "Período inválido", "error": {"code": "INVALID_PERIOD"}})
        if error_msg == "INVALID_DATE_RANGE":
            raise HTTPException(status_code=400, detail={"success": False, "statusCode": 400, "message": "Rango de fechas inválido", "error": {"code": "INVALID_DATE_RANGE"}})
        if error_msg == "INVALID_DATA":
            raise HTTPException(status_code=400, detail={"success": False, "statusCode": 400, "message": "Parámetro inválido", "error": {"code": "INVALID_DATA"}})
        if error_msg == "INVALID_FORMAT":
            raise HTTPException(status_code=400, detail={"success": False, "statusCode": 400, "message": "Formato inválido", "error": {"code": "INVALID_FORMAT"}})
        raise HTTPException(status_code=500, detail={"success": False, "statusCode": 500, "message": error_msg})
    except Exception:
        raise HTTPException(status_code=503, detail={"success": False, "statusCode": 503, "message": "Error de conexión con la base de datos", "error": {"code": "DATABASE_ERROR"}})