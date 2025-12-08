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
  const API_URL = 'http://localhost:8000/api/usuarios';

  window.UsuariosAPI = {
    validarCedula(c){ return cedulaRegex.test(c); },
    async listar({search}={}){ 
      let url = API_URL;
      if (search) url += `?search=${encodeURIComponent(search)}`;
      const res = await fetch(url);
      if (!res.ok) throw new Error('Error al obtener usuarios');
      // Si tu backend responde {usuarios: [...]}, usa .usuarios; si no, usa el array directo
      const data = await res.json();
      return data.usuarios || data;
    },
    async crear(u){ 
      const res = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(u)
      });
      if (!res.ok) throw new Error('Error al crear usuario');
      return await res.json();
    },
    async actualizar(id, u){ 
      const res = await fetch(`${API_URL}/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(u)
      });
      if (!res.ok) throw new Error('Error al actualizar usuario');
      return await res.json();
    },
    async eliminar(id){ 
      const res = await fetch(`${API_URL}/${id}`, {
        method: 'DELETE'
      });
      if (!res.ok) throw new Error('Error al eliminar usuario');
      return await res.json();
    }
  };
})();