import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import { VitePWA } from 'vite-plugin-pwa'

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
    proxy: {
      '/api': 'http://127.0.0.1:8000',
      '/admin': 'http://127.0.0.1:8000',
      '/static': 'http://127.0.0.1:8000',
    },
  },
  preview: {
    host: true,
    proxy: {
      '/api': 'http://127.0.0.1:8000',
      '/admin': 'http://127.0.0.1:8000',
      '/static': 'http://127.0.0.1:8000',
    },
  },
})
