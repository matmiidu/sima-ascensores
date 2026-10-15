// Prueba de concepto S01: guardar el checklist en el celular (IndexedDB) y
// enviarlo cuando vuelve la señal. Cada registro lleva un id generado en el
// celular, así un reenvío no crea duplicados en el servidor.

import { enviar } from './api'

export interface ChecklistLocal {
  id_local: string
  ascensor: number | null
  ascensor_nombre: string
  respuestas: Record<string, string>
  observaciones: string
  guardado_en_dispositivo: string
  enviado: string | null
  intentos: number
  ultimo_error: string | null
}

const BASE = 'sima-terreno'
const TABLA = 'checklists'

function abrir(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(BASE, 1)
    req.onupgradeneeded = () => {
      req.result.createObjectStore(TABLA, { keyPath: 'id_local' })
    }
    req.onsuccess = () => resolve(req.result)
    req.onerror = () => reject(req.error)
  })
}

async function conTabla<T>(modo: IDBTransactionMode, fn: (t: IDBObjectStore) => IDBRequest<T>): Promise<T> {
  const db = await abrir()
  return new Promise((resolve, reject) => {
    const tx = db.transaction(TABLA, modo)
    const req = fn(tx.objectStore(TABLA))
    tx.oncomplete = () => {
      db.close()
      resolve(req.result)
    }
    tx.onerror = () => reject(tx.error)
  })
}

export const listar = () => conTabla<ChecklistLocal[]>('readonly', (t) => t.getAll())
const guardarRegistro = (c: ChecklistLocal) => conTabla('readwrite', (t) => t.put(c))
export const borrarEnviados = async () => {
  for (const c of await listar()) if (c.enviado) await conTabla('readwrite', (t) => t.delete(c.id_local))
}

// crypto.randomUUID solo existe con HTTPS; getRandomValues funciona siempre.
function nuevoId(): string {
  if (crypto.randomUUID) return crypto.randomUUID()
  const b = crypto.getRandomValues(new Uint8Array(16))
  b[6] = (b[6] & 0x0f) | 0x40
  b[8] = (b[8] & 0x3f) | 0x80
  const h = [...b].map((x) => x.toString(16).padStart(2, '0')).join('')
  return `${h.slice(0, 8)}-${h.slice(8, 12)}-${h.slice(12, 16)}-${h.slice(16, 20)}-${h.slice(20)}`
}

export async function guardar(datos: Pick<ChecklistLocal, 'ascensor' | 'ascensor_nombre' | 'respuestas' | 'observaciones'>) {
  const registro: ChecklistLocal = {
    ...datos,
    id_local: nuevoId(),
    guardado_en_dispositivo: new Date().toISOString(),
    enviado: null,
    intentos: 0,
    ultimo_error: null,
  }
  await guardarRegistro(registro)
  return registro
}

let sincronizando = false

/** Envía lo pendiente. Devuelve cuántos se enviaron y cuántos siguen pendientes. */
export async function sincronizar(): Promise<{ enviados: number; pendientes: number }> {
  if (sincronizando) return { enviados: 0, pendientes: (await listar()).filter((c) => !c.enviado).length }
  sincronizando = true
  let enviados = 0
  try {
    const pendientes = (await listar()).filter((c) => !c.enviado)
    for (const c of pendientes) {
      if (!navigator.onLine) break
      try {
        await enviar('poc/checklists/', {
          id_local: c.id_local,
          ascensor: c.ascensor,
          respuestas: c.respuestas,
          observaciones: c.observaciones,
          guardado_en_dispositivo: c.guardado_en_dispositivo,
        })
        await guardarRegistro({ ...c, enviado: new Date().toISOString(), intentos: c.intentos + 1, ultimo_error: null })
        enviados++
      } catch (e) {
        await guardarRegistro({ ...c, intentos: c.intentos + 1, ultimo_error: (e as Error).message })
      }
    }
  } finally {
    sincronizando = false
  }
  return { enviados, pendientes: (await listar()).filter((c) => !c.enviado).length }
}
