/**
 * AulasAPI — CRUD de aulas y dispositivos IoT
 *
 * Propósito:
 * - Gestionar la colección de aulas (código, device, estado) sobre SimDB,
 *   exponiendo operaciones como Promesas.
 *
 * Métodos:
 * - listar({search?}) -> Promise<Aula[]>
 * - crear(aulaItem) -> Promise<Aula>
 * - actualizar(id, aulaItem) -> Promise<Aula>
 * - eliminar(id) -> Promise<{ok:true}>
 *
 * Notas:
 * - El parámetro search filtra por aula o device (toLowerCase).
 */
(function(){
  const db = window.SimDB, api = window.SimAPI;

  window.AulasAPI = {
    async listar({search}={}){ await api.delay(); let a = db.getAulas(); if(search){ const s=search.toLowerCase(); a = a.filter(x=>x.aula.toLowerCase().includes(s)||x.device.toLowerCase().includes(s)); } return a; },
    async crear(item){ await api.delay(); const ni = Object.assign({id: api.id('a')}, item); db.setAulas([...db.getAulas(), ni]); return ni; },
    async actualizar(id, item){ await api.delay(); const aulas=db.getAulas(); const i=aulas.findIndex(x=>x.id===id); if(i===-1) throw new Error('Aula no encontrada'); aulas[i]=Object.assign({id}, item); db.setAulas(aulas); return aulas[i]; },
    async eliminar(id){ await api.delay(); db.setAulas(db.getAulas().filter(x=>x.id!==id)); return {ok:true}; }
  };
})();