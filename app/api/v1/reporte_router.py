from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List
from fastapi.responses import JSONResponse, StreamingResponse, Response
from app.service.reporte_service import ReporteService
from app.core.security import verify_admin
import io

router = APIRouter(prefix="/reportes", tags=["Reportes"])

service = ReporteService()


@router.get("/reservas", status_code=status.HTTP_200_OK)
def generar_reporte_reservas(
    fecha_inicio: Optional[str] = Query(None, description="Fecha de inicio (YYYY-MM-DD)"),
    fecha_fin: Optional[str] = Query(None, description="Fecha de fin (YYYY-MM-DD)"),
    estados: Optional[str] = Query(None, description="Estados separados por coma: pendiente,confirmada,finalizada,cancelada"),
    formato: str = Query("json", description="Formato de exportación: json, csv, xlsx, pdf"),
    admin: dict = Depends(verify_admin)
):
    """Genera un reporte de reservas. Solo administradores."""
    
    from datetime import date as date_type
    
    try:
        # Procesar parámetros
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
            "formato": formato
        }
        
        # Generar reporte
        resultado = service.generar_reporte_reservas(filtros)
        
        total = resultado["total_registros"]
        reporte_data = resultado["reporte"]
        resumen = resultado["resumen"]
        filtros_aplicados = resultado["filtros_aplicados"]
        
        if total == 0:
            return {
                "success": True,
                "statusCode": 200,
                "message": "No hay reservas con los filtros seleccionados",
                "data": {
                    "total_registros": 0,
                    "reporte": []
                }
            }
        
        # Exportar según formato
        if formato == "csv":
            csv_data = service.exportar_csv(reporte_data)
            return Response(
                content=csv_data,
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=reporte_reservas.csv"}
            )
        
        if formato == "xlsx":
            excel_data = service.exportar_excel(reporte_data)
            return Response(
                content=excel_data,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": "attachment; filename=reporte_reservas.xlsx"}
            )
        
        if formato == "pdf":
            pdf_data = service.exportar_pdf(reporte_data)
            return Response(
                content=pdf_data,
                media_type="application/pdf",
                headers={"Content-Disposition": "attachment; filename=reporte_reservas.pdf"}
            )
        
        # JSON por defecto
        return {
            "success": True,
            "statusCode": 200,
            "message": "Reporte generado exitosamente",
            "data": {
                "filtros_aplicados": filtros_aplicados,
                "total_registros": total,
                "resumen": resumen,
                "reporte": reporte_data
            }
        }
    
    except ValueError as e:
        error_msg = str(e)
        if error_msg == "INVALID_DATE_RANGE":
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "statusCode": 400,
                    "message": "Rango de fechas inválido",
                    "error": {
                        "code": "INVALID_DATE_RANGE",
                        "details": "La fecha de inicio debe ser menor o igual a la fecha de fin"
                    }
                }
            )
        if error_msg == "INVALID_STATUS":
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "statusCode": 400,
                    "message": "Estado inválido",
                    "error": {
                        "code": "INVALID_DATA",
                        "details": "Los estados permitidos son: pendiente, confirmada, en_curso, finalizada, cancelada"
                    }
                }
            )
        if error_msg == "INVALID_FORMAT":
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "statusCode": 400,
                    "message": "Formato inválido",
                    "error": {
                        "code": "INVALID_FORMAT",
                        "details": "Los formatos permitidos son: json, csv, xlsx, pdf"
                    }
                }
            )
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "statusCode": 500,
                "message": "Error interno del servidor",
                "error": {
                    "code": "INTERNAL_ERROR",
                    "details": error_msg
                }
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "success": False,
                "statusCode": 503,
                "message": "Error de conexión con la base de datos",
                "error": {
                    "code": "DATABASE_ERROR",
                    "details": "Intente nuevamente más tarde"
                }
            }
        )