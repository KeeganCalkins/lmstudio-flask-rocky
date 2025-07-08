import { createRouter, createWebHistory } from 'vue-router'
import Main       from './components/Main.vue'
import LandingPage from './views/LandingPage.vue'
import FocusUser  from './components/FocusUser.vue'
import FocusAdmin from './components/FocusAdmin.vue'

const routes = [
    {
        path: '/', // login
        component: LandingPage
    },
    {
        path: '/user',
        component: Main,
        children: [{ path: '', component: FocusUser }]
    },
    {
        path: '/admin',
        component: Main,
        children: [{ path: '', component: FocusAdmin }]
    }
]

export const router = createRouter({
    history: createWebHistory(),
    routes,
})