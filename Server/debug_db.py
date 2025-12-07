import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import traceback

print("=" * 50)
print("🔍 DIAGNÓSTICO DE CONEXIÓN MYSQL")
print("=" * 50)

# 1. PRIMERO: Probar conexión DIRECTA con pymysql
print("\n1. Probando conexión DIRECTA con pymysql...")
try:
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='1234',
        database='asistencia',
        port=3306
    )
    print("   ✅ pymysql conectado correctamente")
    
    # Verificar base de datos
    with conn.cursor() as cursor:
        cursor.execute("SELECT DATABASE()")
        db = cursor.fetchone()[0]
        print(f"   📁 Base de datos: {db}")
        
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"   📊 Tablas en la BD: {len(tables)}")
        for table in tables:
            print(f"      - {table[0]}")
    
    conn.close()
except Exception as e:
    print(f"   ❌ Error pymysql: {e}")
    print(f"   🔍 Detalle: {traceback.format_exc()}")

# 2. SEGUNDO: Probar conexión SQLAlchemy
print("\n2. Probando conexión SQLAlchemy...")
try:
    DATABASE_URL = "mysql+pymysql://root:1234@localhost:3306/Asistencia?charset=utf8mb4"
    print(f"   URL usada: {DATABASE_URL}")
    
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("   ✅ SQLAlchemy conectado")
        
        # Probar query simple
        result = conn.execute(text("SELECT 1 as test, DATABASE() as db, USER() as user"))
        row = result.fetchone()
        print(f"   📋 Test query: test={row[0]}, db={row[1]}, user={row[2]}")
        
except SQLAlchemyError as e:
    print(f"   ❌ Error SQLAlchemy: {e}")
    print(f"   🔍 Detalle SQLAlchemy: {traceback.format_exc()}")
except Exception as e:
    print(f"   ❌ Error general: {e}")
    print(f"   🔍 Detalle completo: {traceback.format_exc()}")

# 3. TERCERO: Verificar si la BD existe
print("\n3. Verificando existencia de base de datos...")
try:
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='1234',
        port=3306
    )
    
    with conn.cursor() as cursor:
        cursor.execute("SHOW DATABASES")
        databases = [db[0] for db in cursor.fetchall()]
        
        if 'Asistencia' in databases:
            print("   ✅ Base de datos 'Asistencia' EXISTE")
        else:
            print("   ❌ Base de datos 'Asistencia' NO EXISTE")
            print("   💡 Creando base de datos...")
            cursor.execute("CREATE DATABASE Asistencia")
            print("   ✅ Base de datos creada")
    
    conn.close()
except Exception as e:
    print(f"   ❌ Error verificando BD: {e}")

print("\n" + "=" * 50)
print("🎯 RECOMENDACIONES BASADAS EN RESULTADOS")
print("=" * 50)