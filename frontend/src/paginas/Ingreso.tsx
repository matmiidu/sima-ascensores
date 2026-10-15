import { useState, type FormEvent } from 'react'
import { iniciarSesion } from '../api'

export default function Ingreso({ alIngresar }: { alIngresar: () => void }) {
  const [usuario, setUsuario] = useState('')
  const [clave, setClave] = useState('')
  const [error, setError] = useState('')
  const [enviando, setEnviando] = useState(false)

  async function entrar(e: FormEvent) {
    e.preventDefault()
    setEnviando(true)
    setError('')
    try {
      await iniciarSesion(usuario, clave)
      alIngresar()
    } catch {
      setError(navigator.onLine ? 'Usuario o clave incorrectos.' : 'Para ingresar la primera vez se necesita señal.')
    } finally {
      setEnviando(false)
    }
  }

  return (
    <main className="ingreso">
      <h1>SIMA</h1>
      <p className="tenue">Ascensores Altavía · mantenciones</p>
      <form onSubmit={entrar} className="tarjeta">
        <label>
          Usuario
          <input value={usuario} onChange={(e) => setUsuario(e.target.value)} autoComplete="username" required />
        </label>
        <label>
          Clave
          <input type="password" value={clave} onChange={(e) => setClave(e.target.value)} autoComplete="current-password" required />
        </label>
        {error && <p className="error">{error}</p>}
        <button className="primario" disabled={enviando}>{enviando ? 'Ingresando…' : 'Ingresar'}</button>
      </form>
    </main>
  )
}
