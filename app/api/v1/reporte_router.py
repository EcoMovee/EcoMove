from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
import io
import csv
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from fastapi.responses import Response
from service.reporte_service import ReporteService
from core.security import verify_admin

router = APIRouter(prefix="/reportes", tags=["Reportes"])

service = ReporteService()

# ==================== FUNCIONES DE EXPORTACIÓN ====================

def exportar_csv(data: list) -> io.BytesIO:
    output = io.StringIO()
    if data:
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    return io.BytesIO(output.getvalue().encode('utf-8-sig'))

def exportar_excel(data: list) -> io.BytesIO:
    wb = Workbook()
    ws = wb.active
    ws.title = "Reporte"
    
    if data:
        headers = list(data[0].keys())
        ws.append(headers)
        for row in data:
            ws.append([row[col] for col in headers])
    
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output

def exportar_pdf(data: list) -> io.BytesIO:
    output = io.BytesIO()
    doc = SimpleDocTemplate(output, pagesize=letter)
    
    elements = []
    
    if data:
        headers = list(data[0].keys())
        table_data = [headers]
        for row in data:
            table_data.append([str(row[col]) for col in headers])
        
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)
    
    doc.build(elements)
    output.seek(0)
    return output

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
    metodo_pago: Optional[str] = Query(None, description="Método de pago: tarjeta_credito, tarjeta_debito, monedero_electronico"),
    estado: Optional[str] = Query(None, description="Estado: aprobado, rechazado, reembolsado"),
    rango_monto_min: Optional[float] = Query(None, ge=0, description="Monto mínimo"),
    rango_monto_max: Optional[float] = Query(None, ge=0, description="Monto máximo"),
    formato: str = Query("json", description="Formato: json, csv"),
    admin: dict = Depends(verify_admin)
):
    from repository.pago_repository import PagoRepository
    from repository.usuario_repository import UsuarioRepository
    from datetime import datetime
    from fastapi.responses import JSONResponse, StreamingResponse
    import io
    import csv
    
    try:
        # ========== VALIDACIÓN DE RANGO DE FECHAS ==========
        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "statusCode": 400,
                    "message": "Rango de fechas inválido",
                    "error": {"code": "INVALID_DATE_RANGE"}
                }
            )
        
        # ========== VALIDACIÓN DE RANGO DE MONTOS ==========
        if rango_monto_min is not None and rango_monto_max is not None and rango_monto_min > rango_monto_max:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "statusCode": 400,
                    "message": "Rango de montos inválido",
                    "error": {
                        "code": "INVALID_DATA",
                        "details": "El monto mínimo no puede ser mayor al monto máximo"
                    }
                }
            )
        
        # ========== VALIDACIÓN DE MÉTODO DE PAGO ==========
        metodos_validos = ["tarjeta_credito", "tarjeta_debito", "monedero_electronico"]
        if metodo_pago and metodo_pago not in metodos_validos:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "statusCode": 400,
                    "message": "Método de pago inválido",
                    "error": {"code": "INVALID_DATA"}
                }
            )
        
        # ========== VALIDACIÓN DE ESTADO ==========
        estados_validos = ["aprobado", "rechazado", "reembolsado"]
        if estado and estado not in estados_validos:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "statusCode": 400,
                    "message": "Estado inválido",
                    "error": {"code": "INVALID_DATA"}
                }
            )
        
        pago_repo = PagoRepository()
        usuario_repo = UsuarioRepository()
        
        pagos_filtrados = []
        total_aprobados = 0
        total_rechazados = 0
        total_reembolsados = 0
        
        for pago in pago_repo._db.values():
            if metodo_pago and pago["metodo_pago"] != metodo_pago:
                continue
            if estado and pago["estado"] != estado:
                continue
            
            if fecha_inicio:
                fecha_inicio_dt = datetime.strptime(fecha_inicio, "%Y-%m-%d")
                if pago["fecha_pago"].date() < fecha_inicio_dt.date():
                    continue
            if fecha_fin:
                fecha_fin_dt = datetime.strptime(fecha_fin, "%Y-%m-%d")
                if pago["fecha_pago"].date() > fecha_fin_dt.date():
                    continue
            
            # Filtro por rango de montos
            if rango_monto_min is not None and pago["monto"] < rango_monto_min:
                continue
            if rango_monto_max is not None and pago["monto"] > rango_monto_max:
                continue
            
            usuario = usuario_repo.get_by_id(pago["usuario_id"])
            
            pago_data = {
                "id": pago["id"],
                "fecha_pago": pago["fecha_pago"].isoformat(),
                "monto": pago["monto"],
                "metodo_pago": pago["metodo_pago"],
                "estado": pago["estado"],
                "reserva_id": pago["reserva_id"],
                "usuario_nombre": usuario.nombre if usuario else "Desconocido",
                "usuario_email": usuario.correo if usuario else "desconocido@example.com",
                "transaccion_id": pago["transaccion_id"],
                "motivo_rechazo": pago.get("motivo_rechazo")
            }
            pagos_filtrados.append(pago_data)
            
            if pago["estado"] == "aprobado":
                total_aprobados += pago["monto"]
            elif pago["estado"] == "rechazado":
                total_rechazados += pago["monto"]
            elif pago["estado"] == "reembolsado":
                total_reembolsados += pago["monto"]
        
        # ========== EXPORTAR A CSV ==========
        if formato == "csv":
            output = io.StringIO()
            if pagos_filtrados:
                writer = csv.DictWriter(output, fieldnames=pagos_filtrados[0].keys())
                writer.writeheader()
                writer.writerows(pagos_filtrados)
            return StreamingResponse(
                io.BytesIO(output.getvalue().encode('utf-8-sig')),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=reporte_pagos.csv"}
            )
        
        # ========== RESPUESTA JSON ==========
        return {
            "success": True,
            "statusCode": 200,
            "message": "Reporte generado exitosamente" if pagos_filtrados else "No hay pagos con los filtros seleccionados",
            "data": {
                "filtros_aplicados": {
                    "fecha_inicio": fecha_inicio,
                    "fecha_fin": fecha_fin,
                    "metodo_pago": metodo_pago,
                    "estado": estado,
                    "rango_monto_min": rango_monto_min,
                    "rango_monto_max": rango_monto_max
                },
                "total_registros": len(pagos_filtrados),
                "totales": {
                    "total_transacciones": len(pagos_filtrados),
                    "total_aprobados": total_aprobados,
                    "total_rechazados": total_rechazados,
                    "total_reembolsados": total_reembolsados
                },
                "reporte": pagos_filtrados
            }
        }
    
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"success": False, "statusCode": 400, "message": str(e), "error": {"code": "INVALID_DATA"}}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "statusCode": 500, "message": "Error interno", "error": {"code": "INTERNAL_ERROR", "details": str(e)}}
        )

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
        
        # Validar período
        periodos_validos = ["dia", "semana", "mes", "rango"]
        if periodo not in periodos_validos:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "statusCode": 400,
                    "message": "Período inválido",
                    "error": {"code": "INVALID_PERIOD", "details": f"Período debe ser: {', '.join(periodos_validos)}"}
                }
            )
        
        # Validar rango
        if periodo == "rango" and (not fecha_inicio or not fecha_fin):
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "statusCode": 400,
                    "message": "Rango de fechas requerido",
                    "error": {"code": "INVALID_DATE_RANGE"}
                }
            )
        
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
        raise HTTPException(status_code=500, detail={"success": False, "statusCode": 500, "message": error_msg})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"success": False, "statusCode": 500, "message": str(e)})