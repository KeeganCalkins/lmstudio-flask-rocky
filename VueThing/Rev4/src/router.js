import { createRouter, createWebHistory } from 'vue-router'
import Main from './components/Main.vue'
import LandingPage from './views/LandingPage.vue'
import FocusUser from './components/FocusUser.vue'
import FocusAdmin from './components/FocusAdmin.vue'

import { msalInstance } from './msalInstance.js'
import { authFetch } from '@/authFetch.js'

const routes = [
    {
        path: '/', // login
        component: LandingPage
    },
    {
        path: '/user',
        component: Main,
        meta: { requiresAuth: true },
        children: [{ path: '', component: FocusUser }]
    },
    {
        path: '/admin',
        component: Main,
        meta: { requiresAuth: true, adminRequired: true },
        children: [{ path: '', component: FocusAdmin }]
    }
]

export const router = createRouter({
    history: createWebHistory(),
    routes,
})

router.beforeEach(async (to, from, next) => {
    if (to.meta.requiresAuth) {
        const accounts = msalInstance.getAllAccounts();
        if (!accounts.length) {
            return next({ path: '/' })
        }
    }

    if (to.meta.adminRequired) {
        try {
            const res = await authFetch('/api/me')
            const me  = await res.json()
            if (!me.isAdmin) {
                return next({ path: '/user' })
            }
        } catch (err) {
            return next({ path: '/' })
        }
    }
    next();
})