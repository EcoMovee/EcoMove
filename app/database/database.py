# app/database/database.py
import sqlite3
from contextlib import contextmanager
from datetime import datetime
import os

# Ruta de la base de datos
DB_PATH = os.path.join(os.path.dirname(__file__), 'ecomove.db')

def get_db():
    """Obtener conexión a la base de datos"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Para acceder por nombre de columna
    return conn

@contextmanager
def get_db_context():
    """Context manager para la base de datos"""
    conn = get_db()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

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

def reset_db():
    """Reiniciar la base de datos (solo para pruebas)"""
    import os
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("🗑️ Base de datos eliminada")
    init_db()