import { useEffect, useState } from 'react'
import { NavLink, Navigate, Route, Routes } from 'react-router-dom'
import { api, guardarSesion, guardarToken, sesionGuardada, token } from './api'
import type { Sesion } from './tipos'
import { useEnLinea } from './useEnLinea'
import Calendario from './paginas/Calendario'
import Cartera from './paginas/Cartera'
import EdificioDetalle from './paginas/EdificioDetalle'
import Ingreso from './paginas/Ingreso'
import MisVisitas from './paginas/MisVisitas'
import PruebaSinConexion from './paginas/PruebaSinConexion'

export default function App() {
  const [conToken, setConToken] = useState(() => token() !== null)
  const [sesion, setSesion] = useState<Sesion | null>(sesionGuardada)
  const enLinea = useEnLinea()

  function salir() {
    guardarToken(null)
    guardarSesion(null)
    setSesion(null)
    setConToken(false)
  }

  // Al entrar se pregunta al servidor quién es el usuario: de eso depende si
  // ve la cartera y el calendario (jefe técnico) o sus visitas (técnico).
  useEffect(() => {
    if (!conToken) return
    api<Sesion>('yo/')
      .then((s) => {
        guardarSesion(s)
        setSesion(s)
      })
      .catch((e) => {
        if (e.estado === 401) salir()
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
              <NavLink to="/sin-conexion">Terreno</NavLink>
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
            {sesion.tecnico && <Route path="/mis-visitas" element={<MisVisitas sesion={sesion} />} />}
            {sesion.es_jefe && (
              <>
                <Route path="/cartera" element={<Cartera />} />
                <Route path="/cartera/:id" element={<EdificioDetalle />} />
                <Route path="/calendario" element={<Calendario />} />
                <Route path="/sin-conexion" element={<PruebaSinConexion />} />
              </>
            )}
            <Route path="*" element={<Navigate to={inicio} replace />} />
          </Routes>
        )}
      </main>
    </>
  )
}
