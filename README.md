# ProyectoSof8 — Backend simulado (demo)

Este proyecto es una demo de frontend (HTML/CSS/JS) que usa **LocalStorage** como backend simulado.
Se añadieron módulos JavaScript en `HTML/js/` que actúan como APIs para cada página.
La idea es que, más adelante, se reemplacen estas funciones por llamadas HTTP reales (fetch/axios) manteniendo los mismos contratos.

## Módulos

- **simdb.js** (base común)
  - Colecciones: `regs`, `justs`, `users`, `aulas`, `session`.
  - `SimDB`: getters/setters para cada colección.
  - `SimAPI`: `delay(ms)`, `id(prefix)`, `cedula()`.
  - Si no hay datos, siembra registros de ejemplo.

- **asistencias.api.js**
  - Operaciones sobre asistencias y justificantes.
  - `listRegistros({rol?, estado?, search?})`
  - `createRegistro(reg)`, `updateRegistro(id, patch)`
  - `listJustificantes()`, `getJustificante(id)`, `createJustificante(just)`, `deleteJustificante(id)`
  - `makeCSVAll()/makeCSVEst()/makeCSVDoc()`

- **usuarios.api.js**
  - CRUD de usuarios.
  - `listar({search?})`, `crear(user)`, `actualizar(id, user)`, `eliminar(id)`
  - `validarCedula(c)` (formato Panamá `X-XXXX-XXXX`).

- **aulas.api.js**
  - CRUD de aulas/dispositivos.
  - `listar({search?})`, `crear(item)`, `actualizar(id, item)`, `eliminar(id)`

- **auth.api.js**
  - Autenticación simulada.
  - `login(usuario, contrasena)` → sesión `{token, usuario, role, at}`
  - `logout()`, `getSession()`

- **dashboard.api.js**
  - Resumen del día para el dashboard.
  - `resumenDelDia()` → `{ total, entradas, salidas, puntualidad }`

- **index.api.js**
  - Stub de la portada; utilidad `info()`.

## Uso típico

```js
// Asistencias
const regs = await AsistenciasAPI.listRegistros({ rol: 'Estudiante' });
await AsistenciasAPI.createRegistro({ nombre, cedula, rol:'Estudiante', aula, tipo:'Entrada', estado:'A tiempo' });

// Usuarios
if (!UsuariosAPI.validarCedula(cedula)) alert('Cédula inválida');
const nuevos = await UsuariosAPI.listar({ search: 'jeremy' });

// Aulas
await AulasAPI.crear({ aula:'3-301', device:'ESP-301-C', estado:'Activo' });

// Auth
const session = await AuthAPI.login('admin@utp', '123456');
await AuthAPI.logout();

// Dashboard
const r = await DashboardAPI.resumenDelDia();
```

## Login de prueba (guía rápida)

Para validar el flujo de autenticación con el backend simulado, el login acepta dos usuarios de prueba:

- Administrador: `admin@utp` / `123456`
- Docente: `prof@utp` / `654321`

Comportamiento:
- En `HTML/js/auth.api.js`, el método `login(usuario, contrasena)` verifica estas credenciales fijas y asigna el rol correspondiente.
- En caso de éxito, se guarda la sesión en LocalStorage (`session`) y se redirige a `dashboard.html`.
- En caso de error, se muestra un mensaje indicando que las credenciales son inválidas.

Notas de UI:
- En `HTML/login.html`, el botón “Ingresar” llama a `AuthAPI.login` y maneja el redireccionamiento.
- El campo de contraseña incluye un botón para mostrar/ocultar (ícono ojo/oj o-tachado).
- El logo institucional se carga desde `img/Log.utp.png`. Dado que `login.html` está en `HTML/`, la ruta correcta es `../img/Log.utp.png`.


## Conexión a backend real

- Mantén los **nombres y firmas** de las funciones en cada `*.api.js`.
- Dentro de cada método, reemplaza el acceso a `SimDB` por `fetch()` hacia tus endpoints.
- Respeta la forma del JSON indicado en los contratos para minimizar cambios en el frontend.

## Notas

- En sistemas Linux, los nombres de archivos son **case-sensitive**. Asegura que los enlaces en HTML coincidan exactamente con los nombres de archivo.
- Para limpiar datos de demo, borra las claves en LocalStorage: `regs`, `justs`, `users`, `aulas`, `session` (desde DevTools).

## Diseño de Base de Datos (propuesta)

Esta sección describe un esquema relacional básico para implementar el backend real. Puedes usar MySQL/PostgreSQL/SQL Server. Incluye tablas, relaciones, tipos sugeridos e índices.

### Entidades principales

1) Usuarios (`usuarios`)
- Campos:
  - `id` (PK, UUID/INT AUTO)
  - `nombre` (VARCHAR(100), NOT NULL)
  - `cedula` (VARCHAR(11), UNIQUE, NOT NULL) — formato Panamá `X-XXXX-XXXX`
  - `rol` (ENUM('Estudiante','Docente','Administrador'), NOT NULL)
  - `grupo` (VARCHAR(20), NULL) — para estudiantes, ej. `1GS123`
  - `correo` (VARCHAR(120), NULL, UNIQUE opcional)
  - `activo` (BOOLEAN, DEFAULT TRUE)
  - `created_at` (TIMESTAMP, DEFAULT NOW)

2) Aulas/Dispositivos (`aulas`)
- Campos:
  - `id` (PK, UUID/INT AUTO)
  - `aula` (VARCHAR(10), NOT NULL) — ej. `3-105`
  - `edificio` (SMALLINT, NOT NULL) — 1/2/3, derivado del prefijo del aula
  - `device_id` (VARCHAR(50), UNIQUE, NOT NULL) — ej. `ESP-105-A`
  - `estado` (ENUM('Activo','Desconectado'), NOT NULL)
  - `created_at` (TIMESTAMP, DEFAULT NOW)

3) Asistencias (`asistencias`)
- Campos:
  - `id` (PK, UUID/INT AUTO)
  - `usuario_id` (FK → `usuarios.id`, NOT NULL)
  - `rol` (ENUM('Estudiante','Docente'), NOT NULL) — redundante para facilidad de reportes
  - `curso` (VARCHAR(20), NULL) — solo para estudiantes
  - `aula_id` (FK → `aulas.id`, NULL) — dónde se registró
  - `tipo` (ENUM('Entrada','Salida'), NOT NULL)
  - `fecha` (DATE, NOT NULL)
  - `hora` (TIME, NOT NULL)
  - `estado` (ENUM('A tiempo','Tarde','Ausente','Justificado','Cumplió horario'), NOT NULL)
  - `created_at` (TIMESTAMP, DEFAULT NOW)

4) Justificantes (`justificantes`)
- Campos:
  - `id` (PK, UUID/INT AUTO)
  - `asistencia_id` (FK → `asistencias.id`, NOT NULL)
  - `usuario_id` (FK → `usuarios.id`, NOT NULL)
  - `fecha_registro` (DATE, NOT NULL) — fecha del registro al que aplica
  - `fecha_documento` (DATE, NOT NULL)
  - `motivo` (TEXT, NOT NULL)
  - `referencia` (VARCHAR(50), NULL) — número de acta u otra referencia
  - `archivo_nombre` (VARCHAR(200), NULL)
  - `archivo_url` (VARCHAR(500), NULL) — URL en almacenamiento (S3/Azure Blob/serv. estático)
  - `created_at` (TIMESTAMP, DEFAULT NOW)

5) Sesiones/Tokens (opcional) (`sesiones`)
- Campos:
  - `id` (PK)
  - `usuario_id` (FK → `usuarios.id`)
  - `token` (VARCHAR(200), UNIQUE)
  - `rol` (ENUM)
  - `expires_at` (TIMESTAMP)

### Relaciones
- `asistencias.usuario_id` → `usuarios.id` (N:1)
- `asistencias.aula_id` → `aulas.id` (N:1)
- `justificantes.asistencia_id` → `asistencias.id` (N:1)
- `justificantes.usuario_id` → `usuarios.id` (N:1)

### Índices recomendados
- `usuarios(cedula)` — UNIQUE
- `aulas(device_id)` — UNIQUE
- `asistencias(usuario_id, fecha)` — consultas por día/usuario
- `asistencias(aula_id, fecha)` — consultas por aula/fecha
- `asistencias(estado)` — filtros por estado
- `justificantes(asistencia_id)`

### Ejemplo SQL (MySQL)

```sql
CREATE TABLE usuarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  cedula VARCHAR(11) NOT NULL UNIQUE,
  rol ENUM('Estudiante','Docente','Administrador') NOT NULL,
  grupo VARCHAR(20) NULL,
  correo VARCHAR(120) NULL,
  activo BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE aulas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  aula VARCHAR(10) NOT NULL,
  edificio SMALLINT NOT NULL,
  device_id VARCHAR(50) NOT NULL UNIQUE,
  estado ENUM('Activo','Desconectado') NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE asistencias (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id INT NOT NULL,
  rol ENUM('Estudiante','Docente') NOT NULL,
  curso VARCHAR(20) NULL,
  aula_id INT NULL,
  tipo ENUM('Entrada','Salida') NOT NULL,
  fecha DATE NOT NULL,
  hora TIME NOT NULL,
  estado ENUM('A tiempo','Tarde','Ausente','Justificado','Cumplió horario') NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
  FOREIGN KEY (aula_id) REFERENCES aulas(id)
);

CREATE TABLE justificantes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  asistencia_id INT NOT NULL,
  usuario_id INT NOT NULL,
  fecha_registro DATE NOT NULL,
  fecha_documento DATE NOT NULL,
  motivo TEXT NOT NULL,
  referencia VARCHAR(50) NULL,
  archivo_nombre VARCHAR(200) NULL,
  archivo_url VARCHAR(500) NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (asistencia_id) REFERENCES asistencias(id),
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);
```

### Consideraciones de backend
- Autenticación: JWT con expiración y roles en el token; refresco opcional.
- Subida de archivos: almacenar en blob (S3/Azure/Drive on-prem) y guardar `archivo_url`.
- Validaciones:
  - Cédula: regex `^[1-9]-\d{4}-\d{4}$`.
  - Aula: formato `E-XXX` (Edificio-NumAula) y derivar `edificio`.
  - Estado: restringir a los enumerados.
- Auditoría: opcional `updated_at`, `updated_by` y logs de cambios.
- Paginación: en listados grandes (asistencias/justificantes).

### API REST (resumen rápido)
- `GET /usuarios?search=...`
- `POST /usuarios` / `PUT /usuarios/:id` / `DELETE /usuarios/:id`
- `GET /aulas?search=&edificio=`
- `POST /aulas` / `PUT /aulas/:id` / `DELETE /aulas/:id`
- `GET /asistencias?rol=&estado=&fecha=&aula_id=&usuario_id=`
- `POST /asistencias` / `PUT /asistencias/:id`
- `GET /justificantes?usuario_id=&fecha=`
- `POST /justificantes` / `DELETE /justificantes/:id`
- `POST /auth/login` / `POST /auth/logout` / `GET /auth/session`

Con este esquema podrás construir el backend real y mapear fácilmente las llamadas desde los archivos `*.api.js` que ya creamos.
