# app/database/database.py
import sqlite3
from contextlib import contextmanager
from datetime import datetime
import os

# Ruta de la base de datos
DB_PATH = os.path.join(os.path.dirname(__file__), 'ecomove.db')

<<<<<<< HEAD

=======
>>>>>>> origin/development
def get_db():
    """Obtener conexión a la base de datos"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Para acceder por nombre de columna
    return conn

<<<<<<< HEAD

=======
>>>>>>> origin/development
@contextmanager
def get_db_context():
    """Context manager para la base de datos"""
    conn = get_db()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

<<<<<<< HEAD

def init_db():
    """Inicializar la base de datos - Crear todas las tablas"""
    with get_db_context() as conn:
        cursor = conn.cursor()

        # ── Tabla usuarios (existente) ──
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre VARCHAR(100) NOT NULL,
            correo VARCHAR(100) UNIQUE NOT NULL,
            telefono VARCHAR(20) NOT NULL,
            contrasena_hash VARCHAR(255) NOT NULL,
            rol VARCHAR(20) DEFAULT 'usuario',
            estado BOOLEAN DEFAULT 1,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            intentos_fallidos INTEGER DEFAULT 0,
            bloqueado_hasta TIMESTAMP NULL,
            fecha_nacimiento DATE NULL
        )
        ''')

        # ── Tabla vehiculos (para HU-005) ──
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehiculos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('carro', 'moto', 'bicicleta')),
            modelo VARCHAR(100) NOT NULL UNIQUE,
            ubicacion VARCHAR(255) NOT NULL,
            tarifaPorHora DECIMAL(10,2) NOT NULL CHECK (tarifaPorHora > 0),
            estado VARCHAR(20) DEFAULT 'disponible' CHECK (estado IN ('disponible', 'en_uso', 'mantenimiento')),
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            nivel_bateria INTEGER DEFAULT 100 CHECK (nivel_bateria BETWEEN 0 AND 100)
        )
        ''')

        # ── Índices ──
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_usuarios_correo ON usuarios(correo)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_vehiculos_modelo ON vehiculos(modelo)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_vehiculos_estado ON vehiculos(estado)')

        print("✅ Base de datos inicializada correctamente")


=======
def init_db():
    """Inicializar la base de datos - Crear tablas"""
    with get_db_context() as conn:
        cursor = conn.cursor()
        
        # Crear tabla usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre VARCHAR(100) NOT NULL,
                correo VARCHAR(100) UNIQUE NOT NULL,
                telefono VARCHAR(20) NOT NULL,
                contrasena_hash VARCHAR(255) NOT NULL,
                rol VARCHAR(20) DEFAULT 'usuario',
                estado BOOLEAN DEFAULT 1,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                intentos_fallidos INTEGER DEFAULT 0,
                bloqueado_hasta TIMESTAMP NULL,
                fecha_nacimiento DATE NULL
            )
        ''')
        
        # Crear índices
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_usuarios_correo ON usuarios(correo)')
        
        print("✅ Base de datos inicializada correctamente")

>>>>>>> origin/development
def reset_db():
    """Reiniciar la base de datos (solo para pruebas)"""
    import os
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("🗑️ Base de datos eliminada")
<<<<<<< HEAD
    init_db()


# ── Funciones específicas para vehículos ──
def get_all_vehiculos():
    """Obtener todos los vehículos"""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM vehiculos ORDER BY id DESC')
        return [dict(row) for row in cursor.fetchall()]


def get_vehiculo_by_id(vehiculo_id: int):
    """Obtener un vehículo por ID"""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM vehiculos WHERE id = ?', (vehiculo_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_vehiculo_by_modelo(modelo: str):
    """Obtener un vehículo por modelo (único)"""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM vehiculos WHERE modelo = ?', (modelo,))
        row = cursor.fetchone()
        return dict(row) if row else None


def create_vehiculo(tipo: str, modelo: str, ubicacion: str, tarifaPorHora: float):
    """Crear un nuevo vehículo"""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO vehiculos (tipo, modelo, ubicacion, tarifaPorHora, estado, nivel_bateria)
            VALUES (?, ?, ?, ?, 'disponible', 100)
        ''', (tipo, modelo, ubicacion, tarifaPorHora))
        vehiculo_id = cursor.lastrowid
        
        # Retornar el vehículo creado
        cursor.execute('SELECT * FROM vehiculos WHERE id = ?', (vehiculo_id,))
        return dict(cursor.fetchone())


def delete_vehiculo(vehiculo_id: int):
    """Eliminar un vehículo por ID"""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM vehiculos WHERE id = ?', (vehiculo_id,))
        return cursor.rowcount > 0


def update_vehiculo_estado(vehiculo_id: int, nuevo_estado: str):
    """Actualizar el estado de un vehículo"""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE vehiculos SET estado = ? WHERE id = ?
        ''', (nuevo_estado, vehiculo_id))
        return cursor.rowcount > 0


# ── Inicializar la base de datos al importar ──
if __name__ == "__main__":
=======
>>>>>>> origin/development
    init_db()