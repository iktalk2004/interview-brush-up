<template>
  <div class="daily-page">
    <div class="page-header">
      <div>
        <h2 class="page-title">每日推荐</h2>
        <p class="page-desc">基于协同过滤算法为你个性化推荐，每日更新</p>
      </div>
      <span class="date-label">{{ todayStr }}</span>
    </div>

    <div class="daily-list" v-loading="loading">
      <div v-if="list.length === 0 && !loading" class="empty-state">
        <p>暂无推荐，先去题库刷几道题，系统会更了解你的偏好</p>
        <button class="btn-secondary" @click="$router.push('/questions')">去题库</button>
      </div>

      <div v-for="(item, idx) in list" :key="item.id" class="daily-card" :class="{ completed: item.is_completed }">
        <div class="card-index">{{ idx + 1 }}</div>
        <div class="card-body" @click="goDetail(item)">
          <h3 class="card-title">{{ item.title }}</h3>
          <div class="card-meta">
            <span class="meta-cat" v-if="item.category">{{ item.category.name }}</span>
            <span class="meta-sub" v-if="item.sub_category">{{ item.sub_category.name }}</span>
            <span class="meta-diff" :class="item.difficulty">{{ diffLabel(item.difficulty) }}</span>
            <span class="meta-type">{{ item.question_type === 'text' ? '简答题' : '代码题' }}</span>
          </div>
        </div>
        <div class="card-right">
          <span v-if="item.is_completed" class="completed-tag">已完成</span>
          <button v-else class="btn-go" @click="goDetail(item)">去作答</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getDailyRecommend } from '@/api/recommend'
import { DIFFICULTY_OPTIONS } from '@/utils/constants'

const router = useRouter()
const loading = ref(false)
const list = ref([])

const today = new Date()
const todayStr = `${today.getFullYear()}年${today.getMonth() + 1}月${today.getDate()}日`

function diffLabel(val) {
  return DIFFICULTY_OPTIONS.find(d => d.value === val)?.label || val
}

function goDetail(item) {
  router.push(item.question_type === 'text' ? `/question/text/${item.id}` : `/question/code/${item.id}`)
}

onMounted(async () => {
  loading.value = true
  try {
    const res = await getDailyRecommend()
    list.value = res.data
  } catch (e) {}
  finally { loading.value = false }
})
</script>

<style scoped>
.daily-page { max-width: 800px; margin: 0 auto; }

.page-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: var(--spacing-lg); }
.page-title { font-size: 20px; font-weight: 600; color: var(--text-primary); margin-bottom: 4px; }
.page-desc { font-size: 14px; color: var(--text-tertiary); }
.date-label { font-size: 14px; color: var(--text-secondary); background: var(--color-info-bg); padding: 4px 12px; border-radius: var(--radius-sm); }

.daily-list { display: flex; flex-direction: column; gap: var(--spacing-md); min-height: 200px; }
.empty-state {
  text-align: center; color: var(--text-tertiary); padding: var(--spacing-xxl);
  background: var(--bg-card); border: 1px solid var(--border-default); border-radius: var(--radius-lg);
  display: flex; flex-direction: column; align-items: center; gap: var(--spacing-md);
}
.btn-secondary {
  height: 36px; padding: 0 20px; background: #fff; color: var(--text-primary);
  border: 1px solid var(--border-default); border-radius: var(--radius-md); font-size: 14px; cursor: pointer;
}
.btn-secondary:hover { background: var(--bg-hover); }

.daily-card {
  display: flex; align-items: center; gap: var(--spacing-md);
  background: var(--bg-card); border: 1px solid var(--border-default); border-radius: var(--radius-lg);
  padding: var(--spacing-md) var(--spacing-lg); box-shadow: var(--shadow-card);
  transition: all var(--transition-base);
}
.daily-card:hover { box-shadow: var(--shadow-card-hover); }
.daily-card.completed { opacity: 0.6; }

.card-index {
  width: 32px; height: 32px; border-radius: 50%; background: var(--bg-page);
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 600; color: var(--text-secondary); flex-shrink: 0;
}

.card-body { flex: 1; min-width: 0; cursor: pointer; }
.card-title { font-size: 15px; font-weight: 500; color: var(--text-primary); margin-bottom: 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.card-meta { display: flex; align-items: center; gap: var(--spacing-sm); flex-wrap: wrap; }
.meta-cat, .meta-sub { font-size: 12px; color: var(--text-secondary); background: var(--color-info-bg); padding: 1px 8px; border-radius: var(--radius-sm); }
.meta-diff { font-size: 12px; font-weight: 500; padding: 1px 8px; border-radius: var(--radius-sm); }
.meta-diff.easy { color: var(--color-easy); background: var(--color-easy-bg); }
.meta-diff.medium { color: var(--color-medium); background: var(--color-medium-bg); }
.meta-diff.hard { color: var(--color-hard); background: var(--color-hard-bg); }
.meta-type { font-size: 11px; color: var(--text-tertiary); }

.card-right { flex-shrink: 0; }
.completed-tag { font-size: 12px; color: var(--color-easy); background: var(--color-easy-bg); padding: 4px 12px; border-radius: var(--radius-sm); }
.btn-go {
  height: 32px; padding: 0 16px; background: var(--btn-primary-bg); color: var(--btn-primary-text);
  border: none; border-radius: var(--radius-md); font-size: 13px; font-weight: 500; cursor: pointer;
  transition: background var(--transition-fast);
}
.btn-go:hover { background: var(--btn-primary-hover); }
</style>