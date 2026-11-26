import { useCallback, useEffect, useState } from 'react'
import { NavLink, Navigate, Route, Routes } from 'react-router-dom'
import { SIN_SESION, api, guardarSesion, guardarToken, sesionGuardada, token } from './api'
import type { Sesion } from './tipos'
import { useEnLinea } from './useEnLinea'
import { useEnvioAutomatico, useMantencionesLocales } from './useTerreno'
import Calendario from './paginas/Calendario'
import Cartera from './paginas/Cartera'
import Certificaciones from './paginas/Certificaciones'
import Checklist from './paginas/Checklist'
import EdificioDetalle from './paginas/EdificioDetalle'
import Informes from './paginas/Informes'
import Ingreso from './paginas/Ingreso'
import Mantencion from './paginas/Mantencion'
import MisVisitas from './paginas/MisVisitas'
import Registros from './paginas/Registros'

export default function App() {
  const [conToken, setConToken] = useState(() => token() !== null)
  const [sesion, setSesion] = useState<Sesion | null>(sesionGuardada)
  const enLinea = useEnLinea()
  const sinEnviar = useMantencionesLocales(sesion?.usuario).filter((m) => m.estado === 'pendiente').length

  // Las mantenciones guardadas sin señal se envían solas mientras el técnico tenga la sesión abierta.
  useEnvioAutomatico(conToken && !!sesion?.tecnico)

  const cerrar = useCallback(() => {
    guardarToken(null)
    guardarSesion(null)
    setSesion(null)
    setConToken(false)
  }, [])

  function salir() {
    if (
      sinEnviar > 0 &&
      !confirm(
        `Tienes ${sinEnviar === 1 ? '1 mantención guardada' : `${sinEnviar} mantenciones guardadas`} en el celular sin enviar. ` +
          'No se pierden: se enviarán cuando vuelvas a entrar con tu usuario en este celular. ¿Salir de todos modos?',
      )
    ) {
      return
    }
    cerrar()
  }

  // Si el servidor avisa que la sesión ya no vale, se pide ingresar de nuevo.
  useEffect(() => {
    window.addEventListener(SIN_SESION, cerrar)
    return () => window.removeEventListener(SIN_SESION, cerrar)
  }, [cerrar])

  // Al entrar se pregunta al servidor quién es el usuario: de eso depende si
  // ve la cartera y el calendario (jefe técnico) o sus visitas (técnico).
  useEffect(() => {
    if (!conToken) return
    api<Sesion>('yo/')
      .then((s) => {
        guardarSesion(s)
        setSesion(s)
      })
      .catch(() => {
        /* sin señal se sigue con la copia guardada; si la sesión no vale, llega el aviso SIN_SESION */
      })
  }, [conToken])

  if (!conToken) return <Ingreso alIngresar={() => setConToken(true)} />
  if (!sesion) {
    return (
      <main className="ingreso">
        <p className="tenue">{enLinea ? 'Cargando…' : 'Para ingresar la primera vez se necesita señal.'}</p>
      </main>
    )
  }

  const inicio = sesion.tecnico ? '/mis-visitas' : '/cartera'

  return (
    <>
      <header className="barra">
        <span className="marca">SIMA</span>
        <nav>
          {sesion.tecnico && <NavLink to="/mis-visitas">Mis visitas</NavLink>}
          {sesion.es_jefe && (
            <>
              <NavLink to="/cartera">Cartera</NavLink>
              <NavLink to="/calendario">Calendario</NavLink>
              <NavLink to="/checklists">Checklists</NavLink>
              <NavLink to="/certificaciones">Certificaciones</NavLink>
              <NavLink to="/informes">Informes</NavLink>
              {/* Panel de administración de Django: página aparte, con su propio ingreso. */}
              <a href="/admin/" target="_blank" rel="noopener" title="Panel de administración (se abre en otra pestaña)">
                Panel
              </a>
            </>
          )}
        </nav>
        <button className="salir" onClick={salir} title={`Salir (${sesion.nombre})`}>
          Salir
        </button>
      </header>
      {!enLinea && <div className="aviso-sin-senal">Sin señal: lo que guardes queda en el celular.</div>}
      <main>
        {!sesion.tecnico && !sesion.es_jefe ? (
          <p className="error">
            Tu usuario no está asociado a un técnico. Pide al jefe técnico que lo asocie.
          </p>
        ) : (
          <Routes>
            {sesion.tecnico && (
              <>
                <Route path="/mis-visitas" element={<MisVisitas sesion={sesion} />} />
                <Route path="/mis-visitas/:id" element={<Checklist sesion={sesion} />} />
              </>
            )}
            {sesion.es_jefe && (
              <>
                <Route path="/cartera" element={<Cartera />} />
                <Route path="/cartera/:id" element={<EdificioDetalle />} />
                <Route path="/calendario" element={<Calendario />} />
                <Route path="/checklists" element={<Registros />} />
                <Route path="/certificaciones" element={<Certificaciones />} />
                <Route path="/informes" element={<Informes />} />
                <Route path="/mantenciones/:id" element={<Mantencion />} />
              </>
            )}
            <Route path="*" element={<Navigate to={inicio} replace />} />
          </Routes>
        )}
      </main>
    </>
  )
}
