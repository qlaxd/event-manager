import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'
import SettingsView from '../views/SettingsView.vue'
import ForgotPasswordView from '../views/ForgotPasswordView.vue'
import ChatView from '../views/ChatView.vue'
import EventsView from '../views/EventsView.vue'
import EventCreateView from '../views/EventCreateView.vue'
import AnalyticsView from '../views/AnalyticsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      redirect: '/dashboard'
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { requiresGuest: true }
    },
    {
      path: '/forgot-password',
      name: 'forgot-password',
      component: ForgotPasswordView,
      meta: { requiresGuest: true }
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView,
      meta: { requiresAuth: true }
    },
    {
      path: '/settings',
      name: 'settings',
      component: SettingsView,
      meta: { requiresAuth: true }
    },
    {
      path: '/events',
      name: 'events',
      component: EventsView,
      meta: { requiresAuth: true }
    },
    {
      path: '/events/create',
      name: 'event-create',
      component: EventCreateView,
      meta: { requiresAuth: true }
    },
    {
      path: '/analytics',
      name: 'analytics',
      component: AnalyticsView,
      meta: { requiresAuth: true }
    }
  ]
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // Try to fetch user if accessToken exists but user object is null
  // This handles the case where the page is refreshed
  if (authStore.accessToken && !authStore.user) {
    try {
      await authStore.fetchUser()
    } catch {
      // Token might be invalid, let the guards handle it
    }
  }

  // If not authenticated, try silent refresh before redirecting to login
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    try {
      await authStore.trySilentRefresh()
    } catch {}
    // After silent refresh, check again
    if (!authStore.isAuthenticated) {
      authStore.setReturnUrl(to.fullPath)
      return next({ name: 'login' })
    }
  }

  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    return next({ name: 'dashboard' })
  }

  next()
})

export default router
