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


#----------------PARTE DEL LOGIN------------------
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
  
  
  
  
#----------------- LISTAR USUARIOS ------------------
@app.get("/api/usuarios")
def listar_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(models.Usuario).all()
    # Serializa cada usuario a dict
    usuarios_dict = [
        {
            "id": u.id,
            "nombre": u.nombre,
            "cedula": u.cedula,
            "rol": u.rol,
            "grupo": u.grupo,
            "correo": u.correo
        }
        for u in usuarios
    ]
    return {"usuarios": usuarios_dict}

#----------------- CREAR USUARIO ------------------
class UsuarioCreate(BaseModel):
    nombre: str
    cedula: str
    rol: str
    grupo: str = None
    correo: str
    password: str = None

@app.post("/api/usuarios")
def crear_usuario(user: UsuarioCreate, db: Session = Depends(get_db)):
    # Verifica si la cédula o correo ya existen
    if db.query(models.Usuario).filter(models.Usuario.cedula == user.cedula).first():
        raise HTTPException(status_code=400, detail="Cédula ya registrada")
    if db.query(models.Usuario).filter(models.Usuario.correo == user.correo).first():
        raise HTTPException(status_code=400, detail="Correo ya registrado")
    nuevo = models.Usuario(**user.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return {"user": {
        "id": nuevo.id,
        "nombre": nuevo.nombre,
        "cedula": nuevo.cedula,
        "rol": nuevo.rol,
        "grupo": nuevo.grupo,
        "correo": nuevo.correo
    }}

#----------------- ACTUALIZAR USUARIO ------------------
class UsuarioUpdate(BaseModel):
    nombre: str = None
    cedula: str = None
    rol: str = None
    grupo: str = None
    correo: str = None
    password: str = None

@app.put("/api/usuarios/{id}")
def actualizar_usuario(id: int, user: UsuarioUpdate, db: Session = Depends(get_db)):
    u = db.query(models.Usuario).filter(models.Usuario.id == id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    for key, value in user.dict(exclude_unset=True).items():
        setattr(u, key, value)
    db.commit()
    db.refresh(u)
    return {"user": {
        "id": u.id,
        "nombre": u.nombre,
        "cedula": u.cedula,
        "rol": u.rol,
        "grupo": u.grupo,
        "correo": u.correo
    }}

#----------------- ELIMINAR USUARIO ------------------
@app.delete("/api/usuarios/{id}")
def eliminar_usuario(id: int, db: Session = Depends(get_db)):
    u = db.query(models.Usuario).filter(models.Usuario.id == id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(u)
    db.commit()
    return {"success": True, "id": id}