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
