// Cliente de la API de SIMA. El token se guarda en el celular para no pedir
// la clave en cada visita.

import type { Sesion } from './tipos'

const CLAVE_TOKEN = 'sima.token'
const CLAVE_SESION = 'sima.sesion'

/** Evento que se emite cuando el servidor responde que la sesión ya no vale. */
export const SIN_SESION = 'sima:sin-sesion'

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

// Quién entró (nombre y si es jefe técnico o técnico). Se guarda una copia en
// el celular para que la aplicación abra aunque no haya señal.
export function sesionGuardada(): Sesion | null {
  try {
    return JSON.parse(localStorage.getItem(CLAVE_SESION) || 'null')
  } catch {
    return null
  }
}

export function guardarSesion(s: Sesion | null) {
  try {
    if (s) localStorage.setItem(CLAVE_SESION, JSON.stringify(s))
    else localStorage.removeItem(CLAVE_SESION)
  } catch {
    /* sin almacenamiento: se vuelve a pedir al servidor */
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
  let datos: unknown = null
  try {
    datos = texto ? JSON.parse(texto) : null
  } catch {
    /* respuesta que no es de la API (por ejemplo, el servidor caído): vale el código de estado */
  }
  if (!res.ok) {
    if (res.status === 401) {
      // La sesión ya no vale: se pide ingresar de nuevo. Lo guardado en el celular no se toca.
      guardarToken(null)
      window.dispatchEvent(new Event(SIN_SESION))
    }
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

/** Descarga un archivo de la API (por ejemplo, el informe en PDF) y lo guarda con el nombre dado. */
export async function descargar(ruta: string, nombre: string) {
  const t = token()
  const res = await fetch(`/api/${ruta}`, {
    headers: { Accept: 'application/pdf, application/json', ...(t ? { Authorization: `Token ${t}` } : {}) },
  })
  if (!res.ok) {
    let datos: unknown = null
    try {
      datos = await res.json()
    } catch {
      /* sin cuerpo JSON: vale el código de estado */
    }
    if (res.status === 401) {
      guardarToken(null)
      window.dispatchEvent(new Event(SIN_SESION))
    }
    throw new ErrorApi(res.status, datos)
  }
  const url = URL.createObjectURL(await res.blob())
  const a = document.createElement('a')
  a.href = url
  a.download = nombre
  document.body.appendChild(a)
  a.click()
  a.remove()
  setTimeout(() => URL.revokeObjectURL(url), 10000)
}
