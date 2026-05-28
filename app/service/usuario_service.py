# app/services/usuario_service.py
import bcrypt
import re
from datetime import datetime, date
from domain.usuario_domain import Usuario
from repository.usuario_repository import UsuarioRepository
from core.constants import ErrorCodes

class UsuarioService:
    def __init__(self):
        self.repository = UsuarioRepository()
    
    def register(self, nombre: str, correo: str, contrasena: str, telefono: str, fecha_nacimiento: str = None) -> Usuario:
        """
        Registrar un nuevo usuario
        """
        print("🔵 INICIO DE REGISTER - Validaciones")
        
        # Normalizar email a minúsculas
        correo = correo.lower().strip()
        print(f"   Email normalizado: {correo}")
        
        # 1. Validar que el email no esté registrado
        print("   Validando email único...")
        existing_user = self.repository.get_by_email(correo)
        if existing_user:
            print("   ❌ Email ya existe")
            raise ValueError(ErrorCodes.EMAIL_EXISTS)
        print("   ✅ Email disponible")
        
        # 2. Validar contraseña
        print("   Validando contraseña...")
        self._validate_password(contrasena)
        print("   ✅ Contraseña válida")
        
        # 3. Validar teléfono
        print("   Validando teléfono...")
        self._validate_phone(telefono)
        print("   ✅ Teléfono válido")
        
        # 4. Validar edad (mayor de 18)
        edad_validada = None
        if fecha_nacimiento:
            print("   Validando edad...")
            edad_validada = self._validate_age(fecha_nacimiento)
            print(f"   ✅ Edad válida: {edad_validada}")
        
        # 5. Encriptar contraseña con bcrypt
        print("   Encriptando contraseña con bcrypt...")
        salt = bcrypt.gensalt(rounds=10)
        hashed_password = bcrypt.hashpw(contrasena.encode('utf-8'), salt)
        print("   ✅ Contraseña encriptada")
        
        # 6. Crear objeto usuario
        print("   Creando objeto Usuario...")
        usuario = Usuario(
            nombre=nombre.strip(),
            correo=correo,
            telefono=telefono,
            contrasena_hash=hashed_password.decode('utf-8'),
            fecha_nacimiento=edad_validada,
            rol="usuario",
            estado=True
        )
        print("   ✅ Usuario creado")
        
        # 7. Guardar en base de datos
        print("   Guardando en base de datos...")
        resultado = self.repository.create(usuario)
        print("🔵 FIN DE REGISTER - Éxito")
        return resultado
    
    def _validate_password(self, password: str) -> None:
        """Validar requisitos de contraseña"""
        errors = []
        if len(password) < 8:
            errors.append("mínimo 8 caracteres")
        if not re.search(r'[A-Z]', password):
            errors.append("al menos una mayúscula")
        if not re.search(r'[0-9]', password):
            errors.append("al menos un número")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("al menos un carácter especial")
        
        if errors:
            error_msg = f"La contraseña debe tener: {', '.join(errors)}"
            print(f"   ❌ {error_msg}")
            raise ValueError(error_msg)
    
    def _validate_phone(self, phone: str) -> None:
        """Validar formato de teléfono internacional"""
        if not re.match(r'^\+\d{1,3}\d{7,15}$', phone):
            error_msg = "El teléfono debe tener código de país y entre 7 y 15 dígitos. Ejemplo: +573001234567"
            print(f"   ❌ {error_msg}")
            raise ValueError(error_msg)
    
    def _validate_age(self, birth_date_str: str) -> date:
        """Validar que el usuario sea mayor de 18 años"""
        try:
            if isinstance(birth_date_str, str):
                birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
            else:
                birth_date = birth_date_str
            
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            
            if age < 18:
                error_msg = "Debes ser mayor de 18 años para registrarte"
                print(f"   ❌ {error_msg} (edad: {age})")
                raise ValueError(error_msg)
            
            print(f"   ✅ Edad válida: {age} años")
            return birth_date
        except ValueError as e:
            if "mayor de 18" in str(e):
                raise
            error_msg = "Formato de fecha inválido. Use YYYY-MM-DD"
            print(f"   ❌ {error_msg}")
            raise ValueError(error_msg)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verificar contraseña contra su hash"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))