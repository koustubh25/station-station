import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/station-station/', // Important for existing repo deployment
  build: {
    outDir: 'dist',
  },
})
