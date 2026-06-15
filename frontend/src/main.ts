import { createApp } from 'vue'
import { createPinia } from 'pinia'
import antd from 'antdv-next'

import App from './App.vue'
import router from './router'
import 'antdv-next/dist/reset.css'
import 'uno.css'
import './style.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(antd)
app.mount('#app')
