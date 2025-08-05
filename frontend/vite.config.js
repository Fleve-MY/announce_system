// frontend/vite.config.js

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  // 2. 添加 resolve 配置来设置路径别名
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    }
  }
})