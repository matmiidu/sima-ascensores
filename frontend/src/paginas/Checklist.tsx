import { useEffect, useState, type FormEvent } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api'
import DetalleRegistro, { desdeCelular, desdeServidor, type RegistroVista } from '../componentes/DetalleRegistro'
import { diaLargo, fechaCorta, fechaDe, horaDe, hoyLocal } from '../fechas'
import {
  alCambiar,
  borrarBorrador,
  buscarVisita,
  cargarPuntos,
  enviarMantencion,
  guardarBorrador,
  guardarMantencion,
  leerBorrador,
  mantencionesLocales,
  quitar,
  revisarChecklist,
  type Borrador,
  type Faltas,
  type MantencionLocal,
} from '../terreno'
import { RESULTADOS, type PuntoChecklist, type RegistroMantencion, type Resultado, type Sesion, type VisitaDelDia } from '../tipos'

const VACIO: Borrador = { respuestas: {}, operativo: null, falla: '', observaciones: '' }
const SIN_FALTAS: Faltas = { puntos: {} }

const arriba = () => window.scrollTo({ top: 0, behavior: 'smooth' })

/** Checklist de mantención de una visita (H06, requisitos RF-02 y RF-03). */
export default function Checklist({ sesion }: { sesion: Sesion }) {
  const visitaId = Number(useParams().id)
  // undefined = cargando; null = no se encontró
  const [visita, setVisita] = useState<VisitaDelDia | null | undefined>(undefined)
  const [puntos, setPuntos] = useState<PuntoChecklist[]>([])
  const [borrador, setBorrador] = useState<Borrador>(VACIO)
  // Tras un intento fallido, lo que falta se sigue marcando mientras el técnico lo completa.
  const [intentado, setIntentado] = useState(false)
  const [rechazoServidor, setRechazoServidor] = useState('')
  const [guardando, setGuardando] = useState(false)
  const [guardada, setGuardada] = useState<MantencionLocal | null>(null)
  const [enCelular, setEnCelular] = useState<MantencionLocal | null>(null)
  const [registro, setRegistro] = useState<RegistroVista | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    let vigente = true
    async function cargar() {
      try {
        const [v, p, locales] = await Promise.all([buscarVisita(visitaId), cargarPuntos(), mantencionesLocales()])
        if (!vigente) return
        setPuntos(p)
        setEnCelular(locales.find((m) => m.visita === visitaId && m.estado !== 'rechazada') ?? null)
        setBorrador(leerBorrador(visitaId) ?? VACIO)
        setVisita(v)
      } catch (e) {
        if (!vigente) return
        setError((e as Error).message)
        setVisita(null)
      }
    }
    cargar()
    return () => {
      vigente = false
    }
  }, [visitaId])

  // Si la visita ya está registrada, se muestra lo registrado en vez del formulario.
  const yaRegistrada = visita?.estado === 'realizada'
  useEffect(() => {
    if (!yaRegistrada) return
    let vigente = true
    api<RegistroMantencion[]>(`mantenciones/?visita=${visitaId}`)
      .then((lista) => vigente && lista[0] && setRegistro(desdeServidor(lista[0])))
      .catch(() => {})
    return () => {
      vigente = false
    }
  }, [yaRegistrada, visitaId])

  // Si lo guardado en el celular se envía mientras se mira la confirmación, se actualiza.
  useEffect(() => {
    if (!guardada || guardada.estado !== 'pendiente') return
    return alCambiar(() => {
      mantencionesLocales()
        .then((l) => {
          const actual = l.find((m) => m.id_local === guardada.id_local)
          if (actual) setGuardada(actual)
        })
        .catch(() => {})
    })
  }, [guardada])

  function cambiar(cambio: Partial<Borrador>) {
    const nuevo = { ...borrador, ...cambio }
    setBorrador(nuevo)
    guardarBorrador(visitaId, nuevo)
  }

  function responder(punto: number, cambio: Partial<{ resultado: Resultado; comentario: string }>) {
    const actual = borrador.respuestas[punto] ?? { comentario: '' }
    cambiar({ respuestas: { ...borrador.respuestas, [punto]: { ...actual, ...cambio } } })
  }

  async function guardar(e: FormEvent) {
    e.preventDefault()
    if (!visita) return
    setRechazoServidor('')
    if (revisarChecklist(puntos, borrador).mensaje) {
      setIntentado(true)
      arriba()
      return
    }
    setGuardando(true)
    try {
      // Primero queda en el celular; si hay señal se envía de inmediato.
      let m = await guardarMantencion({
        visita: visita.id,
        titulo: `${visita.edificio_nombre} · ${visita.ascensor_identificador}`,
        fecha_visita: visita.fecha,
        respuestas: puntos.map((p) => {
          const r = borrador.respuestas[p.id]
          return { punto: p.id, resultado: r.resultado!, comentario: r.resultado === 'observacion' ? r.comentario.trim() : '' }
        }),
        operativo: borrador.operativo!,
        falla_descripcion: borrador.operativo ? '' : borrador.falla.trim(),
        observaciones: borrador.observaciones.trim(),
      })
      if (navigator.onLine) m = await enviarMantencion(m)
      if (m.estado === 'rechazada') {
        // El servidor no la aceptó: se muestra el motivo y lo respondido se conserva.
        await quitar(m.id_local)
        setRechazoServidor(m.ultimo_error || 'El servidor no aceptó la mantención.')
        cargarPuntos().then(setPuntos).catch(() => {})
        buscarVisita(visita.id).then((v) => v && setVisita(v)).catch(() => {})
      } else {
        borrarBorrador(visita.id)
        setGuardada(m)
      }
    } catch (e) {
      setRechazoServidor(`No se pudo guardar en el celular: ${(e as Error).message}`)
    } finally {
      setGuardando(false)
      arriba()
    }
  }

  if (visita === undefined) return <p className="tenue">Cargando…</p>
  if (visita === null) {
    return (
      <section>
        <Link to="/mis-visitas" className="volver">← Mis visitas</Link>
        <p className="error">{error || 'No se encontró la visita entre tus visitas.'}</p>
      </section>
    )
  }

  const hoy = hoyLocal()
  const titulo = `${visita.edificio_nombre} · ${visita.ascensor_identificador}`
  const encabezado = (
    <>
      <Link to="/mis-visitas" className="volver">← Mis visitas</Link>
      <h1>{titulo}</h1>
      <p className="tenue">
        {visita.direccion}, {visita.comuna} · Visita del {diaLargo(visita.fecha)} · {visita.tecnico_nombre}
      </p>
    </>
  )

  if (guardada) {
    const conObservacion = guardada.respuestas.filter((r) => r.resultado === 'observacion').length
    const enviada = guardada.estado === 'enviada'
    return (
      <section>
        {encabezado}
        <div className={`tarjeta confirmacion ${enviada ? 'ok' : 'alerta'}`}>
          <strong>{enviada ? `Mantención ${guardada.codigo} guardada` : 'Mantención guardada en el celular'}</strong>
          <p>
            {titulo}, {diaLargo(fechaDe(guardada.guardado_en_dispositivo))} a las {horaDe(guardada.guardado_en_dispositivo)},
            técnico {sesion.nombre}.
          </p>
          <p>
            {guardada.respuestas.length} de {puntos.length} puntos respondidos · {conObservacion} con observación ·{' '}
            {guardada.operativo ? 'Equipo operativo' : 'Equipo detenido'}.
          </p>
          {enviada ? (
            <p>La visita quedó <strong>Realizada</strong> en el calendario del jefe técnico.</p>
          ) : (
            <p>No hay señal. Se enviará sola cuando vuelva; hasta entonces el jefe técnico no la ve.</p>
          )}
          {!guardada.operativo && <p>Falla informada: {guardada.falla_descripcion}</p>}
        </div>
        <Link to="/mis-visitas" className="boton primario grande">Volver a mis visitas</Link>
      </section>
    )
  }

  if (yaRegistrada || enCelular) {
    const vista = registro ?? (enCelular ? desdeCelular(enCelular, puntos, sesion.nombre) : null)
    const cuando = vista?.guardado ?? visita.registro?.guardado_en_dispositivo
    return (
      <section>
        {encabezado}
        {rechazoServidor && <p className="error">{rechazoServidor}</p>}
        <p className="aviso">
          Esta visita ya fue registrada{cuando ? ` el ${fechaCorta(fechaDe(cuando))} a las ${horaDe(cuando)}` : ''}. No se
          puede registrar dos veces.
        </p>
        {vista ? <DetalleRegistro registro={vista} /> : <p className="tenue">El detalle se verá cuando vuelva la señal.</p>}
      </section>
    )
  }

  if (visita.estado !== 'programada') {
    return (
      <section>
        {encabezado}
        <p className="aviso">Esta visita quedó como no realizada. Consulta al jefe técnico.</p>
      </section>
    )
  }
  if (visita.fecha > hoy) {
    return (
      <section>
        {encabezado}
        <p className="aviso">
          Esta visita está programada para el {diaLargo(visita.fecha)}. Se podrá registrar desde ese día.
        </p>
      </section>
    )
  }
  if (visita.fecha.slice(0, 7) !== hoy.slice(0, 7)) {
    return (
      <section>
        {encabezado}
        <p className="aviso">Esta visita era de un mes que ya terminó. Avisa al jefe técnico para que la reprograme.</p>
      </section>
    )
  }

  const revision = intentado ? revisarChecklist(puntos, borrador) : null
  const faltas = revision?.faltas ?? SIN_FALTAS
  const rechazo = rechazoServidor || (revision?.mensaje ? `${revision.mensaje} Lo que ya respondiste se conserva.` : '')
  const respondidos = puntos.filter((p) => borrador.respuestas[p.id]?.resultado).length

  return (
    <section>
      {encabezado}
      {visita.fecha < hoy && (
        <p className="aviso">Visita atrasada: estaba programada para el {diaLargo(visita.fecha)}.</p>
      )}
      {rechazo && <p className="error" role="alert">{rechazo}</p>}

      <form className="tarjeta" onSubmit={guardar} noValidate>
        {puntos.map((p, i) => {
          const r = borrador.respuestas[p.id]
          return (
            <fieldset key={p.id} className={`punto ${faltas.puntos[p.id] ? 'falta' : ''}`}>
              <legend>
                {i + 1}. {p.descripcion}
              </legend>
              <div className="opciones">
                {(Object.keys(RESULTADOS) as Resultado[]).map((o) => (
                  <button
                    type="button"
                    key={o}
                    className={r?.resultado === o ? 'elegida' : ''}
                    aria-pressed={r?.resultado === o}
                    onClick={() => responder(p.id, { resultado: o })}
                  >
                    {RESULTADOS[o]}
                  </button>
                ))}
              </div>
              {r?.resultado === 'observacion' && (
                <textarea
                  rows={2}
                  value={r.comentario}
                  onChange={(e) => responder(p.id, { comentario: e.target.value })}
                  placeholder="Escribe la observación"
                  aria-label={`Observación de ${p.descripcion}`}
                  maxLength={300}
                />
              )}
              {faltas.puntos[p.id] && <p className="error">{faltas.puntos[p.id]}</p>}
            </fieldset>
          )
        })}

        <fieldset className={`punto ${faltas.operativo ? 'falta' : ''}`}>
          <legend>¿El equipo quedó operativo?</legend>
          <div className="sino">
            <button
              type="button"
              className={borrador.operativo === true ? 'elegida' : ''}
              aria-pressed={borrador.operativo === true}
              onClick={() => cambiar({ operativo: true })}
            >
              Sí
            </button>
            <button
              type="button"
              className={borrador.operativo === false ? 'elegida' : ''}
              aria-pressed={borrador.operativo === false}
              onClick={() => cambiar({ operativo: false })}
            >
              No, quedó detenido
            </button>
          </div>
          {faltas.operativo && <p className="error">{faltas.operativo}</p>}
        </fieldset>

        {borrador.operativo === false && (
          <label className={faltas.falla ? 'falta' : ''}>
            Describe la falla (obligatorio si el equipo quedó detenido)
            <textarea rows={3} value={borrador.falla} onChange={(e) => cambiar({ falla: e.target.value })} />
            {faltas.falla && <span className="error">{faltas.falla}</span>}
          </label>
        )}

        <label>
          Observaciones generales
          <textarea rows={2} value={borrador.observaciones} onChange={(e) => cambiar({ observaciones: e.target.value })} />
        </label>

        <p className="tenue centro">
          {respondidos} de {puntos.length} puntos respondidos
        </p>
        <button className="primario grande" disabled={guardando}>
          {guardando ? 'Guardando…' : 'Guardar mantención'}
        </button>
      </form>
    </section>
  )
}
