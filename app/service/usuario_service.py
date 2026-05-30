from domain.usuario_domain import Usuario
from repository.usuario_repository import UsuarioRepository
import bcrypt
import re
from datetime import datetime, date

class UsuarioService:
    def __init__(self):
        self.repository = UsuarioRepository()
    
    def register(self, nombre: str, correo: str, contrasena: str, telefono: str, fecha_nacimiento: str = None) -> Usuario:
        correo = correo.lower().strip()
        
        if self.repository.get_by_email(correo):
            raise ValueError("El email ya está registrado")
        
        self._validate_password(contrasena)
        self._validate_phone(telefono)
        
        edad_validada = None
        if fecha_nacimiento:
            edad_validada = self._validate_age(fecha_nacimiento)
        
        salt = bcrypt.gensalt(rounds=10)
        hashed_password = bcrypt.hashpw(contrasena.encode('utf-8'), salt)
        
        usuario = Usuario(
            nombre=nombre.strip(),
            correo=correo,
            telefono=telefono,
            contrasena_hash=hashed_password.decode('utf-8'),
            fecha_nacimiento=edad_validada,
            rol="usuario",
            estado=True
        )
        
        return self.repository.create(usuario)
    
    def _validate_password(self, password: str) -> None:
        if len(password) < 8:
            raise ValueError("La contraseña debe tener mínimo 8 caracteres")
        if not re.search(r'[A-Z]', password):
            raise ValueError("La contraseña debe tener al menos una mayúscula")
        if not re.search(r'[0-9]', password):
            raise ValueError("La contraseña debe tener al menos un número")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValueError("La contraseña debe tener al menos un carácter especial")
    
    def _validate_phone(self, phone: str) -> None:
        if not re.match(r'^\+\d{1,3}\d{7,15}$', phone):
            raise ValueError("El teléfono debe tener código de país y entre 7 y 15 dígitos")
    
    def _validate_age(self, birth_date_str: str) -> date:
        birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        if age < 18:
            raise ValueError("Debes ser mayor de 18 años para registrarte")
        return birth_date