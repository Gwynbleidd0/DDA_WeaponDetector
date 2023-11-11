// Composables
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    component: () => import('@/layouts/default/Default.vue'),
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import(/* webpackChunkName: "home" */ '@/views/Reports.vue'),
      },
      {
        path: 'incidents',
        name: 'Incidents',
        component: () => import(/* webpackChunkName: "home" */ '@/views/Incidents.vue'),
      },
      {
        path: 'reports',
        name: 'Reports',
        component: () => import(/* webpackChunkName: "home" */ '@/views/Reports.vue'),
      },
      {
        path: 'results/:id',
        name: 'Results',
        component: () => import(/* webpackChunkName: "home" */ '@/views/Result.vue'),
        props: true
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
})

export default router
