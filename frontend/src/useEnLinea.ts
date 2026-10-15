import { useEffect, useState } from 'react'

// Los eventos online/offline no siempre llegan (en salas de máquinas la señal
// va y viene), así que además se revisa cada pocos segundos.
export function useEnLinea(cadaMs = 5000) {
  const [enLinea, setEnLinea] = useState(navigator.onLine)
  useEffect(() => {
    const revisar = () => setEnLinea(navigator.onLine)
    window.addEventListener('online', revisar)
    window.addEventListener('offline', revisar)
    document.addEventListener('visibilitychange', revisar)
    const t = setInterval(revisar, cadaMs)
    return () => {
      window.removeEventListener('online', revisar)
      window.removeEventListener('offline', revisar)
      document.removeEventListener('visibilitychange', revisar)
      clearInterval(t)
    }
  }, [cadaMs])
  return enLinea
}
