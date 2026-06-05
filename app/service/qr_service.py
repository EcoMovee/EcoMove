import qrcode
from io import BytesIO
import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta
from typing import Tuple
import os

SECRET_KEY = os.getenv("QR_SECRET", "tu-clave-secreta-para-hmac-sha256-minimo-32-caracteres")
ALGORITHM = "sha256"
QR_EXPIRATION_MINUTES = 10

class QRService:
    
    @staticmethod
    def generar_contenido_firmado(reserva_id: int, vehiculo_id: int, 
                                   fecha_inicio: datetime, fecha_fin: datetime) -> Tuple[str, str, datetime]:
        """Genera el contenido cifrado y la firma digital"""
        
        fecha_expiracion = datetime.now() + timedelta(minutes=QR_EXPIRATION_MINUTES)
        exp_timestamp = int(fecha_expiracion.timestamp())
        
        datos = {
            "reserva_id": reserva_id,
            "vehiculo_id": vehiculo_id,
            "inicio": fecha_inicio.isoformat(),
            "fin": fecha_fin.isoformat(),
            "exp": exp_timestamp
        }
        
        string_to_sign = f"{reserva_id}:{vehiculo_id}:{fecha_inicio.isoformat()}:{fecha_fin.isoformat()}:{exp_timestamp}"
        
        firma = hmac.new(
            SECRET_KEY.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        datos["firma"] = firma
        
        return json.dumps(datos), firma, fecha_expiracion
    
    @staticmethod
    def generar_imagen_qr(datos_cifrados: str) -> str:
        """Genera la imagen QR en Base64"""
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(datos_cifrados)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/png;base64,{img_base64}"
    
    @staticmethod
    def generar_hash(datos: str) -> str:
        """Genera hash del contenido para almacenar"""
        return hashlib.sha256(datos.encode('utf-8')).hexdigest()