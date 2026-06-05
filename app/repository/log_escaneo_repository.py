from typing import List, Optional
from domain.log_escaneo_domain import LogEscaneoQR, ResultadoEscaneo

class LogEscaneoRepository:
    def __init__(self):
        self._logs: List[LogEscaneoQR] = []
        self._counter = 1
    
    def create(self, log: LogEscaneoQR) -> LogEscaneoQR:
        log.id = self._counter
        self._counter += 1
        self._logs.append(log)
        return log
    
    def get_by_qr_id(self, qr_id: int) -> List[LogEscaneoQR]:
        return [log for log in self._logs if log.qr_id == qr_id]

# Instancia global
log_repo = LogEscaneoRepository()