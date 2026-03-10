<template>
  <div class="default-layout">
    <header class="layout-header">
      <div class="header-content">
        <div class="logo" @click="$router.push('/')">
          <span class="logo-text">八股文刷题</span>
        </div>
        <nav class="nav-menu">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="nav-item"
            :class="{ active: isActive(item.path) }"
          >
            {{ item.label }}
          </router-link>
        </nav>
        <div class="header-right">
          <template v-if="userStore.isLoggedIn">
            <el-dropdown trigger="click" :teleported="true">
              <div class="user-info">
                <el-avatar :size="32" :src="userStore.avatar" />
                <span class="username">{{ userStore.username }}</span>
                <el-icon :size="12"><ArrowDown /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="$router.push('/profile')">个人中心</el-dropdown-item>
                  <el-dropdown-item @click="$router.push('/mistakes')">错题本</el-dropdown-item>
                  <el-dropdown-item @click="$router.push('/profile/collections')">我的收藏</el-dropdown-item>
                  <el-dropdown-item @click="$router.push('/profile/settings')">个人设置</el-dropdown-item>
                  <el-dropdown-item v-if="userStore.isAdmin" divided @click="$router.push('/admin')">管理后台</el-dropdown-item>
                  <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
          <template v-else>
            <button class="btn-secondary btn-sm" @click="$router.push('/login')">登录</button>
            <button class="btn-primary btn-sm" @click="$router.push('/register')">注册</button>
          </template>
        </div>
      </div>
    </header>
    <main class="layout-main">
      <router-view />
    </main>
    <footer class="layout-footer">
      <p>八股文刷题系统 · 本科毕业设计</p>
    </footer>
  </div>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const navItems = [
  { path: '/', label: '首页' },
  { path: '/questions', label: '题库' },
  { path: '/practice', label: '专题练习' },
  { path: '/daily', label: '每日推荐' },
  { path: '/ranking', label: '排行榜' },
]

function isActive(path) {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

function handleLogout() {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.default-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.layout-header {
  height: var(--nav-height);
  background: var(--bg-nav);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-light);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: var(--max-width);
  margin: 0 auto;
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0 var(--spacing-lg);
}

.logo {
  cursor: pointer;
  margin-right: var(--spacing-xxl);
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.nav-menu {
  flex: 1;
  display: flex;
  align-items: center;
  gap: var(--spacing-xl);
}

.nav-item {
  font-size: 14px;
  color: var(--text-secondary);
  padding: 6px 0;
  border-bottom: 2px solid transparent;
  transition: all var(--transition-fast);
}

.nav-item:hover {
  color: var(--text-primary);
}

.nav-item.active {
  color: var(--text-primary);
  font-weight: 500;
  border-bottom-color: var(--text-primary);
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.user-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  cursor: pointer;
  padding: 4px 8px;
  border-radius: var(--radius-md);
  transition: background var(--transition-fast);
}

.user-info:hover {
  background: var(--bg-hover);
}

.username {
  font-size: 14px;
  color: var(--text-primary);
}

.btn-primary {
  background: var(--btn-primary-bg);
  color: var(--btn-primary-text);
  border: none;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 500;
  transition: background var(--transition-fast);
}

.btn-primary:hover {
  background: var(--btn-primary-hover);
}

.btn-secondary {
  background: #FFFFFF;
  color: var(--text-primary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 500;
  transition: all var(--transition-fast);
}

.btn-secondary:hover {
  background: var(--bg-hover);
}

.btn-sm {
  height: 36px;
  padding: 0 16px;
}

.layout-main {
  flex: 1;
  max-width: var(--max-width);
  width: 100%;
  margin: 0 auto;
  padding: var(--spacing-xl) var(--spacing-lg);
}

.layout-footer {
  text-align: center;
  padding: var(--spacing-lg);
  color: var(--text-tertiary);
  font-size: 13px;
  border-top: 1px solid var(--border-light);
}
</style>