import { diaLargo, fechaDe, horaDe } from '../fechas'
import type { MantencionLocal } from '../terreno'
import { RESULTADOS, type PuntoChecklist, type RegistroMantencion, type Resultado } from '../tipos'

// Una mantención registrada, venga del servidor o de lo guardado en el celular.
export interface RegistroVista {
  codigo: string | null
  guardado: string
  tecnico: string
  operativo: boolean
  falla: string
  observaciones: string
  respuestas: { descripcion: string; resultado: Resultado; comentario: string }[]
}

export const desdeServidor = (r: RegistroMantencion): RegistroVista => ({
  codigo: r.codigo,
  guardado: r.guardado_en_dispositivo,
  tecnico: r.tecnico_nombre,
  operativo: r.operativo,
  falla: r.falla_descripcion,
  observaciones: r.observaciones,
  respuestas: r.respuestas,
})

export const desdeCelular = (m: MantencionLocal, puntos: PuntoChecklist[], tecnico: string): RegistroVista => ({
  codigo: m.codigo,
  guardado: m.guardado_en_dispositivo,
  tecnico,
  operativo: m.operativo,
  falla: m.falla_descripcion,
  observaciones: m.observaciones,
  respuestas: m.respuestas.map((r) => ({
    descripcion: puntos.find((p) => p.id === r.punto)?.descripcion ?? `Punto ${r.punto}`,
    resultado: r.resultado,
    comentario: r.comentario,
  })),
})

const CLASES: Record<Resultado, string> = { bien: 'ok', observacion: 'alerta', no_aplica: '' }

export default function DetalleRegistro({ registro }: { registro: RegistroVista }) {
  return (
    <>
      <div className={`tarjeta ${registro.operativo ? 'ok' : 'detenido'}`}>
        <strong>{registro.codigo ? `Mantención ${registro.codigo}` : 'Mantención guardada en el celular'}</strong>
        <p>
          Registrada el {diaLargo(fechaDe(registro.guardado))} a las {horaDe(registro.guardado)} por {registro.tecnico}.
        </p>
        <p className={registro.operativo ? '' : 'peligro'}>
          {registro.operativo ? 'El equipo quedó operativo.' : 'El equipo quedó detenido.'}
        </p>
        {!registro.operativo && <p>Falla: {registro.falla}</p>}
        {!registro.codigo && <p className="advertencia">Todavía no llega al servidor: se enviará sola cuando vuelva la señal.</p>}
      </div>
      <ul className="lista">
        {registro.respuestas.map((r, i) => (
          <li key={i} className="fila">
            <div>
              <span>
                {i + 1}. {r.descripcion}
              </span>
              {r.comentario && <span className="tenue">{r.comentario}</span>}
            </div>
            <span className={`etiqueta ${CLASES[r.resultado]}`}>{RESULTADOS[r.resultado]}</span>
          </li>
        ))}
      </ul>
      {registro.observaciones && <p>Observaciones generales: {registro.observaciones}</p>}
    </>
  )
}
