from app.domain.vehiculo_domain import Vehiculo, VehiculoCreate
from app.repository.vehiculo_repository import VehiculoRepository


class VehiculoService:
    
    def __init__(self, repo: VehiculoRepository):
        self.repo = repo

    def create(self, data: VehiculoCreate) -> Vehiculo:
        existing = self.repo.get_by_modelo(data.modelo)
        if existing:
            raise ValueError("VEHICLE_ALREADY_EXISTS")
        return self.repo.create(data)