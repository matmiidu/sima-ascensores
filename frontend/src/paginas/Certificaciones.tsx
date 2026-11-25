import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import { fechaCorta } from '../fechas'
import type { AlertaCertificacion, Certificaciones as Datos } from '../tipos'

const dias = (n: number) => (n === 1 ? '1 día' : `${n} días`)

function plazo(a: AlertaCertificacion) {
  if (a.vencimiento === null || a.dias_restantes === null) return null
  if (a.dias_restantes < 0) return `Venció el ${fechaCorta(a.vencimiento)} (hace ${dias(-a.dias_restantes)})`
  if (a.dias_restantes === 0) return `Vence hoy, ${fechaCorta(a.vencimiento)}`
  return `Vence el ${fechaCorta(a.vencimiento)} (en ${dias(a.dias_restantes)})`
}

/** Correo ya escrito para el administrador; se abre en la aplicación de correo del jefe técnico. */
function correo(a: AlertaCertificacion) {
  const asunto = `Certificación del ascensor ${a.identificador} · ${a.edificio}`
  const vencio = a.dias_restantes !== null && a.dias_restantes < 0
  const cuerpo =
    `Estimado(a) ${a.administrador.nombre || 'administrador(a)'}:\n\n` +
    `Le informamos que la certificación del ascensor ${a.identificador} de ${a.edificio} (${a.direccion}, ${a.comuna}) ` +
    `${vencio ? 'venció' : 'vence'} el ${fechaCorta(a.vencimiento ?? '')}. ` +
    'Según la Ley 20.296, el edificio debe renovarla con una entidad certificadora inscrita. ' +
    'Quedamos atentos para coordinar la visita del certificador.\n\nSaludos,\nAscensores Altavía'
  return `mailto:${a.administrador.correo}?subject=${encodeURIComponent(asunto)}&body=${encodeURIComponent(cuerpo)}`
}

function Alerta({ a, tipo }: { a: AlertaCertificacion; tipo: 'vencida' | 'por-vencer' | 'sin-fecha' }) {
  const adm = a.administrador
  return (
    <div className={`tarjeta ${tipo === 'vencida' ? 'detenido' : tipo === 'por-vencer' ? 'alerta' : ''}`}>
      <strong>
        <Link to={`/cartera/${a.edificio_id}`}>{a.edificio}</Link> · {a.identificador}
      </strong>
      <p className="tenue">{a.direccion}, {a.comuna}</p>
      {tipo === 'sin-fecha' ? (
        <p className="tenue">Falta registrar el vencimiento en la ficha del edificio.</p>
      ) : (
        <>
          <p><span className={`etiqueta ${tipo === 'vencida' ? 'peligro' : 'alerta'}`}>{plazo(a)}</span></p>
          <p className="tenue">
            Administrador: {adm.nombre || 'sin registrar'}
            {adm.telefono && <> · <a href={`tel:${adm.telefono}`}>{adm.telefono}</a></>}
          </p>
          {adm.correo ? (
            <a className="boton primario" href={correo(a)}>Avisar al administrador</a>
          ) : (
            <p className="advertencia">El edificio no tiene correo del administrador registrado.</p>
          )}
        </>
      )}
    </div>
  )
}

/** Certificaciones vencidas y por vencer, para avisar al administrador con anticipación (H10). */
export default function Certificaciones() {
  const [datos, setDatos] = useState<Datos | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api<Datos>('certificaciones/')
      .then(setDatos)
      .catch((e) => setError((e as Error).message))
  }, [])

  if (error) return <p className="error">{error}</p>
  if (!datos) return <p className="tenue">Cargando…</p>

  const total = datos.vencidas.length + datos.por_vencer.length + datos.sin_fecha.length
  return (
    <section>
      <h1>Certificaciones</h1>
      <div className={`tarjeta ${total ? 'alerta' : 'ok'}`}>
        <strong>
          {total === 0 ? 'Ninguna certificación necesita aviso' : total === 1 ? '1 ascensor necesita aviso' : `${total} ascensores necesitan aviso`}
        </strong>
        <p className="tenue">
          {datos.vencidas.length} vencida{datos.vencidas.length === 1 ? '' : 's'} · {datos.por_vencer.length} vence
          {datos.por_vencer.length === 1 ? '' : 'n'} en los próximos {datos.dias} días · {datos.sin_fecha.length} sin fecha registrada
        </p>
      </div>
      {datos.vencidas.length > 0 && <h3>Vencidas</h3>}
      {datos.vencidas.map((a) => <Alerta key={a.ascensor_id} a={a} tipo="vencida" />)}
      {datos.por_vencer.length > 0 && <h3>Vencen en los próximos {datos.dias} días</h3>}
      {datos.por_vencer.map((a) => <Alerta key={a.ascensor_id} a={a} tipo="por-vencer" />)}
      {datos.sin_fecha.length > 0 && <h3>Sin fecha registrada</h3>}
      {datos.sin_fecha.map((a) => <Alerta key={a.ascensor_id} a={a} tipo="sin-fecha" />)}
    </section>
  )
}
