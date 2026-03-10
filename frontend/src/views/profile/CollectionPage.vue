<template>
  <div class="collection-page">
    <h2 class="page-title">我的收藏</h2>

    <div class="list-wrap" v-loading="loading">
      <div v-if="list.length === 0 && !loading" class="empty-state">
        <p>还没有收藏任何题目</p>
        <button class="btn-secondary" @click="$router.push('/questions')">去题库看看</button>
      </div>

      <div v-for="item in list" :key="item.id" class="item-card">
        <div class="item-left" @click="goDetail(item.question)">
          <h3 class="item-title">{{ item.question.title }}</h3>
          <div class="item-meta">
            <span v-if="item.question.category">{{ item.question.category.name }}</span>
            <span class="meta-dot" v-if="item.question.category && item.question.sub_category">·</span>
            <span v-if="item.question.sub_category">{{ item.question.sub_category.name }}</span>
            <span class="meta-dot">·</span>
            <span>{{ formatDateTime(item.created_at) }} 收藏</span>
          </div>
        </div>
        <div class="item-right">
          <span class="type-tag">{{ item.question.question_type === 'text' ? '简答题' : '代码题' }}</span>
          <span class="diff-tag" :class="item.question.difficulty">{{ diffLabel(item.question.difficulty) }}</span>
          <button class="btn-cancel" @click="handleRemove(item.question.id)">取消收藏</button>
        </div>
      </div>
    </div>

    <div class="pagination-wrap" v-if="total > pageSize">
      <el-pagination
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="fetchList"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getCollections, removeCollection } from '@/api/collections'
import { DIFFICULTY_OPTIONS } from '@/utils/constants'
import { formatDateTime } from '@/utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const list = ref([])
const page = ref(1)
const pageSize = 20
const total = ref(0)

function diffLabel(val) {
  return DIFFICULTY_OPTIONS.find(d => d.value === val)?.label || val
}

function goDetail(q) {
  router.push(q.question_type === 'text' ? `/question/text/${q.id}` : `/question/code/${q.id}`)
}

async function handleRemove(questionId) {
  try {
    await ElMessageBox.confirm('确定取消收藏吗？', '提示', { type: 'warning' })
    await removeCollection(questionId)
    ElMessage.success('已取消收藏')
    fetchList()
  } catch (e) {}
}

async function fetchList() {
  loading.value = true
  try {
    const res = await getCollections({ page: page.value, page_size: pageSize })
    list.value = res.data.results
    total.value = res.data.count
  } catch (e) {}
  finally { loading.value = false }
}

onMounted(fetchList)
</script>

<style scoped>
.collection-page { max-width: 960px; margin: 0 auto; }
.page-title { font-size: 20px; font-weight: 600; color: var(--text-primary); margin-bottom: var(--spacing-lg); }

.list-wrap {
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  overflow: hidden;
  min-height: 200px;
  background: var(--border-light);
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.empty-state {
  padding: var(--spacing-xxl);
  text-align: center;
  color: var(--text-tertiary);
  background: var(--bg-card);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-md);
}

.item-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md) var(--spacing-lg);
  background: var(--bg-card);
  transition: background var(--transition-fast);
}
.item-card:hover { background: var(--bg-hover); }

.item-left { flex: 1; min-width: 0; cursor: pointer; }
.item-title {
  font-size: 15px; font-weight: 500; color: var(--text-primary);
  margin-bottom: 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.item-meta { display: flex; align-items: center; gap: 4px; font-size: 12px; color: var(--text-tertiary); }
.meta-dot { color: var(--text-placeholder); }

.item-right { display: flex; align-items: center; gap: var(--spacing-sm); flex-shrink: 0; margin-left: var(--spacing-md); }
.type-tag { font-size: 12px; color: var(--text-secondary); background: var(--color-info-bg); padding: 2px 10px; border-radius: var(--radius-sm); }
.diff-tag { font-size: 12px; font-weight: 500; padding: 2px 10px; border-radius: var(--radius-sm); }
.diff-tag.easy { color: var(--color-easy); background: var(--color-easy-bg); }
.diff-tag.medium { color: var(--color-medium); background: var(--color-medium-bg); }
.diff-tag.hard { color: var(--color-hard); background: var(--color-hard-bg); }

.btn-cancel {
  height: 28px; padding: 0 12px; background: #fff; color: var(--text-tertiary);
  border: 1px solid var(--border-default); border-radius: var(--radius-sm); font-size: 12px; cursor: pointer;
  transition: all var(--transition-fast);
}
.btn-cancel:hover { color: var(--color-danger); border-color: var(--color-danger); }

.btn-secondary {
  height: 36px; padding: 0 20px; background: #fff; color: var(--text-primary);
  border: 1px solid var(--border-default); border-radius: var(--radius-md); font-size: 14px; cursor: pointer;
}
.btn-secondary:hover { background: var(--bg-hover); }

.pagination-wrap { display: flex; justify-content: center; margin-top: var(--spacing-lg); }
</style>