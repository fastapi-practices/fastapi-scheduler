import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import unocss from 'unocss/vite'
import dayjs from 'vite-plugin-dayjs'

// https://vite.dev/config/
export default defineConfig({
  plugins: [dayjs(), vue(), unocss()],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
