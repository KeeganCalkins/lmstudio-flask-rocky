import { createRouter, createWebHistory } from 'vue-router'
import Main from './components/Main.vue'
import LandingPage from './views/LandingPage.vue'
import FocusUser from './components/FocusUser.vue'
import FocusAdmin from './components/FocusAdmin.vue'

import { useUserStore } from '@/stores/userStores'
import { pinia } from '@/pinia'

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
        meta: { requiresAuth: true, requiresAdmin: true },
        children: [{ path: '', component: FocusAdmin }]
    }
]

export const router = createRouter({
    history: createWebHistory(),
    routes,
})

router.beforeEach(async (to, from, next) => {
    const store = useUserStore(pinia)
    if (!store.loaded) {
        await store.init()
    }

    const needsAuth  = to.matched.some(r => r.meta.requiresAuth)
    const needsAdmin = to.matched.some(r => r.meta.requiresAdmin)

    if (needsAuth && !store.isAuthed) {
        return next('/')
    }

    if (needsAdmin) {
        await store.refreshMe()
        if (!store.isAdmin) {
            return next('/user')
        }
    }

    next();
})