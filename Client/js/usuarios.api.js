/**
 * UsuariosAPI — CRUD de usuarios de la plataforma
 *
 * Propósito:
 * - Abstraer operaciones de usuarios sobre SimDB (localStorage) y devolver Promesas
 *   para simular un backend.
 *
 * Métodos:
 * - listar({search?}) -> Promise<Usuario[]>
 * - crear(user) -> Promise<Usuario>
 * - actualizar(id, user) -> Promise<Usuario>
 * - eliminar(id) -> Promise<{ok:true}>
 * - validarCedula(c) -> boolean (formato Panamá X-XXXX-XXXX)
 *
 * Notas:
 * - El parámetro search filtra por nombre o cédula (toLowerCase).
 */
(function(){
  const db = window.SimDB, api = window.SimAPI;
  const cedulaRegex = /^[1-9]-\d{4}-\d{4}$/;

  window.UsuariosAPI = {
    validarCedula(c){ return cedulaRegex.test(c); },
    async listar({search}={}){ await api.delay(); let users = db.getUsers(); if(search){ const s=search.toLowerCase(); users = users.filter(u=>u.nombre.toLowerCase().includes(s)||u.cedula.toLowerCase().includes(s)); } return users; },
    async crear(u){ await api.delay(); const nu = Object.assign({id: api.id('u')}, u); const all=[...db.getUsers(), nu]; db.setUsers(all); return nu; },
    async actualizar(id, u){ await api.delay(); const users=db.getUsers(); const i=users.findIndex(x=>x.id===id); if(i===-1) throw new Error('Usuario no encontrado'); users[i]=Object.assign({id}, u); db.setUsers(users); return users[i]; },
    async eliminar(id){ await api.delay(); db.setUsers(db.getUsers().filter(x=>x.id!==id)); return {ok:true}; }
  };
})();