import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import { fechaCorta, fechaDe, horaDe, nombreMes } from '../fechas'
import type { RegistroMantencion, Tecnico } from '../tipos'

function mesActual() {
  const d = new Date()
  return { anio: d.getFullYear(), mes: d.getMonth() + 1 }
}

/** Todos los checklists que enviaron los técnicos en el mes, para el jefe técnico. */
export default function Registros() {
  const [{ anio, mes }, setPeriodo] = useState(mesActual)
  const [registros, setRegistros] = useState<RegistroMantencion[] | null>(null)
  const [tecnicos, setTecnicos] = useState<Tecnico[]>([])
  const [tecnico, setTecnico] = useState('')
  const [estado, setEstado] = useState('')
  const [error, setError] = useState('')

  const clave = `${anio}-${String(mes).padStart(2, '0')}`

  useEffect(() => {
    setRegistros(null)
    setError('')
    api<RegistroMantencion[]>(`mantenciones/?mes=${clave}`)
      .then(setRegistros)
      .catch((e) => setError((e as Error).message))
  }, [clave])

  useEffect(() => {
    api<Tecnico[]>('tecnicos/').then(setTecnicos).catch(() => {})
  }, [])

  function mover(delta: number) {
    const d = new Date(anio, mes - 1 + delta, 1)
    setPeriodo({ anio: d.getFullYear(), mes: d.getMonth() + 1 })
  }

  const filtrados = useMemo(
    () =>
      (registros ?? []).filter(
        (r) =>
          (!tecnico || String(r.tecnico) === tecnico) &&
          (!estado || (estado === 'operativo') === r.operativo),
      ),
    [registros, tecnico, estado],
  )

  const detenidos = (registros ?? []).filter((r) => !r.operativo).length

  return (
    <section>
      <div className="encabezado">
        <button onClick={() => mover(-1)} aria-label="Mes anterior">‹</button>
        <h1 className="mes">{nombreMes(anio, mes)}</h1>
        <button onClick={() => mover(1)} aria-label="Mes siguiente">›</button>
      </div>

      {registros && (
        <p className="tenue">
          {registros.length === 1 ? '1 checklist recibido' : `${registros.length} checklists recibidos`}
          {registros.length > 0 && `: ${registros.length - detenidos} con el equipo operativo y ${detenidos} detenido${detenidos === 1 ? '' : 's'}.`}
        </p>
      )}

      {registros && registros.length > 0 && (
        <div className="filtros">
          <select value={tecnico} onChange={(e) => setTecnico(e.target.value)} aria-label="Técnico">
            <option value="">Todos los técnicos</option>
            {tecnicos.map((t) => <option key={t.id} value={t.id}>{t.nombre}</option>)}
          </select>
          <select value={estado} onChange={(e) => setEstado(e.target.value)} aria-label="Cómo quedó el equipo">
            <option value="">Todos los estados</option>
            <option value="operativo">Solo operativos</option>
            <option value="detenido">Solo detenidos</option>
          </select>
        </div>
      )}

      {error && <p className="error">{error}</p>}
      {registros === null && !error && <p className="tenue">Cargando…</p>}
      {registros && registros.length > 0 && filtrados.length === 0 && (
        <p className="tenue">Ningún checklist calza con el filtro.</p>
      )}

      <ul className="lista">
        {filtrados.map((r) => (
          <li key={r.id} className="fila">
            <div>
              <Link to={`/mantenciones/${r.id}`}>
                <strong>{r.edificio_nombre} · {r.ascensor_identificador}</strong>
              </Link>
              <span className="tenue">
                {r.codigo} · {r.tecnico_nombre} · {fechaCorta(fechaDe(r.guardado_en_dispositivo))} a las {horaDe(r.guardado_en_dispositivo)}
              </span>
              {!r.operativo && <span>Falla: {r.falla_descripcion}</span>}
            </div>
            <span className="derecha">
              <span className={`etiqueta ${r.operativo ? 'ok' : 'peligro'}`}>{r.operativo ? 'Operativo' : 'Detenido'}</span>
            </span>
          </li>
        ))}
      </ul>
    </section>
  )
}
