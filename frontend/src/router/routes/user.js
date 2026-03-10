import DefaultLayout from '@/layouts/DefaultLayout.vue'

export const userRoutes = [
  {
    path: '/',
    component: DefaultLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: 'questions',
        name: 'QuestionList',
        component: () => import('@/views/questions/QuestionListPage.vue'),
        meta: { title: '题库' },
      },
      {
        path: 'question/text/:id',
        name: 'TextQuestion',
        component: () => import('@/views/questions/TextQuestionPage.vue'),
        meta: { title: '简答题' },
      },
      {
        path: 'question/code/:id',
        name: 'CodeQuestion',
        component: () => import('@/views/questions/CodeQuestionPage.vue'),
        meta: { title: '代码题' },
      },
      {
        path: 'practice',
        name: 'Practice',
        component: () => import('@/views/practice/PracticePage.vue'),
        meta: { title: '专题练习' },
      },
      {
        path: 'daily',
        name: 'Daily',
        component: () => import('@/views/practice/DailyPage.vue'),
        meta: { title: '每日推荐' },
      },
      {
        path: 'mistakes',
        name: 'Mistakes',
        component: () => import('@/views/practice/MistakesPage.vue'),
        meta: { title: '错题本' },
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/profile/ProfilePage.vue'),
        meta: { title: '个人中心' },
      },
      {
        path: 'profile/collections',
        name: 'Collections',
        component: () => import('@/views/profile/CollectionPage.vue'),
        meta: { title: '我的收藏' },
      },
      {
        path: 'profile/history',
        name: 'History',
        component: () => import('@/views/profile/HistoryPage.vue'),
        meta: { title: '刷题记录' },
      },
      {
        path: 'profile/settings',
        name: 'Settings',
        component: () => import('@/views/profile/SettingsPage.vue'),
        meta: { title: '个人设置' },
      },
      {
        path: 'ranking',
        name: 'Ranking',
        component: () => import('@/views/ranking/RankingPage.vue'),
        meta: { title: '排行榜' },
      },
      {
        path: '/practice/session',
        name: 'PracticeSession',
        component: () => import('@/views/practice/PracticeSessionPage.vue'),
        meta: { title: '专题练习', requiresAuth: true }
      },
    ],
  },
]