import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, descargar } from '../api'
import { nombreMes } from '../fechas'
import type { InformeEdificio, InformesDelMes } from '../tipos'

function mesActual() {
  const d = new Date()
  return { anio: d.getFullYear(), mes: d.getMonth() + 1 }
}

const plural = (n: number, uno: string, varios: string) => `${n} ${n === 1 ? uno : varios}`

/** Correo ya escrito para el administrador; el PDF descargado se adjunta en la aplicación de correo. */
function correo(e: InformeEdificio, mes: string) {
  const asunto = `Informe de mantención de ${e.nombre} · ${mes}`
  const cuerpo =
    `Estimado(a) ${e.administrador.nombre || 'administrador(a)'}:\n\n` +
    `Adjuntamos el informe de mantención de ${mes} de los ascensores de ${e.nombre} (${e.direccion}, ${e.comuna}), ` +
    'con las tareas revisadas, las observaciones y el estado en que quedó cada equipo. ' +
    'Le sugerimos archivarlo en la carpeta de ascensores del edificio, que el certificador revisa en cada certificación.\n\n' +
    'Saludos,\nAscensores Altavía'
  return `mailto:${e.administrador.correo}?subject=${encodeURIComponent(asunto)}&body=${encodeURIComponent(cuerpo)}`
}

function Edificio({ e, clave, mes }: { e: InformeEdificio; clave: string; mes: string }) {
  const [estado, setEstado] = useState<'' | 'bajando' | 'listo'>('')
  const [error, setError] = useState('')

  async function bajar() {
    setEstado('bajando')
    setError('')
    try {
      await descargar(`informes/${e.id}/pdf/?mes=${clave}`, e.archivo)
      setEstado('listo')
    } catch (err) {
      setError((err as Error).message)
      setEstado('')
    }
  }

  return (
    <div className={`tarjeta ${e.detenidos ? 'detenido' : e.completo ? 'ok' : 'alerta'}`}>
      <strong>
        <Link to={`/cartera/${e.id}`}>{e.nombre}</Link>
      </strong>
      <p className="tenue">
        {e.comuna}
        {e.tecnico && ` · ${e.tecnico}`}
      </p>
      <p>
        {e.registradas} de {plural(e.visitas, 'mantención registrada', 'mantenciones registradas')}{' '}
        {e.completo ? (
          <span className="etiqueta ok">Completo</span>
        ) : (
          <span className="etiqueta alerta">Faltan {e.faltan}</span>
        )}{' '}
        {e.detenidos > 0 && <span className="etiqueta peligro">{plural(e.detenidos, 'detenido', 'detenidos')}</span>}
      </p>
      {e.registradas > 0 ? (
        <>
          <button className={e.completo ? 'primario grande' : 'grande'} onClick={bajar} disabled={estado === 'bajando'}>
            {estado === 'bajando' ? 'Preparando el PDF…' : e.completo ? 'Descargar informe (PDF)' : 'Descargar informe parcial (PDF)'}
          </button>
          {estado === 'listo' &&
            (e.administrador.correo ? (
              <p>
                Descargado: {e.archivo}.{' '}
                <a href={correo(e, mes)}>Escribir al administrador</a> y adjuntar el archivo.
              </p>
            ) : (
              <p className="advertencia">Descargado. El edificio no tiene correo del administrador registrado.</p>
            ))}
        </>
      ) : (
        <p className="tenue">Todavía no hay mantenciones registradas este mes.</p>
      )}
      {error && <p className="error">{error}</p>}
    </div>
  )
}

/** Informe mensual de mantención en PDF por edificio, para enviarlo al administrador (H09). */
export default function Informes() {
  const [{ anio, mes }, setPeriodo] = useState(mesActual)
  const [datos, setDatos] = useState<InformesDelMes | null>(null)
  const [buscar, setBuscar] = useState('')
  const [filtro, setFiltro] = useState('')
  const [error, setError] = useState('')

  const clave = `${anio}-${String(mes).padStart(2, '0')}`

  useEffect(() => {
    setDatos(null)
    setError('')
    api<InformesDelMes>(`informes/?mes=${clave}`)
      .then(setDatos)
      .catch((e) => setError((e as Error).message))
  }, [clave])

  function mover(delta: number) {
    const d = new Date(anio, mes - 1 + delta, 1)
    setPeriodo({ anio: d.getFullYear(), mes: d.getMonth() + 1 })
  }

  const edificios = useMemo(() => {
    const texto = buscar.trim().toLowerCase()
    return (datos?.edificios ?? []).filter(
      (e) =>
        (!texto || `${e.nombre} ${e.comuna}`.toLowerCase().includes(texto)) &&
        (!filtro ||
          (filtro === 'completos' && e.completo) ||
          (filtro === 'faltan' && !e.completo) ||
          (filtro === 'detenidos' && e.detenidos > 0)),
    )
  }, [datos, buscar, filtro])

  const completos = (datos?.edificios ?? []).filter((e) => e.completo).length

  return (
    <section>
      <div className="encabezado">
        <button onClick={() => mover(-1)} aria-label="Mes anterior">‹</button>
        <h1 className="mes">{nombreMes(anio, mes)}</h1>
        <button onClick={() => mover(1)} aria-label="Mes siguiente">›</button>
      </div>

      {datos && (
        <p className="tenue">
          {datos.edificios.length === 0
            ? 'No hay visitas programadas este mes.'
            : `${plural(completos, 'edificio', 'edificios')} con el informe completo de ${datos.edificios.length}. ` +
              'Un informe se puede descargar antes de completarse: sale marcado como parcial.'}
        </p>
      )}

      {datos && datos.edificios.length > 0 && (
        <div className="filtros">
          <input type="search" placeholder="Buscar edificio o comuna" value={buscar} onChange={(e) => setBuscar(e.target.value)} />
          <select value={filtro} onChange={(e) => setFiltro(e.target.value)} aria-label="Qué informes mostrar">
            <option value="">Todos</option>
            <option value="completos">Solo completos</option>
            <option value="faltan">Con mantenciones por registrar</option>
            <option value="detenidos">Con equipos detenidos</option>
          </select>
        </div>
      )}

      {error && <p className="error">{error}</p>}
      {datos === null && !error && <p className="tenue">Cargando…</p>}
      {datos && datos.edificios.length > 0 && edificios.length === 0 && (
        <p className="tenue">Ningún edificio calza con la búsqueda.</p>
      )}
      {datos && edificios.map((e) => <Edificio key={e.id} e={e} clave={clave} mes={datos.nombre_mes} />)}
    </section>
  )
}
