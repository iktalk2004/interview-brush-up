// 路由守卫, 用于处理路由跳转前的逻辑
import { useUserStore } from '@/stores/user'

export function setupGuards(router) {
    router.beforeEach((to, from, next) => {
        const userStore = useUserStore()
        
        // 设置页面标题
        document.title = to.meta.title
        ? `${to.meta.title} - 八股文刷题系统`
        : '八股文刷题系统'

        // 不需要认证的页面
        if (to.meta.requiresAuth === false) {
            if(userStore.isLoggedIn && ['/login', '/register'].includes(to.name)){
                next({ name: 'Home' })
                return
            }
            next()
            return
        }
        // 需要认证的页面
        if (to.matched.some(record => record.meta.requiresAuth !== false)) {
            if (!userStore.isLoggedIn) {
                next({ name: 'Login', query: { redirect: to.fullPath } })
                return
            }
        if (to.matched.some(record => record.meta.requiresAdmin)) {
            if (!userStore.isAdmin) {
                next({ name: 'Home' })
                return
            }
        }
    }

    next()
    })
}
























