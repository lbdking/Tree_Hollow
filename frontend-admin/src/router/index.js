import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/login', component: () => import('../views/Login.vue'), meta: { public: true } },
  {
    path: '/',
    component: () => import('../layouts/AdminLayout.vue'),
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', component: () => import('../views/Dashboard.vue') },
      { path: 'users', component: () => import('../views/Users.vue') },
      { path: 'posts', component: () => import('../views/Posts.vue') },
      { path: 'reports', component: () => import('../views/Reports.vue') },
      { path: 'articles', component: () => import('../views/Articles.vue') },
      { path: 'counselors', component: () => import('../views/Counselors.vue') }
    ]
  }
]

const router = createRouter({ history: createWebHistory(), routes })
router.beforeEach((to, from, next) => {
  const t = localStorage.getItem('th_admin_token')
  if (!t && !to.meta.public) return next('/login')
  if (t && to.path === '/login') return next('/')
  next()
})

export default router
