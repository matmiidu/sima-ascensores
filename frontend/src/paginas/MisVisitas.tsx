import { useCallback, useEffect, useState } from 'react'
import { api } from '../api'
import { diaLargo, mayuscula, sumarDias } from '../fechas'
import type { MisVisitasDelDia, Sesion, VisitaDelDia } from '../tipos'

const ESTADOS = {
  programada: { clase: '', texto: 'Programada' },
  realizada: { clase: 'ok', texto: 'Realizada' },
  no_realizada: { clase: 'peligro', texto: 'No realizada' },
}

// Los ascensores de un edificio se visitan juntos: se muestran bajo su edificio.
function porEdificio(visitas: VisitaDelDia[]) {
  const grupos = new Map<string, VisitaDelDia[]>()
  for (const v of visitas) {
    const clave = `${v.fecha}/${v.edificio_id}`
    if (!grupos.has(clave)) grupos.set(clave, [])
    grupos.get(clave)!.push(v)
  }
  return [...grupos.values()]
}

function Edificio({ visitas, conFecha }: { visitas: VisitaDelDia[]; conFecha?: boolean }) {
  const e = visitas[0]
  return (
    <div className="edificio">
      <h3>
        {e.edificio_nombre}
        {conFecha && <span className="tenue"> · {diaLargo(e.fecha)}</span>}
      </h3>
      <ul className="lista">
        {visitas.map((v, i) => (
          <li key={v.id} className="fila">
            <div>
              <strong>{v.ascensor_identificador}</strong>
              <span className="tenue">
                {i === 0 && `${v.direccion}, ${v.comuna} · `}
                {v.marca ? `${v.marca}, ` : ''}
                {v.paradas} paradas
              </span>
            </div>
            <span className="derecha">
              <span className={`etiqueta ${ESTADOS[v.estado].clase}`}>{ESTADOS[v.estado].texto}</span>
            </span>
          </li>
        ))}
      </ul>
      {e.administrador_nombre && (
        <p className="tenue">
          Administrador del {e.edificio_nombre}: {e.administrador_nombre}
          {e.administrador_telefono && (
            <>
              {' '}· <a href={`tel:${e.administrador_telefono.replace(/\s/g, '')}`}>{e.administrador_telefono}</a>
            </>
          )}
        </p>
      )}
    </div>
  )
}

export default function MisVisitas({ sesion }: { sesion: Sesion }) {
  // Sin fecha elegida se pide el día de hoy, que lo decide el servidor.
  const [fecha, setFecha] = useState('')
  const [datos, setDatos] = useState<MisVisitasDelDia | null>(null)
  const [error, setError] = useState('')

  const cargar = useCallback(async () => {
    setError('')
    try {
      setDatos(await api<MisVisitasDelDia>(`mis-visitas/${fecha ? `?fecha=${fecha}` : ''}`))
    } catch (e) {
      setError((e as Error).message)
    }
  }, [fecha])

  useEffect(() => {
    cargar()
  }, [cargar])

  if (!datos) return <p className={error ? 'error' : 'tenue'}>{error || 'Cargando…'}</p>

  const esHoy = datos.fecha === datos.hoy
  const registradas = datos.visitas.filter((v) => v.estado === 'realizada').length
  const total = datos.visitas.length

  return (
    <section>
      <div className="encabezado">
        <button onClick={() => setFecha(sumarDias(datos.fecha, -1))} aria-label="Día anterior">‹</button>
        <h1 className="mes">{esHoy ? 'Mis visitas de hoy' : 'Mis visitas'}</h1>
        <button onClick={() => setFecha(sumarDias(datos.fecha, 1))} aria-label="Día siguiente">›</button>
      </div>
      <p className="tenue centro">
        {mayuscula(diaLargo(datos.fecha))} · {sesion.nombre}
        {!esHoy && (
          <>
            {' '}· <button className="enlace" onClick={() => setFecha('')}>Volver a hoy</button>
          </>
        )}
      </p>
      {error && <p className="error">{error}</p>}

      {total > 0 ? (
        <div className={`tarjeta estado ${registradas === total ? 'ok' : 'alerta'}`}>
          <strong>
            {registradas} de {total} equipos registrados
          </strong>
        </div>
      ) : (
        <div className="tarjeta estado">
          <strong>No tienes visitas programadas para {esHoy ? 'hoy' : 'este día'}.</strong>
          {datos.proxima_fecha && (
            <button onClick={() => setFecha(datos.proxima_fecha!)}>
              Ver la siguiente: {diaLargo(datos.proxima_fecha)}
            </button>
          )}
        </div>
      )}

      {porEdificio(datos.visitas).map((vs) => (
        <Edificio key={vs[0].edificio_id} visitas={vs} />
      ))}

      {esHoy && datos.atrasadas.length > 0 && (
        <>
          <h2 className="separado">Atrasadas de este mes ({datos.atrasadas.length})</h2>
          <p className="tenue">Visitas de días anteriores que siguen sin registrar.</p>
          {porEdificio(datos.atrasadas).map((vs) => (
            <Edificio key={`${vs[0].fecha}/${vs[0].edificio_id}`} visitas={vs} conFecha />
          ))}
        </>
      )}
    </section>
  )
}
