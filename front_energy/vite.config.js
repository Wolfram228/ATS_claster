import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  base: '/energy-service-prod/', // <- обязательно для GitHub Pages при не- корневом пути
  plugins: [vue()],
})
