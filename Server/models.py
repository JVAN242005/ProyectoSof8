from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, Text, Time, Date, ForeignKey, SmallInteger
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    cedula = Column(String(12), unique=True, nullable=False)
    rol = Column(Enum('Estudiante', 'Docente', 'Administrador'), nullable=False)
    grupo = Column(String(20))
    correo = Column(String(120), unique=True)
    password = Column(String(255))
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

class Aula(Base):
    __tablename__ = "aulas"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    aula = Column(String(10), nullable=False)
    edificio = Column(SmallInteger, nullable=False)
    device_id = Column(String(50), unique=True, nullable=False)
    estado = Column(Enum('Activo', 'Desconectado'), default='Activo')
    ultima_conexion = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)

class Asistencia(Base):  # NOTA: Se llama "Asistencia" no "Registro"
    __tablename__ = "asistencias"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    rol = Column(Enum('Estudiante', 'Docente'), nullable=False)
    curso = Column(String(20))
    aula_id = Column(Integer, ForeignKey('aulas.id'))
    tipo = Column(Enum('Entrada', 'Salida'), nullable=False)
    fecha = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    estado = Column(Enum('A tiempo', 'Tarde', 'Ausente', 'Justificado', 'Cumplió horario'), nullable=False)
    device_id = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)
    
    # Relaciones
    usuario = relationship("Usuario")
    aula = relationship("Aula")

class Justificante(Base):
    __tablename__ = "justificantes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    asistencia_id = Column(Integer, ForeignKey('asistencias.id'), nullable=False)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    fecha_registro = Column(Date, nullable=False)
    fecha_documento = Column(Date, nullable=False)
    motivo = Column(Text, nullable=False)
    referencia = Column(String(50))
    archivo_nombre = Column(String(200))
    archivo_url = Column(String(500))
    archivo_mime = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)