import { defineConfig } from 'vite'

export default defineConfig({
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    cors: true,
    hmr: {
      host: 'localhost',
      port: 5173,
      protocol: 'ws',
    },
    watch: {
      usePolling: true,
      poll: 1000,
      ignored: ['**/node_modules/**', '**/dist/**', '**/.git/**'],
    },
  },
  emptyOutDir: true,
  build: {
    outDir: "../static/vite",
    manifest: true,
    rollupOptions: {
      input: "src/main.js",
    },
    minify: 'esbuild',
    sourcemap: false,
  },
  optimizeDeps: {
    include: ['alpinejs', 'bootstrap', 'highlight.js'],
  },
})
