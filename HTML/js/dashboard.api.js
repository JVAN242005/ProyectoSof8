/**
 * DashboardAPI — Resumen del día
 *
 * Propósito:
 * - Calcular métricas rápidas para el dashboard a partir de los registros
 *   de asistencias guardados en SimDB.
 *
 * Método:
 * - resumenDelDia() -> Promise<{ total, entradas, salidas, puntualidad }>
 *   donde puntualidad es el % de entradas con estado "A tiempo".
 */
(function(){
  const db = window.SimDB, api = window.SimAPI;

  window.DashboardAPI = {
    async resumenDelDia(){
      await api.delay();
      const asistencias = db.getRegs();
      const hoy = new Date().toISOString().slice(0,10);
      const registrosHoy = asistencias.filter(a=>a.fecha===hoy);
      const entradas = registrosHoy.filter(a=>a.tipo==='Entrada');
      const salidas = registrosHoy.filter(a=>a.tipo==='Salida');
      const entradasPuntuales = entradas.filter(a=>a.estado==='A tiempo');
      const porcentajePuntual = entradas.length>0 ? Math.round((entradasPuntuales.length/entradas.length)*100) : 0;
      return { total: registrosHoy.length, entradas: entradas.length, salidas: salidas.length, puntualidad: porcentajePuntual };
    }
  };
})();