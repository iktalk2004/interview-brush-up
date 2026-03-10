<template>
  <div class="user-manage">
    <div class="page-header">
      <h3>用户管理</h3>
      <el-input v-model="search" placeholder="搜索用户名或邮箱" clearable style="width: 280px" @keyup.enter="fetchList" @clear="fetchList">
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
    </div>

    <div class="table-wrap" v-loading="loading">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>用户名</th>
            <th>邮箱</th>
            <th>角色</th>
            <th>技术水平</th>
            <th>注册时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="list.length === 0 && !loading">
            <td colspan="7" class="empty-cell">暂无数据</td>
          </tr>
          <tr v-for="item in list" :key="item.id">
            <td>{{ item.id }}</td>
            <td>
              <div class="user-cell">
                <el-avatar :size="24" :src="item.avatar || '/default-avatar.png'" />
                <span>{{ item.username }}</span>
              </div>
            </td>
            <td>{{ item.email }}</td>
            <td><span class="role-tag" :class="item.role">{{ item.role === 'admin' ? '管理员' : '用户' }}</span></td>
            <td>{{ techLabel(item.tech_level) }}</td>
            <td>{{ formatDateTime(item.date_joined) }}</td>
            <td>
              <button v-if="item.role !== 'admin'" class="btn-text" @click="handleToggle(item)">
                {{ item.is_active !== false ? '禁用' : '启用' }}
              </button>
              <span v-else class="text-muted">-</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="pagination-wrap" v-if="total > pageSize">
      <el-pagination v-model:current-page="page" :page-size="pageSize" :total="total" layout="prev, pager, next" @current-change="fetchList" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAdminUsers, toggleUserStatus } from '@/api/admin'
import { TECH_LEVEL_OPTIONS } from '@/utils/constants'
import { formatDateTime } from '@/utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const list = ref([])
const search = ref('')
const page = ref(1)
const pageSize = 20
const total = ref(0)

function techLabel(val) {
  return TECH_LEVEL_OPTIONS.find(t => t.value === val)?.label || val
}

async function handleToggle(item) {
  const action = item.is_active !== false ? '禁用' : '启用'
  try {
    await ElMessageBox.confirm(`确定${action}用户 ${item.username} 吗？`, '提示', { type: 'warning' })
    await toggleUserStatus(item.id)
    ElMessage.success(`已${action}`)
    fetchList()
  } catch (e) {}
}

async function fetchList() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize }
    if (search.value) params.search = search.value
    const res = await getAdminUsers(params)
    list.value = res.data.results
    total.value = res.data.count
  } catch (e) {}
  finally { loading.value = false }
}

onMounted(fetchList)
</script>

<style scoped>
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--spacing-lg); }
.page-header h3 { font-size: 16px; font-weight: 600; color: var(--text-primary); }

.table-wrap {
  background: var(--bg-card); border: 1px solid var(--border-default); border-radius: var(--radius-lg);
  overflow: hidden; box-shadow: var(--shadow-card);
}

.data-table { width: 100%; border-collapse: collapse; }
.data-table th {
  text-align: left; padding: var(--spacing-sm) var(--spacing-md);
  font-size: 13px; font-weight: 500; color: var(--text-secondary); background: var(--bg-table-header);
  border-bottom: 1px solid var(--border-default);
}
.data-table td {
  padding: var(--spacing-sm) var(--spacing-md); font-size: 14px; color: var(--text-primary);
  border-bottom: 1px solid var(--border-light);
}
.data-table tr:hover td { background: var(--bg-hover); }
.empty-cell { text-align: center; color: var(--text-tertiary); padding: var(--spacing-xxl) !important; }

.user-cell { display: flex; align-items: center; gap: var(--spacing-sm); }
.role-tag { font-size: 12px; padding: 2px 8px; border-radius: var(--radius-sm); }
.role-tag.admin { color: var(--color-medium); background: var(--color-medium-bg); }
.role-tag.user { color: var(--text-tertiary); background: var(--color-info-bg); }
.text-muted { color: var(--text-placeholder); font-size: 13px; }

.btn-text {
  background: none; border: none; font-size: 13px; color: var(--text-secondary); cursor: pointer;
  padding: 4px 8px; border-radius: var(--radius-sm); transition: all var(--transition-fast);
}
.btn-text:hover { color: var(--color-danger); background: var(--bg-hover); }

.pagination-wrap { display: flex; justify-content: center; margin-top: var(--spacing-lg); }
</style>