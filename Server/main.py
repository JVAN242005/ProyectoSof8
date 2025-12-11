from fastapi import FastAPI, HTTPException, Depends, Body, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import text  
from sqlalchemy.orm import Session
from uuid import uuid4
from database import engine, Base, get_db
import datetime
import models
import base64
from datetime import datetime, date, timedelta, time

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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
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


# ------------- LECTURA DE QR Y REGISTRO DE ASISTENCIA -------------

# Configuración de horarios
HORA_ENTRADA = time(8, 0)   # 8:00 AM (referencia, ya no se usa para tardanza)
HORA_SALIDA  = time(12, 0)  # ejemplo

# Ventana de marcaje para estudiantes y tolerancia de tardanza relativa al docente
VENTANA_MIN = 30            # minutos que dura la ventana de marcaje para estudiantes
TARDANZA_EST_MIN = 2        # minutos para considerar tardanza al estudiante tras marcar el docente

# Estado de ventana por aula (aula_id: dict con fin y tardanza)
VENTANAS_ACTIVAS = {}

def extraer_info(base64_str):
    texto = base64.b64decode(base64_str).decode('utf-8')
    if '@' in texto:
        return texto.split('@', 1)
    return texto, None

class QRAsistencia(BaseModel):
    qr_texto: str

# Registrar asistencia desde QR
@app.post("/api/asistencias/qr")
def registrar_asistencia_qr(body: QRAsistencia, db: Session = Depends(get_db)):
    cedula, _ = extraer_info(body.qr_texto)
    partes = cedula.split('-')
    partes[-1] = partes[-1].lstrip('0')
    cedula = '-'.join(partes)

    usuario = db.query(models.Usuario).filter(models.Usuario.cedula == cedula).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    ahora = datetime.now()
    hoy = ahora.date().isoformat()
    aula_id = getattr(usuario, "aula_id", None)

    # Consulta registros de hoy
    entrada_hoy = db.query(models.Asistencia).filter(
        models.Asistencia.usuario_id == usuario.id,
        models.Asistencia.fecha == hoy,
        models.Asistencia.tipo == "Entrada"
    ).first()
    salida_hoy = db.query(models.Asistencia).filter(
        models.Asistencia.usuario_id == usuario.id,
        models.Asistencia.fecha == hoy,
        models.Asistencia.tipo == "Salida"
    ).first()

    # Si es docente y ya tiene entrada y no tiene salida → registra salida
    if usuario.rol == "Docente" and entrada_hoy and not salida_hoy:
        nueva = models.Asistencia(
            usuario_id=usuario.id,
            rol="Docente",
            tipo="Salida",
            fecha=hoy,
            hora=ahora.time().strftime("%H:%M:%S"),
            estado="Cumplió horario",
            aula_id=aula_id
        )
        db.add(nueva)
        VENTANAS_ACTIVAS.pop(aula_id, None)
        estudiantes_q = db.query(models.Usuario).filter(models.Usuario.rol == "Estudiante")
        if hasattr(models.Usuario, "aula_id") and aula_id is not None:
            estudiantes_q = estudiantes_q.filter(models.Usuario.aula_id == aula_id)
        estudiantes = estudiantes_q.all()
        for est in estudiantes:
            existe = db.query(models.Asistencia).filter(
                models.Asistencia.usuario_id == est.id,
                models.Asistencia.fecha == hoy,
                models.Asistencia.tipo == "Entrada"
            ).first()
            if not existe:
                db.add(models.Asistencia(
                    usuario_id=est.id,
                    rol="Estudiante",
                    tipo="Entrada",
                    fecha=hoy,
                    hora=ahora.time().strftime("%H:%M:%S"),
                    estado="Ausente",
                    aula_id=aula_id
                ))
        db.commit()
        db.refresh(nueva)
        return {"asistencia": {"id": nueva.id, "usuario_id": nueva.usuario_id, "rol": nueva.rol,
                               "tipo": nueva.tipo, "fecha": nueva.fecha, "hora": nueva.hora, "estado": nueva.estado}}

    # Control de duplicados de entrada
    if entrada_hoy:
        raise HTTPException(status_code=409, detail="Ya existe un registro de entrada para este usuario hoy")

    # Lógica de ventana y estado
    if usuario.rol == "Docente":
        # Abre ventana para estudiantes y fija tolerancia de tardanza
        VENTANAS_ACTIVAS[aula_id] = {
            "fin": ahora + timedelta(minutes=VENTANA_MIN),
            "tardanza": ahora + timedelta(minutes=TARDANZA_EST_MIN),
            "inicio": ahora
        }
        tipo = "Entrada"
        estado = "A tiempo"  # Docente siempre “A tiempo” al entrar
    elif usuario.rol == "Estudiante":
        ventana = VENTANAS_ACTIVAS.get(aula_id)
        if not ventana or ahora > ventana["fin"]:
            raise HTTPException(status_code=403, detail="Ventana de marcaje no activa(Profesor, faltante)")
        tipo = "Entrada"
        estado = "A tiempo" if ahora <= ventana["tardanza"] else "Tarde"
    else:
        raise HTTPException(status_code=403, detail="Rol no permitido")

    nueva = models.Asistencia(
        usuario_id=usuario.id,
        rol=usuario.rol,
        tipo=tipo,
        fecha=hoy,
        hora=ahora.time().strftime("%H:%M:%S"),
        estado=estado,
        aula_id=aula_id
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return {"asistencia": {
        "id": nueva.id, "usuario_id": nueva.usuario_id, "nombre": usuario.nombre,
        "cedula": usuario.cedula, "rol": nueva.rol, "tipo": nueva.tipo,
        "fecha": nueva.fecha, "hora": nueva.hora, "estado": nueva.estado
    }}

#----------------- MARCAR SALIDA PROFESOR Y ACTUALIZAR ESTUDIANTES AUSENTES ------------------
@app.post("/api/profesor/salida")
def marcar_salida_profesor(aula_id: int = Body(...), profesor_cedula: str = Body(...), db: Session = Depends(get_db)):
    profesor_q = db.query(models.Usuario).filter(
        models.Usuario.cedula == profesor_cedula,
        models.Usuario.rol == "Docente"
    )
    if hasattr(models.Usuario, "aula_id") and aula_id is not None:
        profesor_q = profesor_q.filter(models.Usuario.aula_id == aula_id)
    profesor = profesor_q.first()
    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")

    hoy = datetime.date.today().isoformat()
    salida_hoy = db.query(models.Asistencia).filter(
        models.Asistencia.usuario_id == profesor.id,
        models.Asistencia.fecha == hoy,
        models.Asistencia.tipo == "Salida"
    ).first()
    if salida_hoy:
        raise HTTPException(status_code=409, detail="Ya existe un registro de salida para este profesor hoy")

    ahora = datetime.datetime.now()

    # Registra la salida del profesor
    nueva = models.Asistencia(
        usuario_id=profesor.id,
        rol="Docente",
        tipo="Salida",
        fecha=ahora.date().isoformat(),
        hora=ahora.time().strftime("%H:%M:%S"),
        estado="Cumplió horario",
        aula_id=aula_id
    )
    db.add(nueva)

    # Marca como "Ausente" a los estudiantes del aula que no registraron entrada hoy
    hoy = ahora.date().isoformat()
    estudiantes_q = db.query(models.Usuario).filter(models.Usuario.rol == "Estudiante")
    if hasattr(models.Usuario, "aula_id") and aula_id is not None:
        estudiantes_q = estudiantes_q.filter(models.Usuario.aula_id == aula_id)
    estudiantes = estudiantes_q.all()
    for est in estudiantes:
        asistencia = db.query(models.Asistencia).filter(
            models.Asistencia.usuario_id == est.id,
            models.Asistencia.fecha == hoy,
            models.Asistencia.tipo == "Entrada"
        ).first()
        if not asistencia:
            nueva_ausente = models.Asistencia(
                usuario_id=est.id,
                rol="Estudiante",
                tipo="Entrada",
                fecha=hoy,
                hora=ahora.time().strftime("%H:%M:%S"),
                estado="Ausente",
                aula_id=aula_id
            )
            db.add(nueva_ausente)

    db.commit()
    return {"mensaje": "Salida registrada y estudiantes ausentes actualizados"}

#----------------- LISTAR ASISTENCIAS ------------------
@app.get("/api/asistencias")
def listar_asistencias(db: Session = Depends(get_db)):
    registros = (
        db.query(
            models.Asistencia.id,
            models.Asistencia.usuario_id,
            models.Usuario.nombre,
            models.Usuario.cedula,
            models.Usuario.rol,
            models.Usuario.grupo,
            models.Asistencia.aula_id,
            models.Aula.aula,
            models.Asistencia.tipo,
            models.Asistencia.fecha,
            models.Asistencia.hora,
            models.Asistencia.estado
        )
        .join(models.Usuario, models.Asistencia.usuario_id == models.Usuario.id)
        .outerjoin(models.Aula, models.Asistencia.aula_id == models.Aula.id)
        .all()
    )
    return {"asistencias": [
        {
            "id": r.id,
            "usuario_id": r.usuario_id,
            "nombre": r.nombre,
            "cedula": r.cedula,
            "rol": r.rol,
            "grupo": r.grupo,
            "aula_id": r.aula_id,
            "aula": r.aula,
            "tipo": r.tipo,
            "fecha": r.fecha,
            "hora": r.hora,
            "estado": r.estado
        }
        for r in registros
    ]}

@app.delete("/api/asistencias/all")
def eliminar_todos_registros(db: Session = Depends(get_db)):
    db.query(models.Asistencia).delete()
    db.query(models.Justificante).delete()
    db.commit()
    return {"success": True, "mensaje": "Todos los registros eliminados"}

class AsistenciaUpdate(BaseModel):
    estado: str | None = None

@app.patch("/api/asistencias/{id}")
def actualizar_asistencia(id: int = Path(...), body: AsistenciaUpdate = Body(...), db: Session = Depends(get_db)):
    reg = db.query(models.Asistencia).filter(models.Asistencia.id == id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Asistencia no encontrada")
    if body.estado:
        reg.estado = body.estado
    db.commit()
    db.refresh(reg)
    return {"asistencia": {
        "id": reg.id, "usuario_id": reg.usuario_id, "rol": reg.rol,
        "tipo": reg.tipo, "fecha": reg.fecha, "hora": reg.hora, "estado": reg.estado
    }}

#----------------- LISTAR JUSTIFICANTES ------------------
@app.get("/api/justificantes")
def listar_justificantes(db: Session = Depends(get_db)):
    from models import Justificante, Usuario
    justs = (
        db.query(Justificante, Usuario)
        .join(Usuario, Justificante.usuario_id == Usuario.id)
        .all()
    )
    return {"justificantes": [
        {
            "id": j.id,
            "asistencia_id": j.asistencia_id,
            "usuario_id": j.usuario_id,
            "nombre": u.nombre,  # <-- nombre del estudiante
            "fecha_registro": str(j.fecha_registro),
            "fecha_documento": str(j.fecha_documento),
            "motivo": j.motivo
        } for j, u in justs
    ]}

from pydantic import BaseModel


# ------------------ CREAR JUSTIFICANTE ------------------
class JustificanteCreate(BaseModel):
    asistencia_id: int
    usuario_id: int
    fecha_registro: str
    fecha_documento: str
    motivo: str

@app.post("/api/justificantes")
def crear_justificante(body: JustificanteCreate, db: Session = Depends(get_db)):
    nuevo = models.Justificante(
        asistencia_id=body.asistencia_id,
        usuario_id=body.usuario_id,
        fecha_registro=body.fecha_registro,
        fecha_documento=body.fecha_documento,
        motivo=body.motivo
    )
    db.add(nuevo)
    # Actualiza el estado de la asistencia a "Justificado"
    asistencia = db.query(models.Asistencia).filter(models.Asistencia.id == body.asistencia_id).first()
    if asistencia:
        asistencia.estado = "Justificado"
    db.commit()
    db.refresh(nuevo)
    return {"justificante": {
        "id": nuevo.id,
        "asistencia_id": nuevo.asistencia_id,
        "usuario_id": nuevo.usuario_id,
        "fecha_registro": str(nuevo.fecha_registro),
        "fecha_documento": str(nuevo.fecha_documento),
        "motivo": nuevo.motivo
    }}

@app.get("/api/justificantes/{justificante_id}")
def ver_justificante(justificante_id: int, db: Session = Depends(get_db)):
    j = db.query(models.Justificante).filter(models.Justificante.id == justificante_id).first()
    if not j:
        raise HTTPException(status_code=404, detail="Justificante no encontrado")
    # Si usas JOIN para nombre y rol, inclúyelos aquí
    usuario = db.query(models.Usuario).filter(models.Usuario.id == j.usuario_id).first()
    return {
        "id": j.id,
        "asistencia_id": j.asistencia_id,
        "usuario_id": j.usuario_id,
        "nombre": usuario.nombre if usuario else "",
        "rol": usuario.rol if usuario else "",
        "fecha_registro": str(j.fecha_registro),
        "fecha_documento": str(j.fecha_documento),
        "motivo": j.motivo,
        "referencia": j.referencia,
        "archivo_nombre": j.archivo_nombre,
        "archivo_url": j.archivo_url
    }

@app.delete("/api/justificantes/{justificante_id}")
def eliminar_justificante(justificante_id: int, db: Session = Depends(get_db)):
    j = db.query(models.Justificante).filter(models.Justificante.id == justificante_id).first()
    if not j:
        raise HTTPException(status_code=404, detail="Justificante no encontrado")
    db.delete(j)
    db.commit()
    return {"ok": True}

@app.get("/api/usuarios/{usuario_id}")
def ver_usuario(usuario_id: int, db: Session = Depends(get_db)):
    u = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {
        "id": u.id,
        "nombre": u.nombre,
        "cedula": u.cedula,
        "rol": u.rol,
        "grupo": u.grupo,
        "correo": u.correo,
        "activo": u.activo
    }

# --------- Estado simple para la ESP32 ----------
LAST_RESULT = {
    "estado": "advertencia",
    "mensaje": "Esperando QR"
}

@app.get("/api/resultado")
def resultado_esp32():
    """
    Devuelve el último resultado para la ESP32.
    Nota: este estado es in-memory. Puedes actualizarlo desde otro proceso si lo necesitas.
    """
    return {
        "estado": LAST_RESULT.get("estado", "advertencia"),
        "mensaje": LAST_RESULT.get("mensaje", "Esperando QR")
    }

# (Opcional) Endpoint para actualizar manualmente el estado desde pruebas
class ResultadoSet(BaseModel):
    estado: str
    mensaje: str | None = None

@app.post("/api/resultado")
def set_resultado_esp32(body: ResultadoSet):
    """
    Permite fijar el estado que leerá la ESP32.
    No afecta la lógica de asistencias existente.
    """
    LAST_RESULT["estado"] = body.estado
    if body.mensaje is not None:
        LAST_RESULT["mensaje"] = body.mensaje
    return {"ok": True, "estado": LAST_RESULT}

