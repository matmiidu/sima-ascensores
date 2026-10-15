export type TipoUso = 'residencial' | 'oficinas' | 'comercial' | 'salud' | 'educacion' | 'mixto'

export const TIPOS_USO: Record<TipoUso, string> = {
  residencial: 'Residencial',
  oficinas: 'Oficinas',
  comercial: 'Comercial',
  salud: 'Salud',
  educacion: 'Educación',
  mixto: 'Mixto',
}

export const TIPOS_ASCENSOR = { electrico: 'Eléctrico de tracción', hidraulico: 'Hidráulico' }
export const USOS_ASCENSOR = {
  pasajeros: 'Pasajeros',
  carga: 'Carga',
  montacamas: 'Montacamas',
  montavehiculos: 'Montavehículos',
}

export interface Tecnico {
  id: number
  nombre: string
  telefono: string
  capacidad_diaria: number
  activo: boolean
}

export interface Ascensor {
  id: number
  edificio: number
  edificio_nombre: string
  identificador: string
  tipo: keyof typeof TIPOS_ASCENSOR
  tipo_display: string
  uso: keyof typeof USOS_ASCENSOR
  uso_display: string
  marca: string
  numero_serie: string
  paradas: number
  capacidad_kg: number | null
  fecha_instalacion: string | null
  vencimiento_certificacion: string | null
  activo: boolean
}

export interface Edificio {
  id: number
  nombre: string
  direccion: string
  comuna: string
  tipo_uso: TipoUso
  tipo_uso_display: string
  administrador_nombre: string
  administrador_correo: string
  administrador_telefono: string
  tecnico_asignado: number | null
  tecnico_nombre: string | null
  activo: boolean
  total_ascensores: number
  ascensores: Ascensor[]
}

export interface Visita {
  id: number
  ascensor: number
  ascensor_identificador: string
  edificio_id: number
  edificio_nombre: string
  direccion: string
  comuna: string
  tecnico: number
  tecnico_nombre: string
  mes: string
  fecha: string
  estado: 'programada' | 'realizada' | 'no_realizada'
}

export interface Resumen {
  mes: string
  equipos_activos: number
  con_visita: number
  sin_visita: { id: number; nombre: string }[]
  dias_habiles: string[]
  carga: { tecnico: string; capacidad: number; total: number; por_dia: Record<string, number> }[]
  ultima_generacion: {
    generado: string
    generado_por: string | null
    visitas_creadas: number
    advertencias: string[]
  } | null
}
