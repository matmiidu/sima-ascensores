// Cliente de la API de SIMA. El token se guarda en el celular para no pedir
// la clave en cada visita.

const CLAVE_TOKEN = 'sima.token'

export class ErrorApi extends Error {
  estado: number
  datos: unknown
  constructor(estado: number, datos: unknown) {
    super(mensajeDeError(datos) || `Error ${estado}`)
    this.estado = estado
    this.datos = datos
  }
}

function mensajeDeError(datos: unknown): string {
  if (!datos || typeof datos !== 'object') return ''
  const d = datos as Record<string, unknown>
  if (typeof d.detail === 'string') return d.detail
  // Los mensajes del servidor ya dicen qué corregir; no se antepone el nombre interno del campo.
  return Object.values(d)
    .map((v) => (Array.isArray(v) ? v.join(' ') : String(v)))
    .join(' · ')
}

export function token(): string | null {
  try {
    return localStorage.getItem(CLAVE_TOKEN)
  } catch {
    return null
  }
}

export function guardarToken(t: string | null) {
  try {
    if (t) localStorage.setItem(CLAVE_TOKEN, t)
    else localStorage.removeItem(CLAVE_TOKEN)
  } catch {
    /* sin almacenamiento: la sesión dura lo que dure la pestaña */
  }
}

export async function api<T>(ruta: string, opciones: RequestInit = {}): Promise<T> {
  const t = token()
  const res = await fetch(`/api/${ruta}`, {
    ...opciones,
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...(t ? { Authorization: `Token ${t}` } : {}),
      ...opciones.headers,
    },
  })
  const texto = await res.text()
  const datos = texto ? JSON.parse(texto) : null
  if (!res.ok) {
    if (res.status === 401) guardarToken(null)
    throw new ErrorApi(res.status, datos)
  }
  return datos as T
}

export const enviar = <T>(ruta: string, cuerpo: unknown, metodo = 'POST') =>
  api<T>(ruta, { method: metodo, body: JSON.stringify(cuerpo) })

export async function iniciarSesion(usuario: string, clave: string) {
  const r = await enviar<{ token: string }>('token/', { username: usuario, password: clave })
  guardarToken(r.token)
}
