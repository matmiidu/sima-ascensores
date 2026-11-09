import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api } from '../api'
import DetalleRegistro, { desdeServidor } from '../componentes/DetalleRegistro'
import { diaLargo } from '../fechas'
import type { RegistroMantencion } from '../tipos'

/** Una mantención registrada, tal como la consulta el jefe técnico (H06). */
export default function Mantencion() {
  const { id } = useParams()
  const navegar = useNavigate()
  const [registro, setRegistro] = useState<RegistroMantencion | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api<RegistroMantencion>(`mantenciones/${id}/`)
      .then(setRegistro)
      .catch((e) => setError(e.message))
  }, [id])

  if (!registro) return <p className={error ? 'error' : 'tenue'}>{error || 'Cargando…'}</p>

  return (
    <section>
      <button className="enlace volver" onClick={() => navegar(-1)}>← Volver</button>
      <h1>
        {registro.edificio_nombre} · {registro.ascensor_identificador}
      </h1>
      <p className="tenue">
        {registro.direccion}, {registro.comuna} · Visita programada para el {diaLargo(registro.fecha_programada)}
      </p>
      <DetalleRegistro registro={desdeServidor(registro)} />
      <p>
        <Link to={`/cartera/${registro.edificio_id}`}>Ver la ficha del edificio</Link>
      </p>
    </section>
  )
}
