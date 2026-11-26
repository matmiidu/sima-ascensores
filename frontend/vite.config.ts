import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import { VitePWA } from 'vite-plugin-pwa'

// Servidor de Django al que se reenvían /api, /admin y /static. SIMA_API permite apuntar a otro (por ejemplo,
// una base de pruebas en otro puerto) sin tocar este archivo.
const API = process.env.SIMA_API ?? 'http://127.0.0.1:8000'
const proxy = { '/api': API, '/admin': API, '/static': API }

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.svg'],
      manifest: {
        name: 'SIMA · Ascensores Altavía',
        short_name: 'SIMA',
        description: 'Gestión de mantenciones de ascensores',
        lang: 'es-CL',
        theme_color: '#1f3a5f',
        background_color: '#f4f6f9',
        display: 'standalone',
        start_url: '/',
        icons: [
          { src: 'icono-192.png', sizes: '192x192', type: 'image/png' },
          { src: 'icono-512.png', sizes: '512x512', type: 'image/png' },
          { src: 'icono.svg', sizes: 'any', type: 'image/svg+xml' },
        ],
      },
      workbox: {
        // La aplicación abre sin señal. El panel /admin y la API no pasan por ella.
        navigateFallback: '/index.html',
        navigateFallbackDenylist: [/^\/(api|admin|static)(\/|$)/],
        runtimeCaching: [
          {
            // Consultas del jefe técnico: si no hay señal se muestra la última copia.
            // Lo del técnico en terreno (visitas del día, checklist y mantenciones)
            // no pasa por aquí: su copia la maneja la aplicación en terreno.ts.
            urlPattern: ({ url }) => /^\/api\/(edificios|ascensores|tecnicos|visitas|feriados|calendario)\//.test(url.pathname),
            handler: 'NetworkFirst',
            method: 'GET',
            options: { cacheName: 'api-lectura', networkTimeoutSeconds: 4 },
          },
        ],
      },
      devOptions: { enabled: false },
    }),
  ],
  server: {
    host: true,
    proxy,
  },
  preview: {
    host: true,
    proxy,
  },
})
