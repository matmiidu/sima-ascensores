const MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
const DIAS = ['domingo', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado']

// Las fechas de la API vienen como AAAA-MM-DD; se leen a mediodía para que la
// zona horaria no las corra un día.
const leer = (iso: string) => new Date(iso.slice(0, 10) + 'T12:00')

export const fechaCorta = (iso: string) => {
  const d = leer(iso)
  return `${String(d.getDate()).padStart(2, '0')}-${String(d.getMonth() + 1).padStart(2, '0')}-${d.getFullYear()}`
}

export const diaLargo = (iso: string) => {
  const d = leer(iso)
  return `${DIAS[d.getDay()]} ${d.getDate()} de ${MESES[d.getMonth()]}`
}

export const nombreMes = (anio: number, mes: number) => `${MESES[mes - 1]} de ${anio}`

const aIso = (d: Date) =>
  `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`

export const sumarDias = (iso: string, dias: number) => {
  const d = leer(iso)
  d.setDate(d.getDate() + dias)
  return aIso(d)
}

export const mayuscula = (texto: string) => texto.charAt(0).toUpperCase() + texto.slice(1)

/** Día de hoy según el reloj del celular, como AAAA-MM-DD. */
export const hoyLocal = () => aIso(new Date())

// Los momentos (fecha y hora) vienen en hora universal; se muestran en la hora del celular.
export const fechaDe = (momento: string) => aIso(new Date(momento))
export const horaDe = (momento: string) => {
  const d = new Date(momento)
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}
