# Proyecto Cliente/Servidor con Hardware 

el proyecto para lanzarse de necesita tener:
- python 3.8.x o superiores
- Extension de python 

--------------------- 

Comando de ejecucion en la ubicación: PROYECTOSOF8/Server/

py -m uvicorn main:app --reload


---------------------

Algunos Endpoints para la verificacion: 

- verificación de la base de datos
http://localhost:8000/api/status

- lista de usuarios
http://localhost:8000/api/usuarios

- Enviar datos procesados por el QR para la asistencia 
http://localhost:8000/api/asistencias/qr


----------------------

Documentacion de la APIs(Swagger):

http://localhost:8000/docs#/



----------------------

# Base de datos Query:

CREATE DATABASE IF NOT EXISTS Asistencia;
USE Asistencia;
-- ============================================
-- TABLA: usuarios
-- Almacena estudiantes, docentes y administradores
-- ============================================
CREATE TABLE usuarios (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  nombre        VARCHAR(100) NOT NULL,
  cedula        VARCHAR(11) NOT NULL UNIQUE,
  rol           ENUM('Estudiante','Docente','Administrador') NOT NULL,
  grupo         VARCHAR(20) NULL,
  correo        VARCHAR(120) NULL UNIQUE,
  password      VARCHAR(255) NULL,
  activo        BOOLEAN DEFAULT TRUE,
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  INDEX idx_cedula (cedula),
  INDEX idx_rol (rol)
);

-- ============================================
-- TABLA: aulas
-- Dispositivos ESP32 y ubicaciones físicas
-- ============================================
CREATE TABLE aulas (
  id                INT AUTO_INCREMENT PRIMARY KEY,
  aula              VARCHAR(10) NOT NULL,
  edificio          SMALLINT NOT NULL,
  device_id         VARCHAR(50) NOT NULL UNIQUE,
  estado            ENUM('Activo','Desconectado') DEFAULT 'Activo',
  ultima_conexion   TIMESTAMP NULL,
  created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  INDEX idx_device (device_id)
);

-- ============================================
-- TABLA: asistencias
-- Registros de entrada/salida
-- ============================================
CREATE TABLE asistencias (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id    INT NOT NULL,
  rol           ENUM('Estudiante','Docente') NOT NULL,
  curso         VARCHAR(20) NULL,
  aula_id       INT NULL,
  tipo          ENUM('Entrada','Salida') NOT NULL,
  fecha         DATE NOT NULL,
  hora          TIME NOT NULL,
  estado        ENUM('A tiempo','Tarde','Ausente','Justificado','Cumplió horario') NOT NULL,
  device_id     VARCHAR(50) NULL,
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
  FOREIGN KEY (aula_id) REFERENCES aulas(id) ON DELETE SET NULL,
  
  INDEX idx_usuario_fecha (usuario_id, fecha),
  INDEX idx_fecha (fecha)
);

-- ============================================
-- TABLA: justificantes
-- Excusas médicas/administrativas
-- ============================================
CREATE TABLE justificantes (
  id                INT AUTO_INCREMENT PRIMARY KEY,
  asistencia_id     INT NOT NULL,
  usuario_id        INT NOT NULL,
  fecha_registro    DATE NOT NULL,
  fecha_documento   DATE NOT NULL,
  motivo            TEXT NOT NULL,
  referencia        VARCHAR(50) NULL,
  archivo_nombre    VARCHAR(200) NULL,
  archivo_url       VARCHAR(500) NULL,
  archivo_mime      VARCHAR(50) NULL,
  created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (asistencia_id) REFERENCES asistencias(id) ON DELETE CASCADE,
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
  
  INDEX idx_asistencia (asistencia_id)
);
