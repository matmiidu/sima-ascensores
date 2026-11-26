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

// Lo esencial de la mantención registrada en una visita (H06).
export interface ResumenRegistro {
  id: number
  codigo: string
  operativo: boolean
  guardado_en_dispositivo: string
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
  registro: ResumenRegistro | null
}

// Quién entró: el jefe técnico administra; un técnico ve sus visitas (H04).
export interface Sesion {
  usuario: string
  nombre: string
  es_jefe: boolean
  tecnico: { id: number; nombre: string } | null
}

// Una visita tal como la ve el técnico en el celular (H04).
export interface VisitaDelDia {
  id: number
  fecha: string
  mes: string
  estado: 'programada' | 'realizada' | 'no_realizada'
  ascensor: number
  ascensor_identificador: string
  marca: string
  paradas: number
  tipo_display: string
  edificio_id: number
  edificio_nombre: string
  direccion: string
  comuna: string
  administrador_nombre: string
  administrador_telefono: string
  tecnico: number
  tecnico_nombre: string
  registro: ResumenRegistro | null
}

export interface MisVisitasDelDia {
  tecnico: { id: number; nombre: string }
  hoy: string
  fecha: string
  visitas: VisitaDelDia[]
  atrasadas: VisitaDelDia[]
  proxima_fecha: string | null
}

// Checklist de mantención (H06).
export type Resultado = 'bien' | 'observacion' | 'no_aplica'

export const RESULTADOS: Record<Resultado, string> = {
  bien: 'Bien',
  observacion: 'Con observación',
  no_aplica: 'No aplica',
}

export interface PuntoChecklist {
  id: number
  codigo: string
  descripcion: string
  orden: number
}

// Una mantención ya guardada en el servidor, con sus respuestas.
export interface RegistroMantencion {
  id: number
  codigo: string
  id_local: string
  visita: number
  fecha_programada: string
  ascensor: number
  ascensor_identificador: string
  edificio_id: number
  edificio_nombre: string
  direccion: string
  comuna: string
  tecnico: number
  tecnico_nombre: string
  operativo: boolean
  falla_descripcion: string
  observaciones: string
  guardado_en_dispositivo: string
  recibido: string
  respuestas: { punto: number; codigo: string; descripcion: string; resultado: Resultado; comentario: string }[]
}

export interface Resumen {
  mes: string
  equipos_activos: number
  con_visita: number
  realizadas: number
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

export interface AlertaCertificacion {
  ascensor_id: number
  identificador: string
  edificio_id: number
  edificio: string
  direccion: string
  comuna: string
  vencimiento: string | null
  dias_restantes: number | null
  administrador: { nombre: string; correo: string; telefono: string }
}

export interface Certificaciones {
  hoy: string
  dias: number
  vencidas: AlertaCertificacion[]
  por_vencer: AlertaCertificacion[]
  sin_fecha: AlertaCertificacion[]
}

export interface InformeEdificio {
  id: number
  nombre: string
  direccion: string
  comuna: string
  tecnico: string
  administrador: { nombre: string; correo: string }
  visitas: number
  registradas: number
  detenidos: number
  faltan: number
  completo: boolean
  archivo: string
}

export interface InformesDelMes {
  mes: string
  nombre_mes: string
  edificios: InformeEdificio[]
}
