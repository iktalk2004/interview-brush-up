<template>
  <div class="practice-page">
    <h2 class="page-title">专题练习</h2>
    <p class="page-desc">选择一个专题，系统化刷题，查漏补缺</p>

    <div class="topic-list" v-loading="loading">
      <div v-if="topics.length === 0 && !loading" class="empty-state">
        <p>暂无专题，请等待管理员添加题目</p>
      </div>

      <div v-for="cat in topics" :key="cat.id" class="topic-group">
        <!-- 一级分类头部 -->
        <div class="group-header" @click="toggleExpand(cat.id)">
          <div class="group-left">
            <el-icon :size="16" :class="{ rotated: expandedIds.has(cat.id) }"><ArrowRight /></el-icon>
            <h3 class="group-name">{{ cat.name }}</h3>
            <span class="group-desc" v-if="cat.description">{{ cat.description }}</span>
          </div>
          <div class="group-right">
            <div class="progress-info">
              <span class="progress-text">{{ cat.done }}/{{ cat.total }}</span>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: percent(cat.done, cat.total) + '%' }"></div>
              </div>
            </div>
            <button class="btn-start" @click.stop="startPractice(cat.id, null)">开始练习</button>
          </div>
        </div>

        <!-- 二级分类列表 -->
        <div class="sub-list" v-show="expandedIds.has(cat.id)">
          <div v-for="sub in cat.sub_categories" :key="sub.id" class="sub-item">
            <div class="sub-left">
              <span class="sub-name">{{ sub.name }}</span>
              <span class="sub-stats">
                <span class="stat-done">{{ sub.done }}</span>/<span>{{ sub.total }}</span>
                <span class="stat-correct" v-if="sub.correct > 0">（掌握 {{ sub.correct }}）</span>
              </span>
            </div>
            <div class="sub-right">
              <div class="progress-bar small">
                <div class="progress-fill" :style="{ width: percent(sub.done, sub.total) + '%' }"></div>
              </div>
              <button class="btn-start-sm" @click="startPractice(cat.id, sub.id)">练习</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getTopicList } from '@/api/practice'

const router = useRouter()
const loading = ref(false)
const topics = ref([])
const expandedIds = ref(new Set())

function percent(done, total) {
  if (!total) return 0
  return Math.round(done / total * 100)
}

function toggleExpand(id) {
  if (expandedIds.value.has(id)) {
    expandedIds.value.delete(id)
  } else {
    expandedIds.value.add(id)
  }
  // 触发响应式更新
  expandedIds.value = new Set(expandedIds.value)
}

function startPractice(categoryId, subCategoryId) {
  const query = { category: categoryId }
  if (subCategoryId) query.sub_category = subCategoryId
  router.push({ path: '/practice/session', query })
}

onMounted(async () => {
  loading.value = true
  try {
    const res = await getTopicList()
    topics.value = res.data
    // 默认展开第一个
    if (topics.value.length > 0) {
      expandedIds.value.add(topics.value[0].id)
    }
  } catch (e) {}
  finally { loading.value = false }
})
</script>

<style scoped>
.practice-page { max-width: 900px; margin: 0 auto; }
.page-title { font-size: 20px; font-weight: 600; color: var(--text-primary); margin-bottom: 4px; }
.page-desc { font-size: 14px; color: var(--text-tertiary); margin-bottom: var(--spacing-lg); }

.topic-list { display: flex; flex-direction: column; gap: var(--spacing-md); min-height: 200px; }
.empty-state { text-align: center; color: var(--text-tertiary); padding: var(--spacing-xxl); }

.topic-group {
  background: var(--bg-card); border: 1px solid var(--border-default); border-radius: var(--radius-lg);
  overflow: hidden; box-shadow: var(--shadow-card);
}

.group-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: var(--spacing-md) var(--spacing-lg); cursor: pointer;
  transition: background var(--transition-fast);
}
.group-header:hover { background: var(--bg-hover); }

.group-left { display: flex; align-items: center; gap: var(--spacing-sm); }
.group-left .el-icon { transition: transform var(--transition-base); color: var(--text-tertiary); }
.group-left .el-icon.rotated { transform: rotate(90deg); }
.group-name { font-size: 16px; font-weight: 600; color: var(--text-primary); }
.group-desc { font-size: 13px; color: var(--text-tertiary); margin-left: var(--spacing-sm); }

.group-right { display: flex; align-items: center; gap: var(--spacing-lg); }

.progress-info { display: flex; align-items: center; gap: var(--spacing-sm); }
.progress-text { font-size: 13px; color: var(--text-secondary); min-width: 48px; text-align: right; }

.progress-bar {
  width: 120px; height: 6px; background: var(--border-light); border-radius: 3px; overflow: hidden;
}
.progress-bar.small { width: 80px; height: 4px; }
.progress-fill {
  height: 100%; background: var(--text-primary); border-radius: 3px;
  transition: width 0.3s ease;
}

.btn-start {
  height: 32px; padding: 0 16px; background: var(--btn-primary-bg); color: var(--btn-primary-text);
  border: none; border-radius: var(--radius-md); font-size: 13px; font-weight: 500; cursor: pointer;
  transition: background var(--transition-fast); white-space: nowrap;
}
.btn-start:hover { background: var(--btn-primary-hover); }

.sub-list { border-top: 1px solid var(--border-light); }

.sub-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: var(--spacing-sm) var(--spacing-lg); padding-left: 52px;
  transition: background var(--transition-fast);
}
.sub-item:hover { background: var(--bg-hover); }
.sub-item + .sub-item { border-top: 1px solid var(--border-light); }

.sub-left { display: flex; align-items: center; gap: var(--spacing-md); }
.sub-name { font-size: 14px; color: var(--text-primary); }
.sub-stats { font-size: 12px; color: var(--text-tertiary); }
.stat-done { font-weight: 500; color: var(--text-secondary); }
.stat-correct { color: var(--color-easy); }

.sub-right { display: flex; align-items: center; gap: var(--spacing-md); }

.btn-start-sm {
  height: 28px; padding: 0 14px; background: #fff; color: var(--text-primary);
  border: 1px solid var(--border-default); border-radius: var(--radius-sm); font-size: 12px; cursor: pointer;
  transition: all var(--transition-fast); white-space: nowrap;
}
.btn-start-sm:hover { background: var(--bg-hover); border-color: var(--text-primary); }
</style>