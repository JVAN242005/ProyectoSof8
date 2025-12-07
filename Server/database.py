from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ⚠️ CAMBIA ESTO CON TUS DATOS REALES ⚠️
# Formato: mysql+pymysql://usuario:contraseña@localhost:3306/nombre_bd
DATABASE_URL = "mysql+pymysql://root:1234@localhost/asistencia"  # ajusta credenciales

# Crear conexión a MySQL
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Crear sesión para consultas
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()