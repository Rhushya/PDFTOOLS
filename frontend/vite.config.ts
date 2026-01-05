import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: './', // Required for Electron to load assets correctly
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/download': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    // Target modern browsers for smaller bundles
    target: 'es2020',
    // Enable CSS code splitting
    cssCodeSplit: true,
    // Disable source maps for smaller production build
    sourcemap: false,
    // Increase chunk warning limit for framer-motion
    chunkSizeWarningLimit: 600,
  },
  // Pre-bundle dependencies for faster dev startup
  optimizeDeps: {
    include: ['react', 'react-dom', 'framer-motion', 'axios', 'react-dropzone', 'react-hot-toast'],
  },
})
