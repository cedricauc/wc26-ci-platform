import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/match/:id',
      name: 'match',
      component: () => import('../views/MatchView.vue'),
    },
    {
      path: '/stadium-map/:matchId',
      name: 'stadium-map',
      component: () => import('../views/StadiumMapView.vue'),
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
    },
    {
      path: '/upload',
      name: 'upload',
      component: () => import('../views/DocumentUploadView.vue'),
    },
  ],
})

export default router
