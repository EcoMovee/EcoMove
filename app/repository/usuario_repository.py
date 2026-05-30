from typing import List, Optional
from domain.usuario_domain import Usuario
from datetime import datetime

class UsuarioRepository:
    def __init__(self):
        self._usuarios: List[Usuario] = []
        self._counter = 1
    
    def create(self, usuario: Usuario) -> Usuario:
        usuario.id = self._counter
        self._counter += 1
        self._usuarios.append(usuario)
        return usuario
    
    def get_by_email(self, correo: str) -> Optional[Usuario]:
        for usuario in self._usuarios:
            if usuario.correo == correo.lower():
                return usuario
        return None
    
    def get_by_id(self, id: int) -> Optional[Usuario]:
        for usuario in self._usuarios:
            if usuario.id == id:
                return usuario
        return None
    
    def update_intentos_fallidos(self, user_id: int, intentos: int) -> None:
        for usuario in self._usuarios:
            if usuario.id == user_id:
                usuario.intentos_fallidos = intentos
                break
    
    def update_bloqueo(self, user_id: int, bloqueado_hasta: Optional[datetime]) -> None:
        for usuario in self._usuarios:
            if usuario.id == user_id:
                usuario.bloqueado_hasta = bloqueado_hasta
                break
    
    def reset_intentos_y_bloqueo(self, user_id: int) -> None:
        for usuario in self._usuarios:
            if usuario.id == user_id:
                usuario.intentos_fallidos = 0
                usuario.bloqueado_hasta = None
                break
    
    # NUEVO MÉTODO PARA HU-003
    def update(self, user_id: int, usuario: Usuario) -> Optional[Usuario]:
        """Actualiza un usuario existente"""
        for i, u in enumerate(self._usuarios):
            if u.id == user_id:
                usuario.id = user_id
                self._usuarios[i] = usuario
                return usuario
        return None