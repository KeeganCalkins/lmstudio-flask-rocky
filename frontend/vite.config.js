import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import fs from 'fs'

// https://vite.dev/config/
export default defineConfig({
    plugins: [
        vue(),
        vueDevTools(),
    ],
    resolve: {
        alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
        'vue': 'vue/dist/vue.esm-bundler.js'
        },
    },
    server: {
        proxy: {
            '/api': { // flask app
                target:         'http://localhost:8055',
                changeOrigin:   true,
                secure:         false,
            }
        },
        host: true, 
        https: true
    },
    preview: {
        host: '0.0.0.0',
        port: 8056,
        https: {
            key: fs.readFileSync('./certs/key.pem'),
            cert: fs.readFileSync('./certs/cert.pem'),
        },
        allowedHosts: ['rocky.cs.kent.edu']
    }
})