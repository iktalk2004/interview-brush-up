<template>
  <div class="admin-layout">
    <aside class="admin-sidebar">
      <div class="sidebar-header">
        <span class="sidebar-title" @click="$router.push('/')">八股文刷题</span>
        <span class="sidebar-badge">管理后台</span>
      </div>
      <nav class="sidebar-menu">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="menu-item"
          :class="{ active: isActive(item.path) }"
        >
          <el-icon :size="18"><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
        </router-link>
      </nav>
      <div class="sidebar-footer">
        <router-link to="/" class="back-link">
          <el-icon :size="16"><Back /></el-icon>
          <span>返回前台</span>
        </router-link>
      </div>
    </aside>
    <div class="admin-main">
      <header class="admin-header">
        <span class="page-title">{{ route.meta.title?.replace('管理后台 - ', '') }}</span>
        <div class="admin-user">
          <el-avatar :size="28" :src="userStore.avatar" />
          <span>{{ userStore.username }}</span>
        </div>
      </header>
      <main class="admin-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const userStore = useUserStore()

const menuItems = [
  { path: '/admin/dashboard', label: '数据看板', icon: 'DataAnalysis' },
  { path: '/admin/questions', label: '题目管理', icon: 'Document' },
  { path: '/admin/categories', label: '分类管理', icon: 'Menu' },
  { path: '/admin/users', label: '用户管理', icon: 'User' },
  { path: '/admin/announcements', label: '公告管理', icon: 'Bell' },
  { path: '/admin/recommend', label: '推荐算法对比', icon: 'TrendCharts' },
]

function isActive(path) {
  return route.path === path
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
}

.admin-sidebar {
  width: var(--sidebar-width);
  background: var(--bg-sidebar);
  border-right: 1px solid var(--border-default);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
}

.sidebar-header {
  padding: var(--spacing-lg);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xs);
  border-bottom: 1px solid var(--border-light);
}

.sidebar-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  cursor: pointer;
}

.sidebar-badge {
  font-size: 11px;
  color: var(--text-tertiary);
  background: var(--bg-card);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-default);
}

.sidebar-menu {
  flex: 1;
  padding: var(--spacing-sm);
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  height: 44px;
  padding: 0 var(--spacing-md);
  border-radius: var(--radius-md);
  font-size: 14px;
  color: var(--text-secondary);
  transition: all var(--transition-fast);
  text-decoration: none;
}

.menu-item:hover {
  background: var(--border-default);
  color: var(--text-primary);
}

.menu-item.active {
  background: var(--bg-card);
  color: var(--text-primary);
  font-weight: 500;
  box-shadow: var(--shadow-card);
  border-left: 3px solid var(--text-primary);
  padding-left: 13px;
}

.sidebar-footer {
  padding: var(--spacing-md);
  border-top: 1px solid var(--border-light);
}

.back-link {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-xs);
  font-size: 13px;
  color: var(--text-tertiary);
  padding: var(--spacing-sm);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
  text-decoration: none;
}

.back-link:hover {
  color: var(--text-primary);
  background: var(--border-default);
}

.admin-main {
  flex: 1;
  margin-left: var(--sidebar-width);
  display: flex;
  flex-direction: column;
  background: var(--bg-page);
}

.admin-header {
  height: 56px;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-light);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--spacing-lg);
  position: sticky;
  top: 0;
  z-index: 50;
}

.page-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.admin-user {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: 14px;
  color: var(--text-secondary);
}

.admin-content {
  flex: 1;
  padding: var(--spacing-lg);
}
</style>