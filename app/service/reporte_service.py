from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
import csv
import io
from openpyxl import Workbook
import pdfkit
from app.repository.reserva_repository import reserva_repo
from app.repository.usuario_repository import UsuarioRepository
from app.repository.vehiculo_repository import VehiculoRepository


class ReporteService:
    
    def __init__(self):
        self.usuario_repo = UsuarioRepository()
        self.vehiculo_repo = VehiculoRepository()

    def _validar_fechas(self, fecha_inicio: Optional[date], fecha_fin: Optional[date]):
        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            raise ValueError("INVALID_DATE_RANGE")

    def _validar_estados(self, estados: Optional[List[str]]):
        estados_validos = ["pendiente", "confirmada", "en_curso", "finalizada", "cancelada"]
        if estados:
            for estado in estados:
                if estado not in estados_validos:
                    raise ValueError("INVALID_STATUS")

    def _validar_metodo_pago(self, metodo_pago: Optional[str]):
        metodos_validos = ["tarjeta_credito", "tarjeta_debito", "monedero_electronico"]
        if metodo_pago and metodo_pago not in metodos_validos:
            raise ValueError("INVALID_DATA")

    def _validar_estado_pago(self, estado: Optional[str]):
        estados_validos = ["aprobado", "rechazado", "reembolsado"]
        if estado and estado not in estados_validos:
            raise ValueError("INVALID_DATA")

    def _validar_formato(self, formato: str):
        formatos_validos = ["json", "csv", "xlsx", "pdf"]
        if formato not in formatos_validos:
            raise ValueError("INVALID_FORMAT")

    def _calcular_resumen(self, reservas: List[Dict]) -> Dict[str, Any]:
        total_reservas = len(reservas)
        total_ingresos = 0
        total_duracion = 0
        
        for r in reservas:
            if r["estado"] in ["confirmada", "finalizada"]:
                total_ingresos += r["costo_estimado"]
            total_duracion += r["duracion_horas"]
        
        duracion_promedio = round(total_duracion / total_reservas, 2) if total_reservas > 0 else 0
        
        return {
            "total_reservas": total_reservas,
            "total_ingresos": round(total_ingresos, 2),
            "duracion_promedio_horas": duracion_promedio
        }

    def _aplicar_filtros(self, reservas: List, filtros: Dict) -> List:
        resultado = []
        
        for r in reservas:
            if filtros.get("fecha_inicio"):
                fecha_reserva = r.fecha if hasattr(r, 'fecha') else r["fecha"]
                if fecha_reserva < filtros["fecha_inicio"]:
                    continue
            if filtros.get("fecha_fin"):
                fecha_reserva = r.fecha if hasattr(r, 'fecha') else r["fecha"]
                if fecha_reserva > filtros["fecha_fin"]:
                    continue
            
            if filtros.get("estados") and len(filtros["estados"]) > 0:
                estado_actual = r.estado.value if hasattr(r, 'estado') else r["estado"]
                if estado_actual not in filtros["estados"]:
                    continue
            
            usuario_id = r.usuario_id if hasattr(r, 'usuario_id') else r["usuario_id"]
            vehiculo_id = r.vehiculo_id if hasattr(r, 'vehiculo_id') else r["vehiculo_id"]
            
            usuario = self.usuario_repo.get_by_id(usuario_id)
            vehiculo = self.vehiculo_repo.get_by_id(vehiculo_id)
            
            resultado.append({
                "id": r.id if hasattr(r, 'id') else r["id"],
                "usuario_nombre": usuario.nombre if usuario else "Desconocido",
                "usuario_email": usuario.correo if usuario else "Desconocido",
                "vehiculo_tipo": vehiculo.tipo if vehiculo else "Desconocido",
                "vehiculo_modelo": vehiculo.modelo if vehiculo else "Desconocido",
                "fecha": r.fecha.isoformat() if hasattr(r, 'fecha') else r["fecha"],
                "hora_inicio": r.hora_inicio.strftime("%H:%M") if hasattr(r, 'hora_inicio') else r["hora_inicio"],
                "hora_fin": r.hora_fin.strftime("%H:%M") if hasattr(r, 'hora_fin') else r["hora_fin"],
                "duracion_horas": r.duracion_horas if hasattr(r, 'duracion_horas') else r["duracion_horas"],
                "costo_estimado": r.costo_estimado if hasattr(r, 'costo_estimado') else r["costo_estimado"],
                "estado": r.estado.value if hasattr(r, 'estado') else r["estado"],
                "fecha_creacion": r.fecha_creacion.isoformat() if hasattr(r, 'fecha_creacion') else r["fecha_creacion"]
            })
        
        return resultado

    def generar_reporte_reservas(self, filtros: Dict) -> Dict[str, Any]:
        self._validar_fechas(filtros.get("fecha_inicio"), filtros.get("fecha_fin"))
        self._validar_estados(filtros.get("estados"))
        self._validar_formato(filtros.get("formato", "json"))
        
        todas_reservas = list(reserva_repo._db.values())
        reservas_filtradas = self._aplicar_filtros(todas_reservas, filtros)
        resumen = self._calcular_resumen(reservas_filtradas)
        
        return {
            "filtros_aplicados": {
                "fecha_inicio": filtros.get("fecha_inicio").isoformat() if filtros.get("fecha_inicio") else None,
                "fecha_fin": filtros.get("fecha_fin").isoformat() if filtros.get("fecha_fin") else None,
                "estados": filtros.get("estados")
            },
            "total_registros": len(reservas_filtradas),
            "resumen": resumen,
            "reporte": reservas_filtradas
        }

    def _aplicar_filtros_pagos(self, pagos: List, filtros: Dict) -> List:
        resultado = []
        
        for p in pagos:
            if filtros.get("fecha_inicio"):
                if p["fecha_pago"].date() < filtros["fecha_inicio"]:
                    continue
            if filtros.get("fecha_fin"):
                if p["fecha_pago"].date() > filtros["fecha_fin"]:
                    continue
            
            if filtros.get("metodo_pago") and p["metodo_pago"] != filtros["metodo_pago"]:
                continue
            
            if filtros.get("estado") and p["estado"] != filtros["estado"]:
                continue
            
            usuario = self.usuario_repo.get_by_id(p["usuario_id"])
            reserva = reserva_repo.get_by_id(p["reserva_id"])
            
            resultado.append({
                "id": p["id"],
                "fecha_pago": p["fecha_pago"].isoformat(),
                "monto": p["monto"],
                "metodo_pago": p["metodo_pago"],
                "estado": p["estado"],
                "reserva_id": p["reserva_id"],
                "usuario_nombre": usuario.nombre if usuario else "Desconocido",
                "usuario_email": usuario.correo if usuario else "Desconocido",
                "transaccion_id": p["transaccion_id"],
                "motivo_rechazo": p.get("motivo_rechazo")
            })
        
        return resultado

    def _calcular_totales_pagos(self, pagos: List[Dict]) -> Dict[str, Any]:
        total_transacciones = len(pagos)
        total_aprobados = 0
        total_rechazados = 0
        total_reembolsados = 0
        
        for p in pagos:
            if p["estado"] == "aprobado":
                total_aprobados += p["monto"]
            elif p["estado"] == "rechazado":
                total_rechazados += p["monto"]
            elif p["estado"] == "reembolsado":
                total_reembolsados += p["monto"]
        
        return {
            "total_transacciones": total_transacciones,
            "total_aprobados": round(total_aprobados, 2),
            "total_rechazados": round(total_rechazados, 2),
            "total_reembolsados": round(total_reembolsados, 2)
        }

    def generar_reporte_pagos(self, filtros: Dict) -> Dict[str, Any]:
        from app.repository.pago_repository import PagoRepository
        pago_repo = PagoRepository()
        
        self._validar_fechas(filtros.get("fecha_inicio"), filtros.get("fecha_fin"))
        self._validar_metodo_pago(filtros.get("metodo_pago"))
        self._validar_estado_pago(filtros.get("estado"))
        self._validar_formato(filtros.get("formato", "json"))
        
        todos_pagos = list(pago_repo._db.values())
        pagos_filtrados = self._aplicar_filtros_pagos(todos_pagos, filtros)
        totales = self._calcular_totales_pagos(pagos_filtrados)
        
        return {
            "filtros_aplicados": {
                "fecha_inicio": filtros.get("fecha_inicio").isoformat() if filtros.get("fecha_inicio") else None,
                "fecha_fin": filtros.get("fecha_fin").isoformat() if filtros.get("fecha_fin") else None,
                "metodo_pago": filtros.get("metodo_pago"),
                "estado": filtros.get("estado")
            },
            "total_registros": len(pagos_filtrados),
            "totales": totales,
            "reporte": pagos_filtrados
        }

    def exportar_csv(self, data: List[Dict]) -> str:
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys() if data else [])
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue()

    def exportar_excel(self, data: List[Dict]) -> bytes:
        wb = Workbook()
        ws = wb.active
        ws.title = "Reporte"
        
        if data:
            headers = list(data[0].keys())
            ws.append(headers)
            for row in data:
                ws.append(list(row.values()))
        
        output = io.BytesIO()
        wb.save(output)
        return output.getvalue()

    def exportar_pdf(self, data: List[Dict]) -> bytes:
        html = "<html><head><meta charset='UTF-8'><title>Reporte</title></head><body>"
        html += "<h1>Reporte</h1>"
        html += "<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>"
        
        if data:
            headers = list(data[0].keys())
            html += "<tr>" + "".join(f"<th>{h}</th>" for h in headers) + "</tr>"
            for row in data:
                html += "<tr>" + "".join(f"<td>{v}</td>" for v in row.values()) + "</tr>"
        
        html += "</table></body></html>"
        return html.encode('utf-8')
    
    # ==================== HU-023: Vehículos más usados ====================

    def _calcular_periodo(self, periodo: str, fecha_inicio: Optional[date], fecha_fin: Optional[date]) -> tuple:
        hoy = date.today()
        
        if periodo == "dia":
            fecha_inicio = hoy
            fecha_fin = hoy
        elif periodo == "semana":
            fecha_inicio = hoy - timedelta(days=7)
            fecha_fin = hoy
        elif periodo == "mes":
            fecha_inicio = hoy - timedelta(days=30)
            fecha_fin = hoy
        elif periodo == "rango":
            if not fecha_inicio or not fecha_fin:
                raise ValueError("INVALID_DATE_RANGE")
            if fecha_inicio > fecha_fin:
                raise ValueError("INVALID_DATE_RANGE")
        else:
            raise ValueError("INVALID_PERIOD")
        
        return fecha_inicio, fecha_fin

    def generar_ranking_vehiculos(self, filtros: Dict) -> Dict[str, Any]:
        from app.repository.reserva_repository import reserva_repo
        from app.repository.vehiculo_repository import VehiculoRepository
        
        vehiculo_repo = VehiculoRepository()
        
        # Validar período
        periodo = filtros.get("periodo")
        fecha_inicio = filtros.get("fecha_inicio")
        fecha_fin = filtros.get("fecha_fin")
        
        fecha_inicio, fecha_fin = self._calcular_periodo(periodo, fecha_inicio, fecha_fin)
        self._validar_formato(filtros.get("formato", "json"))
        
        # Obtener todas las reservas
        todas_reservas = list(reserva_repo._db.values())
        
        # Filtrar por fecha y estados finalizados/confirmados
        reservas_filtradas = []
        for r in todas_reservas:
            fecha_reserva = r.fecha if hasattr(r, 'fecha') else r["fecha"]
            estado = r.estado.value if hasattr(r, 'estado') else r["estado"]
            
            if fecha_inicio <= fecha_reserva <= fecha_fin:
                if estado in ["finalizada", "confirmada", "en_curso"]:
                    reservas_filtradas.append(r)
        
        # Agrupar por vehículo
        ranking = {}
        for r in reservas_filtradas:
            vehiculo_id = r.vehiculo_id if hasattr(r, 'vehiculo_id') else r["vehiculo_id"]
            duracion = r.duracion_horas if hasattr(r, 'duracion_horas') else r["duracion_horas"]
            costo = r.costo_estimado if hasattr(r, 'costo_estimado') else r["costo_estimado"]
            
            if vehiculo_id not in ranking:
                vehiculo = vehiculo_repo.get_by_id(vehiculo_id)
                ranking[vehiculo_id] = {
                    "id": vehiculo_id,
                    "tipo": vehiculo.tipo if vehiculo else "Desconocido",
                    "modelo": vehiculo.modelo if vehiculo else "Desconocido",
                    "ubicacion": vehiculo.ubicacion if vehiculo else "Desconocido",
                    "cantidad_reservas": 0,
                    "horas_totales_uso": 0,
                    "ingresos_generados": 0
                }
            
            ranking[vehiculo_id]["cantidad_reservas"] += 1
            ranking[vehiculo_id]["horas_totales_uso"] += duracion
            ranking[vehiculo_id]["ingresos_generados"] += costo
        
        # Convertir a lista y ordenar
        ranking_lista = list(ranking.values())
        ranking_lista.sort(key=lambda x: x["cantidad_reservas"], reverse=True)
        
        # Agregar posición
        for i, item in enumerate(ranking_lista, 1):
            item["posicion"] = i
        
        # Calcular resumen
        total_vehiculos = len(ranking_lista)
        total_reservas = sum(item["cantidad_reservas"] for item in ranking_lista)
        total_horas = sum(item["horas_totales_uso"] for item in ranking_lista)
        total_ingresos = sum(item["ingresos_generados"] for item in ranking_lista)
        
        return {
            "periodo": {
                "tipo": periodo,
                "fecha_inicio": fecha_inicio.isoformat(),
                "fecha_fin": fecha_fin.isoformat()
            },
            "resumen": {
                "total_vehiculos_en_ranking": total_vehiculos,
                "total_reservas_periodo": total_reservas,
                "total_horas_uso": round(total_horas, 2),
                "total_ingresos": round(total_ingresos, 2)
            },
            "ranking": ranking_lista
        }