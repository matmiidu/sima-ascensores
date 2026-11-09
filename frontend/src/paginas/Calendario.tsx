import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, enviar } from '../api'
import { diaLargo, fechaCorta, fechaDe, horaDe, nombreMes } from '../fechas'
import type { RegistroMantencion, Resumen, Tecnico, Visita } from '../tipos'

// Se abre en el mes en curso, que es el que el jefe técnico va siguiendo; para
// planificar el próximo basta avanzar un mes.
function mesActual() {
  const d = new Date()
  return { anio: d.getFullYear(), mes: d.getMonth() + 1 }
}

export default function Calendario() {
  const [{ anio, mes }, setPeriodo] = useState(mesActual)
  const [visitas, setVisitas] = useState<Visita[] | null>(null)
  const [resumen, setResumen] = useState<Resumen | null>(null)
  const [detenidos, setDetenidos] = useState<RegistroMantencion[]>([])
  const [tecnicos, setTecnicos] = useState<Tecnico[]>([])
  const [tecnico, setTecnico] = useState('')
  const [generando, setGenerando] = useState(false)
  const [mensaje, setMensaje] = useState('')
  const [error, setError] = useState('')

  const clave = `${anio}-${String(mes).padStart(2, '0')}`

  const cargar = useCallback(async () => {
    setError('')
    try {
      const [v, r, d] = await Promise.all([
        api<Visita[]>(`visitas/?mes=${clave}`),
        api<Resumen>(`calendario/resumen/?mes=${clave}`),
        api<RegistroMantencion[]>(`mantenciones/?mes=${clave}&detenidos=1`),
      ])
      setVisitas(v)
      setResumen(r)
      setDetenidos(d)
    } catch (e) {
      setError((e as Error).message)
    }
  }, [clave])

  useEffect(() => {
    setVisitas(null)
    cargar()
  }, [cargar])

  useEffect(() => {
    api<Tecnico[]>('tecnicos/').then(setTecnicos).catch(() => {})
  }, [])

  async function generar(reemplazar: boolean) {
    if (reemplazar && !confirm('Se borran las visitas programadas del mes (no las realizadas) y se vuelven a repartir. ¿Seguir?')) return
    setGenerando(true)
    setMensaje('')
    setError('')
    try {
      const r = await enviar<{ creadas: number; ya_programadas: number }>('calendario/generar/', { anio, mes, reemplazar })
      setMensaje(
        r.creadas === 0
          ? 'No había equipos sin visita: el calendario ya estaba completo.'
          : `${r.creadas === 1 ? 'Se programó 1 visita' : `Se programaron ${r.creadas} visitas`}${r.ya_programadas && !reemplazar ? ` (ya había ${r.ya_programadas})` : ''}.`,
      )
      await cargar()
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setGenerando(false)
    }
  }

  function mover(delta: number) {
    const d = new Date(anio, mes - 1 + delta, 1)
    setPeriodo({ anio: d.getFullYear(), mes: d.getMonth() + 1 })
    setMensaje('')
  }

  const porDia = useMemo(() => {
    const filtradas = (visitas ?? []).filter((v) => !tecnico || String(v.tecnico) === tecnico)
    const grupos = new Map<string, Map<number, Visita[]>>()
    for (const v of filtradas) {
      if (!grupos.has(v.fecha)) grupos.set(v.fecha, new Map())
      const dia = grupos.get(v.fecha)!
      if (!dia.has(v.edificio_id)) dia.set(v.edificio_id, [])
      dia.get(v.edificio_id)!.push(v)
    }
    return [...grupos.entries()].sort(([a], [b]) => a.localeCompare(b))
  }, [visitas, tecnico])

  const completo = resumen && resumen.equipos_activos > 0 && resumen.sin_visita.length === 0

  return (
    <section>
      <div className="encabezado">
        <button onClick={() => mover(-1)} aria-label="Mes anterior">‹</button>
        <h1 className="mes">{nombreMes(anio, mes)}</h1>
        <button onClick={() => mover(1)} aria-label="Mes siguiente">›</button>
      </div>

      {resumen && (
        <div className={`tarjeta cobertura ${completo ? 'ok' : 'alerta'}`}>
          <strong>
            {resumen.con_visita} de {resumen.equipos_activos} equipos con visita
          </strong>
          <span className="tenue">{resumen.dias_habiles.length} días hábiles en el mes</span>
          {resumen.con_visita > 0 && (
            <span>
              {resumen.realizadas} de {resumen.con_visita} visitas realizadas
            </span>
          )}
          {resumen.sin_visita.length > 0 && resumen.con_visita > 0 && (
            <details>
              <summary>{resumen.sin_visita.length} sin visita</summary>
              <ul>{resumen.sin_visita.map((a) => <li key={a.id}>{a.nombre}</li>)}</ul>
            </details>
          )}
          <div className="acciones">
            {!completo && (
              <button className="primario" disabled={generando} onClick={() => generar(false)}>
                {generando ? 'Generando…' : resumen.con_visita ? 'Programar los que faltan' : 'Generar calendario'}
              </button>
            )}
            {resumen.con_visita > 0 && (
              <button disabled={generando} onClick={() => generar(true)}>Volver a repartir</button>
            )}
          </div>
          {mensaje && <p>{mensaje}</p>}
          {resumen.ultima_generacion?.advertencias.map((a) => (
            <p key={a} className="advertencia">⚠ {a}</p>
          ))}
        </div>
      )}
      {error && <p className="error">{error}</p>}

      {detenidos.length > 0 && (
        <div className="tarjeta detenido">
          <strong>
            {detenidos.length === 1 ? '1 equipo quedó detenido' : `${detenidos.length} equipos quedaron detenidos`}
          </strong>
          <span className="tenue">Falta programar su visita correctiva.</span>
          <ul className="lista">
            {detenidos.map((d) => (
              <li key={d.id}>
                <Link to={`/mantenciones/${d.id}`}>
                  {d.edificio_nombre} · {d.ascensor_identificador}
                </Link>
                <span className="tenue">
                  {' '}{fechaCorta(fechaDe(d.guardado_en_dispositivo))} a las {horaDe(d.guardado_en_dispositivo)}, {d.tecnico_nombre}
                </span>
                <br />
                Falla: {d.falla_descripcion}
              </li>
            ))}
          </ul>
        </div>
      )}

      {resumen && resumen.carga.length > 0 && (
        <details className="tarjeta">
          <summary>Carga por técnico</summary>
          <table className="tabla">
            <thead>
              <tr><th>Técnico</th><th>Equipos</th><th>Máx. diario</th></tr>
            </thead>
            <tbody>
              {resumen.carga.map((c) => {
                const max = Math.max(...Object.values(c.por_dia))
                return (
                  <tr key={c.tecnico}>
                    <td>{c.tecnico}</td>
                    <td>{c.total}</td>
                    <td className={max > c.capacidad ? 'peligro' : ''}>{max} / {c.capacidad}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </details>
      )}

      {visitas && visitas.length > 0 && (
        <div className="filtros">
          <select value={tecnico} onChange={(e) => setTecnico(e.target.value)} aria-label="Técnico">
            <option value="">Todos los técnicos</option>
            {tecnicos.map((t) => <option key={t.id} value={t.id}>{t.nombre}</option>)}
          </select>
        </div>
      )}

      {visitas === null && !error && <p className="tenue">Cargando…</p>}
      {porDia.map(([fecha, edificios]) => (
        <div key={fecha} className="dia">
          <h3>{diaLargo(fecha)}</h3>
          <ul className="lista">
            {[...edificios.values()].map((vs) => (
              <li key={vs[0].edificio_id} className="fila">
                <div>
                  <strong>{vs[0].edificio_nombre}</strong>
                  <span className="tenue">{vs[0].direccion}, {vs[0].comuna}</span>
                  <span className="equipos">
                    {vs.map((v) =>
                      v.registro ? (
                        <Link
                          key={v.id}
                          to={`/mantenciones/${v.registro.id}`}
                          className={`etiqueta ${v.registro.operativo ? 'ok' : 'peligro'}`}
                          title={v.registro.operativo ? 'Mantención realizada' : 'El equipo quedó detenido'}
                        >
                          {v.ascensor_identificador} {v.registro.operativo ? 'realizada' : 'detenido'}
                        </Link>
                      ) : (
                        <span key={v.id} className="etiqueta">{v.ascensor_identificador}</span>
                      ),
                    )}
                  </span>
                </div>
                <span className="tenue derecha">{vs[0].tecnico_nombre}</span>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </section>
  )
}
