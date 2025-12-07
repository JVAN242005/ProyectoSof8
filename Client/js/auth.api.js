const API_URL = 'http://localhost:8000/api';

// Función para hacer login contra el backend
// Recibe correo y contraseña, hace petición POST y devuelve el usuario si es correcto
export async function login(correo, password) {
  // Realiza la petición al endpoint /login del backend
  const res = await fetch(`${API_URL}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ correo, password })
  });

  // Si la respuesta no es exitosa, lanza error
  if (!res.ok) throw new Error('Usuario o contraseña incorrectos');
  // Devuelve el objeto usuario recibido del backend
  return await res.json(); // { user }
}