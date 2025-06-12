import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import path from 'node:path'
import fs from 'node:fs'

// https://vite.dev/config/
export default defineConfig({
  // server: {
  //   host: '0.0.0.0',
  //   port: 3000,
  //   https: {
  //     key: fs.readFileSync('../nginx/certs/key.pem'),
  //     cert: fs.readFileSync('../nginx/certs/cert.pem'),
  //   },
  //   proxy: {
  //     '/api': {
  //       target: 'http://localhost:8000',
  //       changeOrigin: true,
  //     },
  //   },
  // },
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
})
