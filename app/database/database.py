from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'ecomove.db')
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ─── ENUMS ───

class TipoVehiculoDB(str, enum.Enum):
    CARRO = "carro"
    MOTO = "moto"
    BICICLETA = "bicicleta"

class EstadoVehiculoDB(str, enum.Enum):
    DISPONIBLE = "disponible"
    EN_USO = "en_uso"
    MANTENIMIENTO = "mantenimiento"

class EstadoReservaDB(str, enum.Enum):
    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"
    COMPLETADA = "completada"

class EstadoPagoDB(str, enum.Enum):
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"
    REEMBOLSADO = "reembolsado"

class MetodoPagoDB(str, enum.Enum):
    TARJETA_CREDITO = "tarjeta_credito"
    TARJETA_DEBITO = "tarjeta_debito"
    MONEDERO_ELECTRONICO = "monedero_electronico"


# ─── TABLA USUARIOS ───

class UsuarioDB(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(100), unique=True, nullable=False)
    telefono = Column(String(20), nullable=False)
    contrasena_hash = Column(String(255), nullable=False)
    rol = Column(String(20), default="usuario")
    estado = Column(Boolean, default=True)
    fecha_registro = Column(DateTime, default=datetime.now)


# ─── TABLA VEHICULOS ───

class VehiculoDB(Base):
    __tablename__ = "vehiculos"
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(Enum(TipoVehiculoDB), nullable=False)
    modelo = Column(String(100), unique=True, nullable=False)
    ubicacion = Column(String(255), nullable=False)
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)
    tarifaPorHora = Column(Float, nullable=False)
    estado = Column(Enum(EstadoVehiculoDB), default=EstadoVehiculoDB.DISPONIBLE)
    fecha_registro = Column(DateTime, default=datetime.now)
    nivel_bateria = Column(Integer, default=100)


# ─── TABLA RESERVAS ───

class ReservaDB(Base):
    __tablename__ = "reservas"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    vehiculo_id = Column(Integer, ForeignKey("vehiculos.id"), nullable=False)
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime, nullable=False)
    costo_estimado = Column(Float, nullable=False)
    estado = Column(Enum(EstadoReservaDB), default=EstadoReservaDB.PENDIENTE)
    fecha_reserva = Column(DateTime, default=datetime.now)


# ─── TABLA PAGOS ───

class PagoDB(Base):
    __tablename__ = "pagos"
    id = Column(Integer, primary_key=True, index=True)
    reserva_id = Column(Integer, ForeignKey("reservas.id"), unique=True, nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    monto = Column(Float, nullable=False)
    metodo_pago = Column(Enum(MetodoPagoDB), nullable=False)
    estado = Column(Enum(EstadoPagoDB), nullable=False)
    transaccion_id = Column(String(100), nullable=False)
    fecha_pago = Column(DateTime, default=datetime.now)
    motivo_rechazo = Column(String(255), nullable=True)


# ─── FUNCIONES ───

def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ Base de datos inicializada correctamente")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()