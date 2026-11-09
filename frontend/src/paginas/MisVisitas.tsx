import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { diaLargo, horaDe, mayuscula, sumarDias } from '../fechas'
import { alCambiar, cargarDia, cargarPuntos, quitar, sincronizar, type DiaCargado, type MantencionLocal } from '../terreno'
import type { Sesion, VisitaDelDia } from '../tipos'
import { useEnLinea } from '../useEnLinea'
import { useMantencionesLocales } from '../useTerreno'

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

type Locales = Map<number, MantencionLocal>

/** Una visita cuenta como registrada si el servidor la tiene Realizada o si está guardada en el celular. */
const registrada = (v: VisitaDelDia, locales: Locales) =>
  v.estado === 'realizada' || ['pendiente', 'enviada'].includes(locales.get(v.id)?.estado ?? '')

function Estado({ visita, hoy, local }: { visita: VisitaDelDia; hoy: string; local?: MantencionLocal }) {
  const ruta = `/mis-visitas/${visita.id}`
  if (visita.estado === 'realizada' || local?.estado === 'enviada') {
    const hora = visita.registro?.guardado_en_dispositivo ?? local?.guardado_en_dispositivo
    const operativo = visita.registro?.operativo ?? local?.operativo ?? true
    return (
      <Link to={ruta} className={`etiqueta ${operativo ? 'ok' : 'peligro'}`}>
        {operativo ? 'Realizada' : 'Detenido'}{hora ? ` ${horaDe(hora)}` : ''}
      </Link>
    )
  }
  if (local?.estado === 'pendiente') return <Link to={ruta} className="etiqueta alerta">En el celular</Link>
  if (visita.estado === 'no_realizada') return <span className="etiqueta peligro">No realizada</span>
  if (visita.fecha > hoy) return <span className="etiqueta">Programada</span>
  return <Link to={ruta} className="boton primario">Registrar</Link>
}

function Edificio({ visitas, hoy, locales, conFecha }: { visitas: VisitaDelDia[]; hoy: string; locales: Locales; conFecha?: boolean }) {
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
              <Estado visita={v} hoy={hoy} local={locales.get(v.id)} />
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

/** Visitas del técnico para un día (H04), con el acceso al checklist de cada una (H06). */
export default function MisVisitas({ sesion }: { sesion: Sesion }) {
  // Sin fecha elegida se pide el día de hoy, que lo decide el servidor.
  const [fecha, setFecha] = useState('')
  const [dia, setDia] = useState<DiaCargado | null>(null)
  const [error, setError] = useState('')
  const enLinea = useEnLinea()
  const guardadas = useMantencionesLocales()

  const cargar = useCallback(async () => {
    try {
      setDia(await cargarDia(fecha))
      setError('')
    } catch (e) {
      setError((e as Error).message)
    }
  }, [fecha])

  // Se vuelve a pedir la lista al cambiar de día, al volver la señal y cuando
  // termina un envío, para que lo recién enviado aparezca como Realizada.
  useEffect(() => {
    cargar()
  }, [cargar, enLinea])
  useEffect(() => alCambiar((aviso) => aviso === 'sincronizado' && cargar()), [cargar])

  // Con señal se deja a mano el checklist, para poder abrirlo después sin señal.
  useEffect(() => {
    if (enLinea) cargarPuntos().catch(() => {})
  }, [enLinea])

  if (!dia) return <p className={error ? 'error' : 'tenue'}>{error || 'Cargando…'}</p>

  const { datos, copiaDe } = dia
  const locales: Locales = new Map(guardadas.map((m) => [m.visita, m]))
  const pendientes = guardadas.filter((m) => m.estado === 'pendiente')
  const rechazadas = guardadas.filter((m) => m.estado === 'rechazada')
  const esHoy = datos.fecha === datos.hoy
  const total = datos.visitas.length
  const registradas = datos.visitas.filter((v) => registrada(v, locales)).length

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
      {copiaDe && <p className="aviso">Sin señal: se muestra la lista guardada en el celular a las {horaDe(copiaDe)}.</p>}

      {pendientes.length > 0 && (
        <div className="tarjeta estado alerta">
          <strong>
            {pendientes.length === 1
              ? '1 mantención guardada en el celular, sin enviar'
              : `${pendientes.length} mantenciones guardadas en el celular, sin enviar`}
          </strong>
          <span className="tenue">{enLinea ? 'Se están enviando.' : 'Se enviarán solas cuando vuelva la señal.'}</span>
          {enLinea && <button onClick={() => sincronizar()}>Enviar ahora</button>}
        </div>
      )}
      {rechazadas.map((m) => (
        <div key={m.id_local} className="tarjeta estado detenido">
          <strong>{m.titulo}: el servidor no aceptó la mantención</strong>
          <span>{m.ultimo_error}</span>
          <button onClick={() => quitar(m.id_local)}>Entendido</button>
        </div>
      ))}

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
        <Edificio key={vs[0].edificio_id} visitas={vs} hoy={datos.hoy} locales={locales} />
      ))}

      {esHoy && datos.atrasadas.length > 0 && (
        <>
          <h2 className="separado">Atrasadas de este mes ({datos.atrasadas.filter((v) => !registrada(v, locales)).length})</h2>
          <p className="tenue">Visitas de días anteriores que siguen sin registrar. Todavía se pueden registrar.</p>
          {porEdificio(datos.atrasadas).map((vs) => (
            <Edificio key={`${vs[0].fecha}/${vs[0].edificio_id}`} visitas={vs} hoy={datos.hoy} locales={locales} conFecha />
          ))}
        </>
      )}
    </section>
  )
}
