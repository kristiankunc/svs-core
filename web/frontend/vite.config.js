import { defineConfig } from 'vite'

export default defineConfig({
  server: {
    host: '127.0.0.1',
    port: 5173,
    strictPort: true,
    cors: true,
    hmr: {
      host: '127.0.0.1',
      protocol: 'ws',
    },
    watch: {
      usePolling: false,
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
    // Optimize build performance
    minify: 'esbuild',
    sourcemap: false,
  },
  // Optimize dependencies
  optimizeDeps: {
    include: ['alpinejs', 'bootstrap', 'highlight.js'],
  },
})
