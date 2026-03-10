import DefaultLayout from '@/layouts/DefaultLayout.vue'
import AuthLayout from '@/layouts/AuthLayout.vue'

// 公共路由, 不需要认证
export const publicRoutes = [
  {
    path: '/',
    component: DefaultLayout,
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('@/views/home/HomePage.vue'),
        meta: { title: '首页', requiresAuth: false },
      },
    ],
  },
  {
    path: '/',
    component: AuthLayout,
    children: [
      {
        path: 'login',
        name: 'Login',
        component: () => import('@/views/auth/LoginPage.vue'),
        meta: { title: '登录', requiresAuth: false },
      },
      {
        path: 'register',
        name: 'Register',
        component: () => import('@/views/auth/RegisterPage.vue'),
        meta: { title: '注册', requiresAuth: false },
      },
      {
        path: 'forgot-password',
        name: 'ForgotPassword',
        component: () => import('@/views/auth/ForgotPasswordPage.vue'),
        meta: { title: '找回密码', requiresAuth: false },
      },
    ],
  },
]