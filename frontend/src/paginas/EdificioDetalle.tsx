import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api, enviar } from '../api'
import { TIPOS_ASCENSOR, USOS_ASCENSOR, type Edificio, type RegistroMantencion } from '../tipos'
import { fechaCorta, fechaDe, horaDe } from '../fechas'

const VACIO = {
  identificador: '',
  tipo: 'electrico',
  uso: 'pasajeros',
  marca: '',
  numero_serie: '',
  paradas: '2',
  capacidad_kg: '',
  vencimiento_certificacion: '',
}

function estadoCertificacion(vence: string | null) {
  // La fecha es la de la certificación (cada uno o dos años), no la de la mantención mensual.
  if (!vence) return { clase: 'alerta', texto: 'Certificación sin fecha' }
  const dias = Math.round((new Date(vence + 'T12:00').getTime() - Date.now()) / 86400000)
  if (dias < 0) return { clase: 'peligro', texto: `Certificación vencida ${fechaCorta(vence)}` }
  if (dias <= 60) return { clase: 'alerta', texto: `Certificación vence ${fechaCorta(vence)}` }
  return { clase: 'ok', texto: `Certificación vigente hasta ${fechaCorta(vence)}` }
}

export default function EdificioDetalle() {
  const { id } = useParams()
  const [edificio, setEdificio] = useState<Edificio | null>(null)
  const [mantenciones, setMantenciones] = useState<RegistroMantencion[]>([])
  const [formulario, setFormulario] = useState<typeof VACIO | null>(null)
  const [error, setError] = useState('')

  const cargar = useCallback(() => {
    api<Edificio>(`edificios/${id}/`).then(setEdificio).catch((e) => setError(e.message))
    api<RegistroMantencion[]>(`mantenciones/?edificio=${id}`).then(setMantenciones).catch(() => {})
  }, [id])

  useEffect(cargar, [cargar])

  async function guardar(e: FormEvent) {
    e.preventDefault()
    if (!formulario) return
    setError('')
    try {
      await enviar('ascensores/', {
        ...formulario,
        edificio: Number(id),
        paradas: Number(formulario.paradas),
        capacidad_kg: formulario.capacidad_kg ? Number(formulario.capacidad_kg) : null,
        vencimiento_certificacion: formulario.vencimiento_certificacion || null,
      })
      setFormulario(null)
      cargar()
    } catch (e) {
      setError((e as Error).message)
    }
  }

  const campo = (k: keyof typeof VACIO) => ({
    value: formulario?.[k] ?? '',
    onChange: (e: { target: { value: string } }) => setFormulario((f) => f && { ...f, [k]: e.target.value }),
  })

  if (!edificio) return <p className="tenue">{error || 'Cargando…'}</p>

  return (
    <section>
      <Link to="/cartera" className="volver">← Cartera</Link>
      <h1>{edificio.nombre}</h1>
      <p>
        {edificio.direccion}, {edificio.comuna} · <span className={`etiqueta uso-${edificio.tipo_uso}`}>{edificio.tipo_uso_display}</span>
      </p>
      <dl className="datos">
        <dt>Técnico</dt>
        <dd>{edificio.tecnico_nombre ?? 'Sin asignar'}</dd>
        <dt>Administrador</dt>
        <dd>
          {edificio.administrador_nombre || '—'}
          {edificio.administrador_telefono && <> · <a href={`tel:${edificio.administrador_telefono}`}>{edificio.administrador_telefono}</a></>}
        </dd>
        <dt>Certificación</dt>
        <dd>{edificio.tipo_uso === 'residencial' ? 'Cada dos años (residencial)' : 'Cada año (otros usos)'}</dd>
      </dl>

      <div className="encabezado">
        <h2>Ascensores ({edificio.ascensores.length})</h2>
        {!formulario && (
          <button className="primario" onClick={() => setFormulario({ ...VACIO, identificador: `A${edificio.ascensores.length + 1}` })}>
            + Ascensor
          </button>
        )}
      </div>

      {formulario && (
        <form className="tarjeta" onSubmit={guardar}>
          <h2>Nuevo ascensor</h2>
          <label>
            Identificador en el edificio
            <input {...campo('identificador')} required />
          </label>
          <label>
            Tipo
            <select {...campo('tipo')}>
              {Object.entries(TIPOS_ASCENSOR).map(([v, t]) => <option key={v} value={v}>{t}</option>)}
            </select>
          </label>
          <label>
            Uso
            <select {...campo('uso')}>
              {Object.entries(USOS_ASCENSOR).map(([v, t]) => <option key={v} value={v}>{t}</option>)}
            </select>
          </label>
          <label>
            Marca
            <input {...campo('marca')} />
          </label>
          <label>
            Número de serie
            <input {...campo('numero_serie')} />
          </label>
          <div className="dos">
            <label>
              Paradas
              <input type="number" min={2} {...campo('paradas')} required />
            </label>
            <label>
              Capacidad (kg)
              <input type="number" min={0} {...campo('capacidad_kg')} />
            </label>
          </div>
          <label>
            Vencimiento de la certificación
            <input type="date" {...campo('vencimiento_certificacion')} />
          </label>
          {error && <p className="error">{error}</p>}
          <div className="acciones">
            <button type="button" onClick={() => setFormulario(null)}>Cancelar</button>
            <button className="primario">Guardar</button>
          </div>
        </form>
      )}

      <ul className="lista">
        {edificio.ascensores.map((a) => {
          const cert = estadoCertificacion(a.vencimiento_certificacion)
          // Las mantenciones vienen de la más reciente a la más antigua: la primera del ascensor es la última.
          const ultima = mantenciones.find((m) => m.ascensor === a.id)
          return (
            <li key={a.id} className={`fila ${a.activo ? '' : 'inactivo'}`}>
              <div>
                <strong>{a.identificador}</strong>
                <span className="tenue">
                  {a.tipo_display} · {a.uso_display} · {a.paradas} paradas{a.marca && ` · ${a.marca}`}
                </span>
              </div>
              <span className="derecha">
                {ultima && !ultima.operativo && (
                  <Link to={`/mantenciones/${ultima.id}`} className="etiqueta peligro">
                    Detenido desde {fechaCorta(fechaDe(ultima.guardado_en_dispositivo))}
                  </Link>
                )}
                <span className={`etiqueta ${cert.clase}`}>{cert.texto}</span>
              </span>
            </li>
          )
        })}
        {edificio.ascensores.length === 0 && <li className="tenue">Este edificio todavía no tiene ascensores.</li>}
      </ul>

      {mantenciones.length > 0 && (
        <>
          <h2 className="separado">Mantenciones registradas ({mantenciones.length})</h2>
          <ul className="lista">
            {mantenciones.map((m) => (
              <li key={m.id}>
                <Link to={`/mantenciones/${m.id}`} className="fila">
                  <div>
                    <strong>
                      {m.ascensor_identificador} · {m.codigo}
                    </strong>
                    <span className="tenue">
                      {fechaCorta(fechaDe(m.guardado_en_dispositivo))} a las {horaDe(m.guardado_en_dispositivo)}, {m.tecnico_nombre}
                    </span>
                  </div>
                  <span className={`etiqueta ${m.operativo ? 'ok' : 'peligro'}`}>{m.operativo ? 'Operativo' : 'Detenido'}</span>
                </Link>
              </li>
            ))}
          </ul>
        </>
      )}
    </section>
  )
}
