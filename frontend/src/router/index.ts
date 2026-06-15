import { createRouter, createWebHistory } from 'vue-router'

import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
    },
    {
      path: '/',
      component: () => import('../layouts/DefaultLayout.vue'),
      children: [
        {
          path: '',
          redirect: { name: 'dashboard' },
        },
        {
          path: 'dashboard',
          name: 'dashboard',
          component: () => import('../views/DashboardView.vue'),
        },
        {
          path: 'analysis',
          name: 'analysis',
          component: () => import('../views/AnalysisView.vue'),
        },
        {
          path: 'scheduler',
          name: 'scheduler',
          component: () => import('../views/SchedulerView.vue'),
        },
        {
          path: 'scheduler/runs',
          name: 'schedulerRuns',
          component: () => import('../views/SchedulerRunsView.vue'),
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: { name: 'dashboard' },
    },
  ],
})

router.beforeEach((to) => {
  const authStore = useAuthStore()
  if (!authStore.isAuthenticated && to.name !== 'login') {
    return { name: 'login' }
  }
  if (authStore.isAuthenticated && to.name === 'login') {
    return { name: 'dashboard' }
  }
  return true
})

export default router
