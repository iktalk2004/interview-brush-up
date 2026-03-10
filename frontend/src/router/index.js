import { createRouter, createWebHistory } from 'vue-router'
import { publicRoutes } from './routes/public'
import { userRoutes } from './routes/user'
import { adminRoutes } from './routes/admin'
import { setupGuards } from './guards'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    ...publicRoutes,
    ...userRoutes,
    ...adminRoutes,
    { // 404 路由, 必须放在最后
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('@/views/home/HomePage.vue'),
      meta: { title: '页面未找到', requiresAuth: false },
    },
  ],
  scrollBehavior() {  // 滚动行为, 滚动到顶部
    return { top: 0 }
  },
})

setupGuards(router)  // 配置路由守卫

export default router