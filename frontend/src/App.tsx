import { useEffect, useState } from 'react'
import { NavLink, Navigate, Route, Routes } from 'react-router-dom'
import { api, guardarToken, token } from './api'
import { useEnLinea } from './useEnLinea'
import Calendario from './paginas/Calendario'
import Cartera from './paginas/Cartera'
import EdificioDetalle from './paginas/EdificioDetalle'
import Ingreso from './paginas/Ingreso'
import PruebaSinConexion from './paginas/PruebaSinConexion'

export default function App() {
  const [sesion, setSesion] = useState<string | null>(token() ? '' : null)
  const enLinea = useEnLinea()

  useEffect(() => {
    if (sesion === '' && navigator.onLine) {
      api<{ nombre: string }>('yo/')
        .then((r) => setSesion(r.nombre))
        .catch((e) => {
          if (e.estado === 401) setSesion(null)
        })
    }
  }, [sesion])

  if (sesion === null) return <Ingreso alIngresar={() => setSesion('')} />

  return (
    <>
      <header className="barra">
        <span className="marca">SIMA</span>
        <nav>
          <NavLink to="/cartera">Cartera</NavLink>
          <NavLink to="/calendario">Calendario</NavLink>
          <NavLink to="/sin-conexion">Terreno</NavLink>
        </nav>
        <button
          className="salir"
          onClick={() => {
            guardarToken(null)
            setSesion(null)
          }}
          title={sesion ? `Salir (${sesion})` : 'Salir'}
        >
          Salir
        </button>
      </header>
      {!enLinea && <div className="aviso-sin-senal">Sin señal: lo que guardes queda en el celular.</div>}
      <main>
        <Routes>
          <Route path="/" element={<Navigate to="/cartera" replace />} />
          <Route path="/cartera" element={<Cartera />} />
          <Route path="/cartera/:id" element={<EdificioDetalle />} />
          <Route path="/calendario" element={<Calendario />} />
          <Route path="/sin-conexion" element={<PruebaSinConexion />} />
          <Route path="*" element={<Navigate to="/cartera" replace />} />
        </Routes>
      </main>
    </>
  )
}
