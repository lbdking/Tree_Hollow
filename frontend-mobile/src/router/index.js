import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/home' },
  { path: '/login', component: () => import('../views/Login.vue'), meta: { public: true } },
  {
    path: '/',
    component: () => import('../layouts/MainLayout.vue'),
    children: [
      { path: 'home', component: () => import('../views/Home.vue') },
      { path: 'hollow', component: () => import('../views/Hollow.vue') },
      { path: 'group', component: () => import('../views/Group.vue') },
      { path: 'me', component: () => import('../views/Me.vue') }
    ]
  },
  { path: '/hollow/post', component: () => import('../views/HollowCreate.vue') },
  { path: '/hollow/:id', component: () => import('../views/HollowDetail.vue') },
  { path: '/content', component: () => import('../views/Content.vue') },
  { path: '/content/:id', component: () => import('../views/ArticleDetail.vue') },
  { path: '/breathing', component: () => import('../views/Breathing.vue') },
  { path: '/mood', component: () => import('../views/Mood.vue') },
  { path: '/group/:id', component: () => import('../views/GroupDetail.vue') },
  { path: '/activities', component: () => import('../views/Activities.vue') },
  { path: '/counselors', component: () => import('../views/Counselors.vue') },
  { path: '/counselors/:id', component: () => import('../views/CounselorDetail.vue') },
  { path: '/appointments', component: () => import('../views/Appointments.vue') },
  { path: '/notifications', component: () => import('../views/Notifications.vue') },
  { path: '/ai', component: () => import('../views/Ai.vue') }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('th_token')
  if (!token && !to.meta.public) return next('/login')
  if (token && to.path === '/login') return next('/home')
  next()
})

export default router
