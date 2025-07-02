import { createRouter, createWebHistory } from 'vue-router'
import LandingPage from '../components/LandingPage.vue'
import LoginPage   from '../components/LoginPage.vue'

const routes = [
  { path: '/',      component: LandingPage },
  { path: '/login', component: LoginPage}
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
