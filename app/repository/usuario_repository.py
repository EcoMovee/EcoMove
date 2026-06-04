from typing import List, Optional
from domain.usuario_domain import Usuario
from datetime import datetime

class UsuarioRepository:
    _instance = None
    _usuarios = None
    _counter = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._usuarios = []
            cls._instance._counter = 1
        return cls._instance
    
    def __init__(self):
        pass
    
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
    
    def update(self, user_id: int, usuario: Usuario) -> Optional[Usuario]:
        for i, u in enumerate(self._usuarios):
            if u.id == user_id:
                usuario.id = user_id
                self._usuarios[i] = usuario
                return usuario
        return None
    
    def count_administradores_activos(self) -> int:
        count = 0
        for usuario in self._usuarios:
            if usuario.rol == "administrador" and usuario.estado:
                count += 1
        return count
    
    def usuario_tiene_reservas_activas(self, user_id: int) -> bool:
        return False
    
    def crear_administrador_inicial(self):
        import bcrypt
        
        for usuario in self._usuarios:
            if usuario.rol == "administrador":
                print(f"✅ Administrador ya existe: {usuario.correo}")
                return usuario
        
        hashed = bcrypt.hashpw("Admin123!".encode('utf-8'), bcrypt.gensalt())
        
        admin = Usuario(
            nombre="Administrador",
            correo="admin@ecomove.com",
            telefono="+573001234567",
            contrasena_hash=hashed.decode('utf-8'),
            rol="administrador",
            estado=True
        )
        
        resultado = self.create(admin)
        print(f"✅ Administrador creado: {resultado.correo} / Contraseña: Admin123!")
        return resultado