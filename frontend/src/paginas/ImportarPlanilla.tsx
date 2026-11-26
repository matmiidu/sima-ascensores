import { useMemo, useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { enviarArchivo } from '../api'
import { TIPOS_USO, type TipoUso } from '../tipos'

type Estado = 'nuevo' | 'actualiza' | 'igual' | 'rechazada'

interface FilaRevisada {
  fila: number
  edificio: string
  direccion: string
  comuna: string
  equipo: string
  estado: Estado
  motivos: string[]
  avisos: string[]
  cambios: string[]
}

interface Revision {
  resumen: { filas: number; nuevo: number; actualiza: number; igual: number; rechazada: number; con_avisos: number; edificios_nuevos: number }
  filas: FilaRevisada[]
  importado?: { equipos_nuevos: number; equipos_actualizados: number; edificios_nuevos: number; sin_cambios: number; rechazadas: number }
}

const ETIQUETA: Record<Estado, [string, string]> = {
  nuevo: ['Nuevo', 'ok'],
  actualiza: ['Se actualiza', 'alerta'],
  igual: ['Sin cambios', ''],
  rechazada: ['No se importa', 'peligro'],
}

const plural = (n: number, uno: string, varios: string) => `${n} ${n === 1 ? uno : varios}`

/** Importar la cartera desde la planilla actual (H02): primero se revisa, después se confirma. */
export default function ImportarPlanilla() {
  const [archivo, setArchivo] = useState<File | null>(null)
  const [tipoUso, setTipoUso] = useState<TipoUso>('residencial')
  const [revision, setRevision] = useState<Revision | null>(null)
  const [filtro, setFiltro] = useState('revisar')
  const [ocupado, setOcupado] = useState(false)
  const [error, setError] = useState('')

  async function enviarPlanilla(confirmar: boolean) {
    if (!archivo) return
    setOcupado(true)
    setError('')
    const datos = new FormData()
    datos.append('archivo', archivo)
    datos.append('tipo_uso', tipoUso)
    if (confirmar) datos.append('confirmar', '1')
    try {
      setRevision(await enviarArchivo<Revision>('cartera/importar/', datos))
    } catch (e) {
      setError((e as Error).message)
      if (!confirmar) setRevision(null)
    } finally {
      setOcupado(false)
    }
  }

  function revisar(e: FormEvent) {
    e.preventDefault()
    enviarPlanilla(false)
  }

  const filas = useMemo(
    () =>
      (revision?.filas ?? []).filter((f) =>
        filtro === 'todas'
          ? true
          : filtro === 'revisar'
            ? f.estado === 'rechazada' || f.estado === 'actualiza' || f.avisos.length > 0
            : f.estado === filtro,
      ),
    [revision, filtro],
  )

  const r = revision?.resumen
  const aImportar = r ? r.nuevo + r.actualiza : 0

  return (
    <section>
      <Link to="/cartera" className="volver">← Cartera</Link>
      <h1>Importar planilla</h1>
      <p className="tenue">
        Sube la planilla de equipos (.csv o .xlsx) con las columnas Edificio, Dirección, Comuna y Equipo; Marca, Tipo,
        Paradas, Vence certificación, Técnico y Observación son opcionales. Primero verás qué pasará con cada fila:
        nada se guarda hasta que confirmes.
      </p>

      {!revision?.importado && (
        <form className="tarjeta" onSubmit={revisar}>
          <label>
            Planilla
            <input
              type="file"
              accept=".csv,.xlsx"
              onChange={(e) => {
                setArchivo(e.target.files?.[0] ?? null)
                setRevision(null)
              }}
            />
          </label>
          <label>
            Tipo de uso de los edificios nuevos
            <select value={tipoUso} onChange={(e) => setTipoUso(e.target.value as TipoUso)}>
              {Object.entries(TIPOS_USO).map(([v, t]) => <option key={v} value={v}>{t}</option>)}
            </select>
          </label>
          <p className="tenue">La planilla no trae el tipo de uso; después se puede corregir en la ficha de cada edificio.</p>
          <button className="grande" disabled={!archivo || ocupado}>
            {ocupado && !revision ? 'Revisando…' : 'Revisar planilla'}
          </button>
        </form>
      )}
      {error && <p className="error" role="alert">{error}</p>}

      {revision?.importado && (
        <div className="tarjeta ok">
          <strong>Planilla importada</strong>
          <p>
            {plural(revision.importado.equipos_nuevos, 'equipo nuevo', 'equipos nuevos')} en{' '}
            {plural(revision.importado.edificios_nuevos, 'edificio nuevo', 'edificios nuevos')},{' '}
            {plural(revision.importado.equipos_actualizados, 'equipo actualizado', 'equipos actualizados')},{' '}
            {revision.importado.sin_cambios} sin cambios y {plural(revision.importado.rechazadas, 'fila no importada', 'filas no importadas')}.
          </p>
          <Link className="boton primario" to="/cartera">Ver la cartera</Link>
        </div>
      )}

      {r && !revision?.importado && (
        <div className={`tarjeta ${r.rechazada ? 'alerta' : 'ok'}`}>
          <strong>{plural(r.filas, 'fila revisada', 'filas revisadas')}</strong>
          <p>
            {plural(r.nuevo, 'equipo nuevo', 'equipos nuevos')} ({plural(r.edificios_nuevos, 'edificio nuevo', 'edificios nuevos')}) ·{' '}
            {r.actualiza} se actualiza{r.actualiza === 1 ? '' : 'n'} · {r.igual} sin cambios ·{' '}
            {plural(r.rechazada, 'fila no se importa', 'filas no se importan')} · {r.con_avisos} con avisos
          </p>
          <button className="primario grande" disabled={!aImportar || ocupado} onClick={() => enviarPlanilla(true)}>
            {ocupado ? 'Importando…' : aImportar ? `Importar ${plural(aImportar, 'equipo', 'equipos')}` : 'No hay nada que importar'}
          </button>
        </div>
      )}

      {revision && (
        <>
          <div className="filtros">
            <select value={filtro} onChange={(e) => setFiltro(e.target.value)} aria-label="Qué filas mostrar">
              <option value="revisar">Para revisar (no se importan, cambios y avisos)</option>
              <option value="rechazada">No se importan</option>
              <option value="nuevo">Nuevos</option>
              <option value="actualiza">Se actualizan</option>
              <option value="igual">Sin cambios</option>
              <option value="todas">Todas</option>
            </select>
          </div>
          {filas.length === 0 && <p className="tenue">Ninguna fila en este grupo.</p>}
          <ul className="lista">
            {filas.map((f) => (
              <li key={f.fila} className="fila">
                <div>
                  <strong>
                    Fila {f.fila}: {f.edificio} · {f.equipo}
                  </strong>
                  <span className="tenue">{f.direccion}, {f.comuna}</span>
                  {[...f.motivos, ...f.cambios, ...f.avisos].map((t) => <span key={t}>{t}</span>)}
                </div>
                <span className="derecha">
                  <span className={`etiqueta ${ETIQUETA[f.estado][1]}`}>{ETIQUETA[f.estado][0]}</span>
                </span>
              </li>
            ))}
          </ul>
        </>
      )}
    </section>
  )
}
