import { defineConfig } from 'vite'

export default defineConfig({
  server: {
    host: '127.0.0.1',
    port: 5173,
    strictPort: true,
    cors: true,
  },
  emptyOutDir: true,
  build: {
    outDir: "../static/vite",
    manifest: true,
    rollupOptions: {
      input: "src/main.js",
    },
  },

})
