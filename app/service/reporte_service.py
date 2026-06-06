from typing import List, Dict, Any, Optional
from datetime import datetime, date
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
            # Filtro por fechas
            if filtros.get("fecha_inicio"):
                fecha_reserva = r.fecha if hasattr(r, 'fecha') else r["fecha"]
                if fecha_reserva < filtros["fecha_inicio"]:
                    continue
            if filtros.get("fecha_fin"):
                fecha_reserva = r.fecha if hasattr(r, 'fecha') else r["fecha"]
                if fecha_reserva > filtros["fecha_fin"]:
                    continue
            
            # Filtro por estados
            if filtros.get("estados") and len(filtros["estados"]) > 0:
                estado_actual = r.estado.value if hasattr(r, 'estado') else r["estado"]
                if estado_actual not in filtros["estados"]:
                    continue
            
            # Obtener datos de usuario y vehículo
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
        # Validar parámetros
        self._validar_fechas(filtros.get("fecha_inicio"), filtros.get("fecha_fin"))
        self._validar_estados(filtros.get("estados"))
        self._validar_formato(filtros.get("formato", "json"))
        
        # Obtener todas las reservas
        todas_reservas = list(reserva_repo._db.values())
        
        # Aplicar filtros
        reservas_filtradas = self._aplicar_filtros(todas_reservas, filtros)
        
        # Calcular resumen
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

    def exportar_csv(self, data: List[Dict]) -> str:
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys() if data else [])
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue()

    def exportar_excel(self, data: List[Dict]) -> bytes:
        wb = Workbook()
        ws = wb.active
        ws.title = "Reporte de Reservas"
        
        if data:
            headers = list(data[0].keys())
            ws.append(headers)
            for row in data:
                ws.append(list(row.values()))
        
        output = io.BytesIO()
        wb.save(output)
        return output.getvalue()

    def exportar_pdf(self, data: List[Dict]) -> bytes:
        html = "<html><head><meta charset='UTF-8'><title>Reporte de Reservas</title></head><body>"
        html += "<h1>Reporte de Reservas</h1>"
        html += "<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>"
        
        if data:
            headers = list(data[0].keys())
            html += "<tr>" + "".join(f"<th>{h}</th>" for h in headers) + "</tr>"
            for row in data:
                html += "<tr>" + "".join(f"<td>{v}</td>" for v in row.values()) + "</tr>"
        
        html += "</table></body></html>"
        
        # Simular PDF (en producción usar pdfkit.from_string)
        return html.encode('utf-8')