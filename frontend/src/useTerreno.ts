import { useEffect, useState } from 'react'
import { alCambiar, limpiarEnviadas, mantencionesLocales, sincronizar, type MantencionLocal } from './terreno'
import { useEnLinea } from './useEnLinea'

/** Lo que el técnico tiene guardado en el celular; se actualiza solo cuando cambia (o cuando entra otro usuario). */
export function useMantencionesLocales(usuario = ''): MantencionLocal[] {
  const [lista, setLista] = useState<MantencionLocal[]>([])
  useEffect(() => {
    let vigente = true
    const leer = () => {
      mantencionesLocales()
        .then((l) => vigente && setLista(l))
        .catch(() => {})
    }
    leer()
    const dejar = alCambiar(leer)
    return () => {
      vigente = false
      dejar()
    }
  }, [usuario])
  return lista
}

/**
 * Envía lo pendiente sin que el técnico haga nada (RNF-01): al abrir la
 * aplicación, apenas vuelve la señal y, mientras quede algo, cada 20 segundos.
 * El aviso de "volvió la señal" del navegador no es confiable (se vio en S01),
 * por eso además se reintenta por tiempo.
 */
export function useEnvioAutomatico(activo: boolean) {
  const enLinea = useEnLinea()
  useEffect(() => {
    if (!activo) return
    limpiarEnviadas().catch(() => {})
  }, [activo])
  useEffect(() => {
    if (!activo || !enLinea) return
    const enviar = () => {
      sincronizar().catch(() => {})
    }
    enviar()
    const t = setInterval(enviar, 20000)
    return () => clearInterval(t)
  }, [activo, enLinea])
}
