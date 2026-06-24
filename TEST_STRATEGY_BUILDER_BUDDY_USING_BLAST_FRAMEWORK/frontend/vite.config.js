import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    {
      name: 'remove-crossorigin',
      transformIndexHtml(html) {
        return html.replace(/\s+crossorigin\s*/gi, ' ')
      },
    },
  ],
  server: {
    proxy: {
      '/fetch-jira': { target: 'http://localhost:8000', changeOrigin: true, secure: false },
      '/generate-strategy': { target: 'http://localhost:8000', changeOrigin: true, secure: false },
      '/create-docx': { target: 'http://localhost:8000', changeOrigin: true, secure: false }
    }
  }
})
