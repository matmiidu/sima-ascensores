// Trabajo en terreno (H06). Para que el técnico pueda registrar aunque no haya
// señal (RNF-01), tres cosas viven en el celular:
//   1. una copia de sus visitas del día y de los puntos del checklist;
//   2. el borrador del checklist que está llenando;
//   3. las mantenciones guardadas que todavía no llegan al servidor.
// Cada mantención lleva un identificador generado en el celular (id_local): si
// un envío se repite, el servidor reconoce que ya la tiene y no la duplica.
// Es el mismo esquema que se probó en S01.

import { ErrorApi, api, enviar, sesionGuardada } from './api'
import type { MisVisitasDelDia, PuntoChecklist, RegistroMantencion, Resultado, VisitaDelDia } from './tipos'

export interface Respuesta {
  resultado?: Resultado
  comentario: string
}

export interface MantencionLocal {
  id_local: string
  usuario: string
  visita: number
  titulo: string
  fecha_visita: string
  respuestas: { punto: number; resultado: Resultado; comentario: string }[]
  operativo: boolean
  falla_descripcion: string
  observaciones: string
  guardado_en_dispositivo: string
  estado: 'pendiente' | 'enviada' | 'rechazada'
  enviado: string | null
  codigo: string | null
  intentos: number
  ultimo_error: string | null
}

// ---------- Avisos a las pantallas ----------

type Aviso = 'cola' | 'sincronizado'
const oyentes = new Set<(a: Aviso) => void>()

/** Avisa cuando cambia lo guardado en el celular ('cola') o termina un envío ('sincronizado'). */
export function alCambiar(fn: (a: Aviso) => void) {
  oyentes.add(fn)
  return () => {
    oyentes.delete(fn)
  }
}
const avisar = (a: Aviso) => oyentes.forEach((fn) => fn(a))

// ---------- Mantenciones guardadas en el celular (IndexedDB) ----------

const BASE = 'sima-terreno'
const TABLA = 'mantenciones'

function abrir(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(BASE, 2)
    req.onupgradeneeded = () => {
      const db = req.result
      // La tabla de la prueba de concepto S01 ya no se usa.
      if (db.objectStoreNames.contains('checklists')) db.deleteObjectStore('checklists')
      if (!db.objectStoreNames.contains(TABLA)) db.createObjectStore(TABLA, { keyPath: 'id_local' })
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
    tx.onabort = () => reject(tx.error)
  })
}

const usuarioActual = () => sesionGuardada()?.usuario ?? ''

/** Lo que este usuario tiene guardado en el celular, de lo más antiguo a lo más nuevo. */
export async function mantencionesLocales(): Promise<MantencionLocal[]> {
  const todas = await conTabla<MantencionLocal[]>('readonly', (t) => t.getAll())
  const usuario = usuarioActual()
  return todas
    .filter((m) => m.usuario === usuario)
    .sort((a, b) => a.guardado_en_dispositivo.localeCompare(b.guardado_en_dispositivo))
}

async function escribir(m: MantencionLocal) {
  await conTabla('readwrite', (t) => t.put(m))
  avisar('cola')
}

export async function quitar(id_local: string) {
  await conTabla('readwrite', (t) => t.delete(id_local))
  avisar('cola')
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

/** Guarda la mantención en el celular. Queda pendiente de envío. */
export async function guardarMantencion(
  datos: Pick<MantencionLocal, 'visita' | 'titulo' | 'fecha_visita' | 'respuestas' | 'operativo' | 'falla_descripcion' | 'observaciones'>,
): Promise<MantencionLocal> {
  const m: MantencionLocal = {
    ...datos,
    id_local: nuevoId(),
    usuario: usuarioActual(),
    guardado_en_dispositivo: new Date().toISOString(),
    estado: 'pendiente',
    enviado: null,
    codigo: null,
    intentos: 0,
    ultimo_error: null,
  }
  await escribir(m)
  return m
}

/** Envía una mantención al servidor y deja anotado el resultado en el celular. */
export async function enviarMantencion(m: MantencionLocal): Promise<MantencionLocal> {
  let resultado: MantencionLocal
  try {
    const r = await enviar<RegistroMantencion>('mantenciones/', {
      id_local: m.id_local,
      visita: m.visita,
      respuestas: m.respuestas,
      operativo: m.operativo,
      falla_descripcion: m.falla_descripcion,
      observaciones: m.observaciones,
      guardado_en_dispositivo: m.guardado_en_dispositivo,
    })
    resultado = { ...m, estado: 'enviada', enviado: new Date().toISOString(), codigo: r.codigo, intentos: m.intentos + 1, ultimo_error: null }
  } catch (e) {
    // Sin señal o con el servidor caído se reintenta después. Si el servidor
    // contestó que no la acepta (por ejemplo, la visita ya estaba registrada),
    // reintentar no sirve: queda rechazada, con el motivo a la vista.
    const estado = e instanceof ErrorApi ? e.estado : 0
    const definitivo = estado >= 400 && estado < 500 && ![401, 408, 429].includes(estado)
    resultado = { ...m, estado: definitivo ? 'rechazada' : 'pendiente', intentos: m.intentos + 1, ultimo_error: (e as Error).message }
  }
  await escribir(resultado)
  return resultado
}

let enCurso: Promise<{ enviadas: number; pendientes: number }> | null = null

/** Envía lo pendiente, en orden. Si ya hay un envío en curso, devuelve ese mismo. */
export function sincronizar(): Promise<{ enviadas: number; pendientes: number }> {
  if (!enCurso) {
    enCurso = (async () => {
      let enviadas = 0
      for (const m of (await mantencionesLocales()).filter((x) => x.estado === 'pendiente')) {
        if (!navigator.onLine) break
        const r = await enviarMantencion(m)
        if (r.estado === 'enviada') enviadas++
        else if (r.estado === 'pendiente') break // sin conexión con el servidor: se reintenta más tarde
      }
      const pendientes = (await mantencionesLocales()).filter((x) => x.estado === 'pendiente').length
      if (enviadas) avisar('sincronizado')
      return { enviadas, pendientes }
    })().finally(() => {
      enCurso = null
    })
  }
  return enCurso
}

/** Quita del celular las mantenciones que ya llegaron al servidor hace más de dos días. */
export async function limpiarEnviadas() {
  const limite = Date.now() - 2 * 86400000
  for (const m of await mantencionesLocales()) {
    if (m.estado === 'enviada' && m.enviado && new Date(m.enviado).getTime() < limite) await quitar(m.id_local)
  }
}

// ---------- Copia de las visitas y de los puntos (para abrir sin señal) ----------

const CLAVE_DIAS = 'sima.terreno.dias'
const CLAVE_PUNTOS = 'sima.terreno.puntos'

interface CopiaDias {
  usuario: string
  dias: Record<string, { datos: MisVisitasDelDia; guardado: string }>
}

function leer<T>(clave: string): T | null {
  try {
    return JSON.parse(localStorage.getItem(clave) || 'null')
  } catch {
    return null
  }
}

function guardar(clave: string, valor: unknown) {
  try {
    localStorage.setItem(clave, JSON.stringify(valor))
  } catch {
    /* sin almacenamiento: la copia solo sirve mientras la pestaña siga abierta */
  }
}

function copiaDias(): CopiaDias {
  const c = leer<CopiaDias>(CLAVE_DIAS)
  return c && c.usuario === usuarioActual() ? c : { usuario: usuarioActual(), dias: {} }
}

const hoyDelCelular = () => {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

export interface DiaCargado {
  datos: MisVisitasDelDia
  /** Si no hubo señal, hora en que se guardó la copia que se está mostrando. */
  copiaDe: string | null
}

/** Visitas del técnico para un día ('' = hoy). Con señal las pide al servidor y deja una copia; sin señal usa la copia. */
export async function cargarDia(fecha: string): Promise<DiaCargado> {
  try {
    const datos = await api<MisVisitasDelDia>(`mis-visitas/${fecha ? `?fecha=${fecha}` : ''}`)
    const copia = copiaDias()
    copia.dias[datos.fecha] = { datos, guardado: new Date().toISOString() }
    // Se conservan solo los días recientes, para no llenar el celular.
    const fechas = Object.keys(copia.dias).sort()
    for (const f of fechas.slice(0, Math.max(0, fechas.length - 10))) delete copia.dias[f]
    guardar(CLAVE_DIAS, copia)
    return { datos, copiaDe: null }
  } catch (e) {
    // Un rechazo del servidor se muestra tal cual; sin señal o con el servidor caído se usa la copia.
    if (e instanceof ErrorApi && e.estado < 500) throw e
    const copia = copiaDias().dias[fecha || hoyDelCelular()]
    if (!copia) {
      throw new Error('No hay señal y este día no está guardado en el celular. Abre la aplicación con señal al empezar la jornada.')
    }
    return { datos: copia.datos, copiaDe: copia.guardado }
  }
}

/** Puntos del checklist. Igual que las visitas: del servidor si hay señal, de la copia si no. */
export async function cargarPuntos(): Promise<PuntoChecklist[]> {
  try {
    const puntos = await api<PuntoChecklist[]>('puntos-checklist/')
    guardar(CLAVE_PUNTOS, puntos)
    return puntos
  } catch (e) {
    // Un rechazo del servidor se muestra tal cual; sin señal o con el servidor caído se usa la copia.
    if (e instanceof ErrorApi && e.estado < 500) throw e
    const copia = leer<PuntoChecklist[]>(CLAVE_PUNTOS)
    if (!copia) throw new Error('No hay señal y el checklist no está guardado en el celular. Ábrelo una vez con señal.')
    return copia
  }
}

/** Busca una visita por su id: primero con el servidor (día de hoy) y, si no hay señal, en las copias guardadas. */
export async function buscarVisita(id: number): Promise<VisitaDelDia | null> {
  const enDias = (dias: MisVisitasDelDia[]) => {
    for (const d of dias) {
      const v = [...d.visitas, ...d.atrasadas].find((x) => x.id === id)
      if (v) return v
    }
    return null
  }
  let reciente: MisVisitasDelDia[] = []
  try {
    reciente = [(await cargarDia('')).datos]
  } catch {
    /* sin señal y sin copia de hoy: se busca en lo que haya */
  }
  const copias = Object.values(copiaDias().dias)
    .sort((a, b) => b.guardado.localeCompare(a.guardado))
    .map((c) => c.datos)
  return enDias(reciente) ?? enDias(copias)
}

// ---------- Borrador del checklist ----------

export interface Borrador {
  respuestas: Record<number, Respuesta>
  operativo: boolean | null
  falla: string
  observaciones: string
}

const claveBorrador = (visita: number) => `sima.borrador.${usuarioActual()}.${visita}`

export const leerBorrador = (visita: number) => leer<Borrador>(claveBorrador(visita))
export const guardarBorrador = (visita: number, b: Borrador) => guardar(claveBorrador(visita), b)
export function borrarBorrador(visita: number) {
  try {
    localStorage.removeItem(claveBorrador(visita))
  } catch {
    /* nada que borrar */
  }
}

// ---------- Reglas del checklist (RF-02 y RF-03) ----------

export interface Faltas {
  puntos: Record<number, string>
  operativo?: string
  falla?: string
}

const cuantos = (n: number) => `${n} ${n === 1 ? 'punto' : 'puntos'}`

/**
 * Revisa el checklist antes de guardarlo. Son las mismas reglas que aplica el
 * servidor; se repiten aquí porque sin señal el servidor no puede rechazar.
 * Devuelve el mensaje (vacío si todo está en orden) y qué falta en cada parte.
 */
export function revisarChecklist(puntos: PuntoChecklist[], b: Borrador): { mensaje: string; faltas: Faltas } {
  const faltas: Faltas = { puntos: {} }
  let sinResponder = 0
  let sinObservacion = 0
  for (const p of puntos) {
    const r = b.respuestas[p.id]
    if (!r?.resultado) {
      faltas.puntos[p.id] = 'Falta responder este punto.'
      sinResponder++
    } else if (r.resultado === 'observacion' && !r.comentario.trim()) {
      faltas.puntos[p.id] = 'Escribe la observación de este punto.'
      sinObservacion++
    }
  }
  const motivos: string[] = []
  if (sinResponder) motivos.push(`falta responder ${cuantos(sinResponder)} del checklist`)
  if (sinObservacion) motivos.push(`falta escribir la observación de ${cuantos(sinObservacion)}`)
  if (b.operativo === null) {
    faltas.operativo = 'Indica si el equipo quedó operativo.'
    motivos.push('falta indicar si el equipo quedó operativo')
  } else if (!b.operativo && !b.falla.trim()) {
    faltas.falla = 'Describe la falla: el equipo quedó detenido.'
    motivos.push('el equipo quedó detenido, describe la falla')
  }
  return { mensaje: motivos.length ? `No se guardó: ${motivos.join('; ')}.` : '', faltas }
}
