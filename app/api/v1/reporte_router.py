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
        

@router.get("/pagos", status_code=status.HTTP_200_OK)
def generar_reporte_pagos(
    fecha_inicio: Optional[str] = Query(None, description="Fecha de inicio (YYYY-MM-DD)"),
    fecha_fin: Optional[str] = Query(None, description="Fecha de fin (YYYY-MM-DD)"),
    metodo_pago: Optional[str] = Query(None, description="Método de pago: tarjeta_credito, tarjeta_debito, monedero_electronico"),
    estado: Optional[str] = Query(None, description="Estado: aprobado, rechazado, reembolsado"),
    formato: str = Query("json", description="Formato de exportación: json, csv, xlsx, pdf"),
    admin: dict = Depends(verify_admin)
):
    """Genera un reporte de pagos. Solo administradores."""
    
    from datetime import date as date_type
    
    try:
        # Procesar parámetros
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
            "formato": formato
        }
        
        # Generar reporte
        resultado = service.generar_reporte_pagos(filtros)
        
        total = resultado["total_registros"]
        reporte_data = resultado["reporte"]
        totales = resultado["totales"]
        filtros_aplicados = resultado["filtros_aplicados"]
        
        if total == 0:
            return {
                "success": True,
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
        
        # Exportar según formato
        if formato == "csv":
            csv_data = service.exportar_csv(reporte_data)
            return Response(
                content=csv_data,
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=reporte_pagos.csv"}
            )
        
        if formato == "xlsx":
            excel_data = service.exportar_excel(reporte_data)
            return Response(
                content=excel_data,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": "attachment; filename=reporte_pagos.xlsx"}
            )
        
        if formato == "pdf":
            pdf_data = service.exportar_pdf(reporte_data)
            return Response(
                content=pdf_data,
                media_type="application/pdf",
                headers={"Content-Disposition": "attachment; filename=reporte_pagos.pdf"}
            )
        
        # JSON por defecto
        return {
            "success": True,
            "statusCode": 200,
            "message": "Reporte generado exitosamente",
            "data": {
                "filtros_aplicados": filtros_aplicados,
                "total_registros": total,
                "totales": totales,
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
                    "error": {"code": "INVALID_DATE_RANGE", "details": "La fecha de inicio debe ser menor o igual a la fecha de fin"}
                }
            )
        if error_msg == "INVALID_DATA":
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "statusCode": 400,
                    "message": "Parámetro inválido",
                    "error": {"code": "INVALID_DATA", "details": "Método de pago o estado inválido"}
                }
            )
        if error_msg == "INVALID_FORMAT":
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "statusCode": 400,
                    "message": "Formato inválido",
                    "error": {"code": "INVALID_FORMAT", "details": "Los formatos permitidos son: json, csv, xlsx, pdf"}
                }
            )
        raise HTTPException(status_code=500, detail={"message": error_msg})
    
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "success": False,
                "statusCode": 503,
                "message": "Error de conexión con la base de datos",
                "error": {"code": "DATABASE_ERROR", "details": "Intente nuevamente más tarde"}
            }
        )
        
        
@router.get("/vehiculos-top", status_code=status.HTTP_200_OK)
def ranking_vehiculos_mas_usados(
    periodo: str = Query(..., description="Período: dia, semana, mes, rango"),
    fecha_inicio: Optional[str] = Query(None, description="Fecha inicio (YYYY-MM-DD) - requerido si periodo=rango"),
    fecha_fin: Optional[str] = Query(None, description="Fecha fin (YYYY-MM-DD) - requerido si periodo=rango"),
    formato: str = Query("json", description="Formato: json, csv, xlsx, pdf"),
    admin: dict = Depends(verify_admin)
):
    """Genera ranking de vehículos más usados. Solo administradores."""
    
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
            "formato": formato
        }
        
        resultado = service.generar_ranking_vehiculos(filtros)
        
        ranking = resultado["ranking"]
        
        if len(ranking) == 0:
            return {
                "success": True,
                "statusCode": 200,
                "message": "No hay reservas en el período seleccionado",
                "data": resultado
            }
        
        # Exportar según formato
        if formato == "csv":
            csv_data = service.exportar_csv(ranking)
            return Response(
                content=csv_data,
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=ranking_vehiculos.csv"}
            )
        
        if formato == "xlsx":
            excel_data = service.exportar_excel(ranking)
            return Response(
                content=excel_data,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": "attachment; filename=ranking_vehiculos.xlsx"}
            )
        
        if formato == "pdf":
            pdf_data = service.exportar_pdf(ranking)
            return Response(
                content=pdf_data,
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
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "statusCode": 400,
                    "message": "Período inválido",
                    "error": {
                        "code": "INVALID_PERIOD",
                        "details": "El período debe ser: dia, semana, mes o rango"
                    }
                }
            )
        if error_msg == "INVALID_DATE_RANGE":
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "statusCode": 400,
                    "message": "Rango de fechas inválido",
                    "error": {
                        "code": "INVALID_DATE_RANGE",
                        "details": "Las fechas son requeridas para período rango o la fecha de inicio es mayor a la fecha de fin"
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
        raise HTTPException(status_code=500, detail={"message": error_msg})
    
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