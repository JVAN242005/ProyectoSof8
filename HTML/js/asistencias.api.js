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

  function csvString(rows, keys){
    return [keys.join(',')].concat(
      rows.map(r => keys.map(k => `"${(((r[k]||'')+'').toString()).replace(/"/g,'""')}"`).join(','))
    ).join('\n');
  }

  window.AsistenciasAPI = {
    async listRegistros({rol, estado, search}={}){
      await api.delay();
      let regs = db.getRegs();
      if(rol) regs = regs.filter(r=>r.rol===rol);
      if(estado) regs = regs.filter(r=>r.estado===estado);
      if(search){
        const s = search.toLowerCase();
        regs = regs.filter(r => (r.nombre||'').toLowerCase().includes(s) || (r.cedula||'').toLowerCase().includes(s));
      }
      return regs;
    },
    async createRegistro(reg){
      await api.delay();
      const r = Object.assign({ id: api.id('r'), fecha: new Date().toISOString().slice(0,10), hora: new Date().toTimeString().slice(0,5) }, reg);
      db.setRegs([r, ...db.getRegs()]);
      return r;
    },
    async updateRegistro(id, patch){
      await api.delay();
      const regs = db.getRegs();
      const i = regs.findIndex(x=>x.id===id);
      if(i===-1) throw new Error('Registro no encontrado');
      regs[i] = Object.assign({}, regs[i], patch);
      db.setRegs(regs);
      return regs[i];
    },
    async listJustificantes(){ await api.delay(); return db.getJusts(); },
    async getJustificante(id){ await api.delay(); return db.getJusts().find(x=>x.id===id)||null; },
    async createJustificante(just){
      await api.delay();
      const j = Object.assign({ id: api.id('j'), created: new Date().toISOString() }, just);
      db.setJusts([j, ...db.getJusts()]);
      if(j.regId){
        const regs = db.getRegs();
        const i = regs.findIndex(x=>x.id===j.regId);
        if(i!==-1){ regs[i].estado = 'Justificado'; db.setRegs(regs); }
      }
      return j;
    },
    async deleteJustificante(id){ await api.delay(); db.setJusts(db.getJusts().filter(x=>x.id!==id)); return {ok:true}; },
    makeCSVAll(){ const keys=['nombre','cedula','rol','curso','aula','tipo','fecha','hora','estado']; return csvString(db.getRegs(), keys); },
    makeCSVEst(){ const keys=['nombre','cedula','curso','aula','tipo','fecha','hora','estado']; return csvString(db.getRegs().filter(r=>r.rol==='Estudiante'), keys); },
    makeCSVDoc(){ const keys=['nombre','cedula','aula','tipo','fecha','hora','estado']; return csvString(db.getRegs().filter(r=>r.rol==='Docente'), keys); }
  };
})();