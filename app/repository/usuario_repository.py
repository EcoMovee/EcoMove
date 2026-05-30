from typing import List, Optional
from domain.usuario_domain import Usuario

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