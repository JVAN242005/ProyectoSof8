/**
 * AuthAPI — Autenticación simulada
 *
 * Propósito:
 * - Simular login/logout y manejo de sesión en localStorage.
 * - No valida credenciales reales; asigna un rol heurístico y genera un token.
 *
 * Métodos:
 * - login(usuario, contrasena) -> Promise<Sesion>
 * - logout() -> Promise<{ok:true}>
 * - getSession() -> Sesion|null
 */
(function(){
  const db = window.SimDB, api = window.SimAPI;

  window.AuthAPI = {
    async login(usuario, contrasena){
      await api.delay();
      // Modo prueba: validar dos usuarios fijos
      const USERS = [
        { user:'admin@utp', pass:'123456', role:'Administrador' },
        { user:'prof@utp',  pass:'654321', role:'Docente' }
      ];
      const u = (usuario||'').trim().toLowerCase();
      const hit = USERS.find(x => x.user === u && x.pass === (contrasena||''));
      if (hit){
        const session = { token: api.id('t'), usuario: hit.user, role: hit.role, at: Date.now() };
        db.setSession(session);
        return session;
      }
      // Si no coincide, no iniciar sesión
      throw new Error('Credenciales inválidas');
    },
    async logout(){ await api.delay(); db.clearSession(); return {ok:true}; },
    getSession(){ return db.getSession(); }
  };
})();