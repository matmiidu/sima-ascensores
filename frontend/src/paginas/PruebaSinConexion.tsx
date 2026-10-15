import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { api } from '../api'
import { borrarEnviados, guardar, listar, sincronizar, type ChecklistLocal } from '../sinConexion'
import type { Ascensor } from '../tipos'
import { useEnLinea } from '../useEnLinea'

// Puntos de prueba. El checklist definitivo se define con el jefe técnico en H06.
const PUNTOS = [
  'Frenos y paracaídas',
  'Puertas de piso y de cabina',
  'Cables y limitador de velocidad',
  'Iluminación de la cabina',
  'Alarma y citófono',
]
const OPCIONES = ['Bien', 'Con observación', 'No aplica']

// Copia local de la lista de ascensores, para elegir el equipo sin señal.
const CLAVE_ASCENSORES = 'sima.ascensores'
function ascensoresGuardados(): Ascensor[] {
  try {
    return JSON.parse(localStorage.getItem(CLAVE_ASCENSORES) || '[]')
  } catch {
    return []
  }
}

const hora = (iso: string) => new Date(iso).toLocaleString('es-CL', { dateStyle: 'short', timeStyle: 'short' })

export default function PruebaSinConexion() {
  const enLinea = useEnLinea()
  const [ascensores, setAscensores] = useState<Ascensor[]>([])
  const [ascensor, setAscensor] = useState('')
  const [respuestas, setRespuestas] = useState<Record<string, string>>({})
  const [observaciones, setObservaciones] = useState('')
  const [registros, setRegistros] = useState<ChecklistLocal[]>([])
  const [mensaje, setMensaje] = useState('')

  const refrescar = useCallback(async () => {
    setRegistros((await listar()).sort((a, b) => b.guardado_en_dispositivo.localeCompare(a.guardado_en_dispositivo)))
  }, [])

  const enviarPendientes = useCallback(async () => {
    const r = await sincronizar()
    if (r.enviados) setMensaje(`Se enviaron ${r.enviados} checklist(s) al recuperar la señal.`)
    await refrescar()
  }, [refrescar])

  useEffect(() => {
    refrescar()
    setAscensores(ascensoresGuardados())
    api<Ascensor[]>('ascensores/')
      .then((lista) => {
        setAscensores(lista)
        try {
          localStorage.setItem(CLAVE_ASCENSORES, JSON.stringify(lista))
        } catch {
          /* sin almacenamiento: la lista solo sirve con señal */
        }
      })
      .catch(() => {})
  }, [refrescar])

  // Al volver la señal se envía lo pendiente sin que el técnico haga nada, y
  // mientras quede algo pendiente se reintenta cada 20 segundos.
  useEffect(() => {
    if (!enLinea) return
    enviarPendientes()
    const t = setInterval(enviarPendientes, 20000)
    return () => clearInterval(t)
  }, [enLinea, enviarPendientes])

  async function guardarChecklist(e: FormEvent) {
    e.preventDefault()
    const a = ascensores.find((x) => String(x.id) === ascensor)
    await guardar({
      ascensor: a ? a.id : null,
      ascensor_nombre: a ? `${a.edificio_nombre} · ${a.identificador}` : 'Sin ascensor',
      respuestas,
      observaciones,
    })
    setRespuestas({})
    setObservaciones('')
    setMensaje(enLinea ? 'Guardado. Enviando…' : 'Guardado en el celular. Se enviará al recuperar la señal.')
    await refrescar()
    if (navigator.onLine) enviarPendientes()
  }

  const pendientes = registros.filter((r) => !r.enviado)
  const completo = PUNTOS.every((p) => respuestas[p])

  return (
    <section>
      <h1>Checklist de prueba</h1>
      <p className="tenue">
        Prueba de concepto S01: guardar sin señal y enviar al volver. No es el checklist definitivo.
      </p>
      <div className={`tarjeta estado ${enLinea ? 'ok' : 'alerta'}`}>
        <strong>{enLinea ? 'Con señal' : 'Sin señal'}</strong>
        <span>{pendientes.length} pendiente(s) de envío</span>
        {enLinea && pendientes.length > 0 && <button onClick={enviarPendientes}>Enviar ahora</button>}
      </div>
      {mensaje && <p>{mensaje}</p>}

      <form className="tarjeta" onSubmit={guardarChecklist}>
        <label>
          Ascensor
          <select value={ascensor} onChange={(e) => setAscensor(e.target.value)}>
            <option value="">{ascensores.length ? 'Elegir…' : 'Sin lista (se guarda sin ascensor)'}</option>
            {ascensores.map((a) => (
              <option key={a.id} value={a.id}>{a.edificio_nombre} · {a.identificador}</option>
            ))}
          </select>
        </label>
        {PUNTOS.map((p) => (
          <fieldset key={p} className="punto">
            <legend>{p}</legend>
            <div className="opciones">
              {OPCIONES.map((o) => (
                <button
                  type="button"
                  key={o}
                  className={respuestas[p] === o ? 'elegida' : ''}
                  onClick={() => setRespuestas((r) => ({ ...r, [p]: o }))}
                >
                  {o}
                </button>
              ))}
            </div>
          </fieldset>
        ))}
        <label>
          Observaciones
          <textarea value={observaciones} onChange={(e) => setObservaciones(e.target.value)} rows={3} />
        </label>
        <button className="primario grande" disabled={!completo}>
          Guardar checklist
        </button>
      </form>

      <div className="encabezado">
        <h2>Registros en este celular</h2>
        {registros.some((r) => r.enviado) && <button onClick={() => borrarEnviados().then(refrescar)}>Limpiar enviados</button>}
      </div>
      <ul className="lista">
        {registros.map((r) => (
          <li key={r.id_local} className="fila">
            <div>
              <strong>{r.ascensor_nombre}</strong>
              <span className="tenue">Guardado {hora(r.guardado_en_dispositivo)}</span>
              {r.ultimo_error && <span className="error">Último intento: {r.ultimo_error}</span>}
            </div>
            <span className={`etiqueta ${r.enviado ? 'ok' : 'alerta'}`}>
              {r.enviado ? `Enviado ${hora(r.enviado)}` : 'Pendiente'}
            </span>
          </li>
        ))}
        {registros.length === 0 && <li className="tenue">Todavía no hay registros.</li>}
      </ul>
    </section>
  )
}
