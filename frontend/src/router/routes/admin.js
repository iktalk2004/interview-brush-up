import AdminLayout from '@/layouts/AdminLayout.vue'

export const adminRoutes = [
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: '',
        redirect: '/admin/dashboard',
      },
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: () => import('@/views/admin/DashboardPage.vue'),
        meta: { title: '管理后台 - 数据看板' },
      },
      {
        path: 'questions',
        name: 'AdminQuestions',
        component: () => import('@/views/admin/QuestionManagePage.vue'),
        meta: { title: '管理后台 - 题目管理' },
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('@/views/admin/UserManagePage.vue'),
        meta: { title: '管理后台 - 用户管理' },
      },
      {
        path: 'categories',
        name: 'AdminCategories',
        component: () => import('@/views/admin/CategoryManagePage.vue'),
        meta: { title: '管理后台 - 分类管理' },
      },
      {
        path: 'announcements',
        name: 'AdminAnnouncements',
        component: () => import('@/views/admin/AnnouncementManagePage.vue'),
        meta: { title: '管理后台 - 公告管理' },
      },
      {
        path: 'recommend',
        name: 'AdminRecommend',
        component: () => import('@/views/admin/RecommendComparePage.vue'),
        meta: { title: '管理后台 - 推荐算法对比' },
      },
    ],
  },
]