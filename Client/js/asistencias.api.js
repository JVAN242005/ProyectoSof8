/**
 * AsistenciasAPI — Operaciones sobre registros de asistencia y justificantes
 *
 * Propósito:
 * - Centralizar la lógica de lectura/escritura de asistencias (regs) y justificantes (justs)
 *   usando SimDB y retornando Promesas para simular llamadas a un backend.
 *
 * Métodos principales:
 * - listRegistros({rol?, estado?, search?}) -> Promise<Registro[]>
 * - createRegistro(reg) -> Promise<Registro>
 * - updateRegistro(id, patch) -> Promise<Registro>
 * - listJustificantes() -> Promise<Justificante[]>
 * - getJustificante(id) -> Promise<Justificante|null>
 * - createJustificante(just) -> Promise<Justificante>
 * - deleteJustificante(id) -> Promise<{ok:true}>
 * - makeCSVAll()/makeCSVEst()/makeCSVDoc() -> string CSV
 *
 * Notas:
 * - Al crear un justificante con regId, se actualiza el estado del registro a "Justificado".
 * - La latencia simulada se aplica con SimAPI.delay().
 */
(function(){
  const db = window.SimDB, api = window.SimAPI;
  const API_URL = "http://localhost:8000/api";
  const API_URL_QR = "http://10.92.255.218:8000/api/asistencias/qr";  // Cambia por tu IP real

  // Función para convertir registros a CSV
  function csvString(rows, keys){
    return [keys.join(',')].concat(
      rows.map(r => keys.map(k => `"${(((r[k]||'')+'').toString()).replace(/"/g,'""')}"`).join(','))
    ).join('\n');
  }

  // API para consumir el backend real
  window.AsistenciasAPI = {
    // Listar asistencias con JOIN
    async listRegistros({rol, estado, search}={}) {
      const res = await fetch(`${API_URL}/asistencias`);
      const data = await res.json();
      let regs = data.asistencias || [];
      if (rol) regs = regs.filter(r => r.rol === rol);
      if (estado) regs = regs.filter(r => r.estado === estado);
      if (search) {
        const s = search.toLowerCase();
        regs = regs.filter(r => (r.nombre||'').toLowerCase().includes(s) || (r.cedula||'').toLowerCase().includes(s));
      }
      return regs;
    },

    // Actualizar estado de asistencia
    async updateRegistro(id, patch) {
      const res = await fetch(`${API_URL}/asistencias/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(patch)
      });
      if (!res.ok) throw new Error("No se pudo actualizar");
      return await res.json();
    },

    // Listar justificantes
    async listJustificantes() {
      const res = await fetch(`${API_URL}/justificantes`);
      if (!res.ok) throw new Error("Error al listar justificantes");
      return (await res.json()).justificantes;
    },

    // Obtener justificante por ID
    async getJustificante(id) {
      const res = await fetch(`${API_URL}/justificantes/${id}`);
      if (!res.ok) throw new Error("No se encontró el justificante");
      return await res.json();
    },

    // Crear justificante
    async createJustificante(just) {
      const res = await fetch(`${API_URL}/justificantes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(just)
      });
      if (!res.ok) throw new Error("No se pudo crear justificante");
      return await res.json();
    },

    // Eliminar justificante por ID
    async deleteJustificante(id) {
      const res = await fetch(`${API_URL}/justificantes/${id}`, { method: "DELETE" });
      if (!res.ok) throw new Error("No se pudo eliminar el justificante");
      return await res.json();
    },

    // Eliminar todos los registros de asistencias y justificantes
    async deleteAllRegistros() {
      const res = await fetch(`${API_URL}/asistencias/all`, {
        method: "DELETE"
      });
      if (!res.ok) throw new Error("No se pudo eliminar");
      return await res.json();
    },

    // Exportar CSV usando los datos del backend
    async makeCSVAll() {
      const regs = await this.listRegistros();
      const keys=['nombre','cedula','rol','grupo','aula_id','tipo','fecha','hora','estado'];
      return csvString(regs, keys);
    },
    async makeCSVEst() {
      const regs = await this.listRegistros({rol:'Estudiante'});
      const keys=['nombre','cedula','grupo','aula_id','tipo','fecha','hora','estado'];
      return csvString(regs, keys);
    },
    async makeCSVDoc() {
      const regs = await this.listRegistros({rol:'Docente'});
      const keys=['nombre','cedula','aula_id','tipo','fecha','hora','estado'];
      return csvString(regs, keys);
    },

    // Marcar asistencia por QR
    async marcarQR(qrTexto) {
      try {
        const res = await fetch(API_URL_QR, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ qr_texto: qrTexto })
        });
        if (!res.ok) {
          const error = await res.json();
          alert(error.detail || "Error al registrar asistencia");
          return;
        }
        alert("Asistencia registrada correctamente");
        renderAllTables();
      } catch (e) {
        alert("Error de conexión con el servidor");
      }
    }
  };
})();