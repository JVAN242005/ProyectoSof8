/**
 * SimDB y SimAPI — Backend simulado en el navegador (LocalStorage)
 *
 * Propósito:
 * - Proveer colecciones en localStorage: regs (asistencias), justs (justificantes),
 *   users (usuarios), aulas (aulas/dispositivos) y session (sesión del usuario).
 * - Ofrecer utilidades de simulación a través de SimAPI: delay(ms), id(prefix), cedula().
 * - Sembrar datos iniciales si no existen.
 *
 * Colecciones:
 * - SimDB.getRegs()/setRegs(arr)
 * - SimDB.getJusts()/setJusts(arr)
 * - SimDB.getUsers()/setUsers(arr)
 * - SimDB.getAulas()/setAulas(arr)
 * - SimDB.getSession()/setSession(obj)/clearSession()
 *
 * Uso típico:
 *   const regs = SimDB.getRegs();
 *   SimDB.setRegs([{...}, ...regs]);
 *   await SimAPI.delay(250); // simular latencia
 *
 * Nota:
 * - Este módulo no hace llamadas HTTP; sirve como backend local.
 * - Para conectar un backend real, reemplace las funciones en los archivos *.api.js por fetch/axios.
 */
(function(){
  const KEYS = { regs:'regs', justs:'justs', users:'users', aulas:'aulas', session:'session' };

  function read(key){ try { return JSON.parse(localStorage.getItem(key) || '[]'); } catch(_) { return []; } }
  function write(key, val){ localStorage.setItem(key, JSON.stringify(val)); }

  function newId(prefix='id'){ return prefix + Date.now() + Math.floor(Math.random()*1000); }
  // Formato Panamá: X-XXXX-XXXX (X=1-9, bloques con 4 dígitos)
  function generateCedula(){
    const d = String(Math.floor(Math.random()*9)+1); // 1-9
    const part4 = () => String(Math.floor(Math.random()*10000)).padStart(4,'0'); // 0000-9999
    return `${d}-${part4()}-${part4()}`;
  }

  function seed(){
    if(!localStorage.getItem(KEYS.regs)){
      write(KEYS.regs, [
        { id:newId('r'), nombre:'Jeremy Valdés', cedula:generateCedula(), rol:'Estudiante', curso:'DSVIII', aula:'3-105', tipo:'Entrada', fecha:'2025-11-26', hora:'07:55', estado:'A tiempo' },
        { id:newId('r'), nombre:'Juan Pérez', cedula:generateCedula(), rol:'Estudiante', curso:'DSVIII', aula:'3-105', tipo:'Entrada', fecha:'2025-11-26', hora:'08:10', estado:'Tarde' },
        { id:newId('r'), nombre:'Prof. Kexy Rodríguez', cedula:generateCedula(), rol:'Docente', aula:'3-105', tipo:'Entrada', fecha:'2025-11-26', hora:'07:00', estado:'A tiempo' }
      ]);
    }
    if(!localStorage.getItem(KEYS.justs)) write(KEYS.justs, []);
    if(!localStorage.getItem(KEYS.users)){
      write(KEYS.users, [
        {id:newId('u'), nombre:'Jeremy Valdés', cedula:'8-1234-5678', rol:'Estudiante', grupo:'1GS123', correo:'jeremy@utp'},
  {id:newId('u'), nombre:'Prof. Ejemplo', cedula:'4-9876-3456', rol:'Docente', grupo:'', correo:'ejemplo@utp'}
      ]);
    }
    if(!localStorage.getItem(KEYS.aulas)){
      write(KEYS.aulas, [
        {id:newId('a'), aula:'3-105', device:'ESP-105-A', estado:'Activo'},
        {id:newId('a'), aula:'3-201', device:'ESP-201-B', estado:'Desconectado'}
      ]);
    }
  }

  function delay(ms=250){ return new Promise(res=>setTimeout(res, ms)); }

  window.SimAPI = { delay, id:newId, cedula:generateCedula, keys:KEYS };
  window.SimDB = {
    read, write, seed,
    getRegs(){ return read(KEYS.regs); }, setRegs(arr){ write(KEYS.regs, arr); },
    getJusts(){ return read(KEYS.justs); }, setJusts(arr){ write(KEYS.justs, arr); },
    getUsers(){ return read(KEYS.users); }, setUsers(arr){ write(KEYS.users, arr); },
    getAulas(){ return read(KEYS.aulas); }, setAulas(arr){ write(KEYS.aulas, arr); },
    getSession(){ try{ return JSON.parse(localStorage.getItem(KEYS.session)||'null'); }catch(_){ return null; } },
    setSession(s){ localStorage.setItem(KEYS.session, JSON.stringify(s)); },
    clearSession(){ localStorage.removeItem(KEYS.session); }
  };

  seed();
})();