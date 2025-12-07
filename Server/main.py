from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import text  
from sqlalchemy.orm import Session
from uuid import uuid4
from database import engine, Base, get_db
import datetime
import models

# 1. Crear tablas en MySQL (si no existen)
Base.metadata.create_all(bind=engine)

# 2. Crear aplicación FastAPI
app = FastAPI(
    title="Sistema IoT Asistencia",
    description="Backend para tu proyecto con ESP32",
    version="1.0"
)

# 3. Permitir conexión desde frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# 4. RUTA DE PRUEBA BÁSICA
@app.get("/")
def inicio():
    return {
        "mensaje": "✅ Backend funcionando con MySQL",
        "base_datos": "Asistencia",
        "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "estado": "Listo para conectar frontend"
    }

# 5. RUTA PARA VERIFICAR CONEXIÓN A BD - VERSIÓN CORREGIDA
@app.get("/api/status")
def verificar_estado():
    try:
        # IMPORTANTE: Usar text() para queries SQL
        from sqlalchemy import text
        
        # Intentar conexión simple a BD
        with engine.connect() as conn:
            # Usar text() para convertir string SQL a objeto ejecutable
            result = conn.execute(text("SELECT 1"))
            # Obtener resultado
            row = result.fetchone()
            
        return {
            "success": True,
            "message": "✅ Conectado a MySQL",
            "database": "asistencia",
            "test_query_result": row[0] if row else None
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"❌ Error conectando a MySQL: {str(e)}",
            "sugerencia": "Verifica DATABASE_URL en database.py"
        }

class LoginRequest(BaseModel):
  correo: str
  password: str

class LoginResponse(BaseModel):
  user: dict  # devolvemos solo los datos básicos del usuario

@app.post("/api/login", response_model=LoginResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
  # Buscar usuario por correo
  user = db.query(models.Usuario).filter(models.Usuario.correo == body.correo).first()

  # Validar credenciales (usa hash si lo implementas)
  if not user or user.password != body.password:
    raise HTTPException(status_code=401, detail="Credenciales inválidas")

  # Responder solo con los datos necesarios del usuario
  return {"user": {
    "id": user.id,
    "nombre": user.nombre,
    "correo": user.correo,
    "rol": user.rol
  }}