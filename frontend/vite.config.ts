/// <reference types="vitest/config" />
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import { VitePWA } from 'vite-plugin-pwa'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'AapniSociety',
        short_name: 'AapniSociety',
        description: 'Worker-led cooperative infrastructure',
        theme_color: '#1f2937',
        background_color: '#ffffff',
        display: 'standalone',
        start_url: '/',
        icons: [
          { src: 'icon.svg', sizes: 'any', type: 'image/svg+xml', purpose: 'any' },
        ],
      },
    }),
  ],
  server: {
    port: 5173,
    // Dev proxy so the SPA can call the backend without CORS friction.
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
  test: {
    environment: 'jsdom',
    // jsdom only exposes localStorage when the document has an origin.
    environmentOptions: { jsdom: { url: 'http://localhost' } },
    globals: true,
    setupFiles: './src/test/setup.ts',
  },
})
