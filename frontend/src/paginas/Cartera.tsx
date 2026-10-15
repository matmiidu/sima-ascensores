import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { api, enviar } from '../api'
import { TIPOS_USO, type Edificio, type Tecnico, type TipoUso } from '../tipos'

const VACIO = {
  nombre: '',
  direccion: '',
  comuna: '',
  tipo_uso: '' as TipoUso | '',
  administrador_nombre: '',
  administrador_correo: '',
  administrador_telefono: '',
  tecnico_asignado: '',
}

export default function Cartera() {
  const [edificios, setEdificios] = useState<Edificio[] | null>(null)
  const [tecnicos, setTecnicos] = useState<Tecnico[]>([])
  const [q, setQ] = useState('')
  const [tipo, setTipo] = useState('')
  const [formulario, setFormulario] = useState<typeof VACIO | null>(null)
  const [error, setError] = useState('')

  const cargar = useCallback(async () => {
    const params = new URLSearchParams()
    if (q) params.set('q', q)
    if (tipo) params.set('tipo_uso', tipo)
    try {
      setEdificios(await api<Edificio[]>(`edificios/?${params}`))
    } catch (e) {
      setError((e as Error).message)
    }
  }, [q, tipo])

  useEffect(() => {
    const t = setTimeout(cargar, 250)
    return () => clearTimeout(t)
  }, [cargar])

  useEffect(() => {
    api<Tecnico[]>('tecnicos/').then(setTecnicos).catch(() => {})
  }, [])

  async function guardar(e: FormEvent) {
    e.preventDefault()
    if (!formulario) return
    setError('')
    try {
      await enviar('edificios/', {
        ...formulario,
        tecnico_asignado: formulario.tecnico_asignado ? Number(formulario.tecnico_asignado) : null,
      })
      setFormulario(null)
      cargar()
    } catch (e) {
      setError((e as Error).message)
    }
  }

  const total = edificios?.reduce((s, e) => s + e.total_ascensores, 0) ?? 0
  const campo = (k: keyof typeof VACIO) => ({
    value: formulario?.[k] ?? '',
    onChange: (e: { target: { value: string } }) => setFormulario((f) => f && { ...f, [k]: e.target.value }),
  })

  return (
    <section>
      <div className="encabezado">
        <h1>Cartera</h1>
        {!formulario && (
          <button className="primario" onClick={() => setFormulario({ ...VACIO })}>
            + Edificio
          </button>
        )}
      </div>

      {formulario && (
        <form className="tarjeta" onSubmit={guardar}>
          <h2>Nuevo edificio</h2>
          <label>
            Nombre
            <input {...campo('nombre')} required />
          </label>
          <label>
            Dirección
            <input {...campo('direccion')} required placeholder="Calle y número" />
          </label>
          <label>
            Comuna
            <input {...campo('comuna')} required />
          </label>
          <label>
            Tipo de uso
            <select {...campo('tipo_uso')} required>
              <option value="">Elegir…</option>
              {Object.entries(TIPOS_USO).map(([v, t]) => (
                <option key={v} value={v}>{t}</option>
              ))}
            </select>
          </label>
          <label>
            Técnico asignado
            <select {...campo('tecnico_asignado')}>
              <option value="">Sin asignar</option>
              {tecnicos.map((t) => (
                <option key={t.id} value={t.id}>{t.nombre}</option>
              ))}
            </select>
          </label>
          <label>
            Administrador
            <input {...campo('administrador_nombre')} />
          </label>
          <label>
            Correo del administrador
            <input type="email" {...campo('administrador_correo')} />
          </label>
          <label>
            Teléfono del administrador
            <input type="tel" {...campo('administrador_telefono')} />
          </label>
          {error && <p className="error">{error}</p>}
          <div className="acciones">
            <button type="button" onClick={() => setFormulario(null)}>Cancelar</button>
            <button className="primario">Guardar</button>
          </div>
        </form>
      )}

      <div className="filtros">
        <input type="search" placeholder="Buscar por nombre, dirección o comuna" value={q} onChange={(e) => setQ(e.target.value)} />
        <select value={tipo} onChange={(e) => setTipo(e.target.value)} aria-label="Tipo de uso">
          <option value="">Todos los usos</option>
          {Object.entries(TIPOS_USO).map(([v, t]) => (
            <option key={v} value={v}>{t}</option>
          ))}
        </select>
      </div>

      {!formulario && error && <p className="error">{error}</p>}
      {edificios === null ? (
        <p className="tenue">Cargando…</p>
      ) : (
        <>
          <p className="tenue">
            {edificios.length} edificios · {total} ascensores
          </p>
          <ul className="lista">
            {edificios.map((e) => (
              <li key={e.id}>
                <Link to={`/cartera/${e.id}`} className="fila">
                  <div>
                    <strong>{e.nombre}</strong>
                    <span className="tenue">
                      {e.direccion}, {e.comuna}
                    </span>
                  </div>
                  <div className="derecha">
                    <span className={`etiqueta uso-${e.tipo_uso}`}>{e.tipo_uso_display}</span>
                    <span className="tenue">{e.total_ascensores} asc.</span>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        </>
      )}
    </section>
  )
}
