<template>
  <div class="mistakes-page">
    <h2 class="page-title">错题本</h2>

    <!-- 筛选 -->
    <div class="filter-bar" v-if="categories.length">
      <div class="filter-group">
        <span class="filter-label">分类</span>
        <div class="filter-tags">
          <span class="tag" :class="{ active: !filters.category }" @click="filters.category = null; fetchList()">全部</span>
          <span
            v-for="cat in categories"
            :key="cat.id"
            class="tag"
            :class="{ active: filters.category === cat.id }"
            @click="filters.category = cat.id; fetchList()"
          >{{ cat.name }}</span>
        </div>
      </div>
      <div class="filter-group">
        <span class="filter-label">难度</span>
        <div class="filter-tags">
          <span class="tag" :class="{ active: !filters.difficulty }" @click="filters.difficulty = null; fetchList()">全部</span>
          <span
            v-for="d in DIFFICULTY_OPTIONS"
            :key="d.value"
            class="tag"
            :class="{ active: filters.difficulty === d.value }"
            @click="filters.difficulty = d.value; fetchList()"
          >{{ d.label }}</span>
        </div>
      </div>
    </div>

    <div class="list-wrap" v-loading="loading">
      <div v-if="list.length === 0 && !loading" class="empty-state">
        <p>错题本空空如也，继续保持！</p>
      </div>

      <div v-for="item in list" :key="item.id" class="item-card">
        <div class="item-left" @click="goDetail(item)">
          <h3 class="item-title">{{ item.question_title }}</h3>
          <div class="item-meta">
            <span>提交 {{ item.attempt_count }} 次</span>
            <span class="meta-dot">·</span>
            <span>最高 {{ item.best_score }} 分</span>
            <span class="meta-dot">·</span>
            <span>最近 {{ item.latest_score }} 分</span>
          </div>
        </div>
        <div class="item-right">
          <span class="type-tag">{{ item.question_type === 'text' ? '简答题' : '代码题' }}</span>
          <button class="btn-redo" @click="goDetail(item)">重新作答</button>
          <button class="btn-remove" @click="handleRemove(item.question_id)">移除</button>
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
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getMistakes, removeMistake } from '@/api/practice'
import { getCategories } from '@/api/questions'
import { DIFFICULTY_OPTIONS } from '@/utils/constants'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const list = ref([])
const categories = ref([])
const page = ref(1)
const pageSize = 20
const total = ref(0)

const filters = reactive({
  category: null,
  difficulty: null,
})

function goDetail(item) {
  router.push(item.question_type === 'text' ? `/question/text/${item.question_id}` : `/question/code/${item.question_id}`)
}

async function handleRemove(questionId) {
  try {
    await ElMessageBox.confirm('确定从错题本移除吗？', '提示', { type: 'warning' })
    await removeMistake(questionId)
    ElMessage.success('已移除')
    fetchList()
  } catch (e) {}
}

async function fetchList() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize }
    if (filters.category) params.category = filters.category
    if (filters.difficulty) params.difficulty = filters.difficulty
    const res = await getMistakes(params)
    list.value = res.data.results
    total.value = res.data.count
  } catch (e) {}
  finally { loading.value = false }
}

async function fetchCategories() {
  try {
    const res = await getCategories()
    categories.value = res.data
  } catch (e) {}
}

onMounted(() => {
  fetchCategories()
  fetchList()
})
</script>

<style scoped>
.mistakes-page { max-width: 960px; margin: 0 auto; }
.page-title { font-size: 20px; font-weight: 600; color: var(--text-primary); margin-bottom: var(--spacing-lg); }

.filter-bar {
  background: var(--bg-card); border: 1px solid var(--border-default); border-radius: var(--radius-lg);
  padding: var(--spacing-md) var(--spacing-lg); margin-bottom: var(--spacing-lg);
  display: flex; flex-direction: column; gap: var(--spacing-sm);
}
.filter-group { display: flex; align-items: center; gap: var(--spacing-md); }
.filter-label { font-size: 13px; color: var(--text-tertiary); min-width: 32px; }
.filter-tags { display: flex; flex-wrap: wrap; gap: var(--spacing-sm); }
.tag {
  padding: 4px 14px; border-radius: var(--radius-sm); font-size: 13px;
  color: var(--text-secondary); cursor: pointer; transition: all var(--transition-fast); border: 1px solid transparent;
}
.tag:hover { color: var(--text-primary); background: var(--bg-hover); }
.tag.active { color: var(--text-primary); font-weight: 500; background: var(--bg-card); border-color: var(--border-default); box-shadow: var(--shadow-card); }

.list-wrap {
  border: 1px solid var(--border-default); border-radius: var(--radius-lg); overflow: hidden;
  min-height: 200px; background: var(--border-light); display: flex; flex-direction: column; gap: 1px;
}
.empty-state { padding: var(--spacing-xxl); text-align: center; color: var(--text-tertiary); background: var(--bg-card); }

.item-card {
  display: flex; align-items: center; justify-content: space-between;
  padding: var(--spacing-md) var(--spacing-lg); background: var(--bg-card); transition: background var(--transition-fast);
}
.item-card:hover { background: var(--bg-hover); }

.item-left { flex: 1; min-width: 0; cursor: pointer; }
.item-title { font-size: 15px; font-weight: 500; color: var(--text-primary); margin-bottom: 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.item-meta { display: flex; align-items: center; gap: 4px; font-size: 12px; color: var(--text-tertiary); }
.meta-dot { color: var(--text-placeholder); }

.item-right { display: flex; align-items: center; gap: var(--spacing-sm); flex-shrink: 0; margin-left: var(--spacing-md); }
.type-tag { font-size: 12px; color: var(--text-secondary); background: var(--color-info-bg); padding: 2px 10px; border-radius: var(--radius-sm); }

.btn-redo {
  height: 28px; padding: 0 12px; background: var(--btn-primary-bg); color: var(--btn-primary-text);
  border: none; border-radius: var(--radius-sm); font-size: 12px; cursor: pointer; transition: background var(--transition-fast);
}
.btn-redo:hover { background: var(--btn-primary-hover); }

.btn-remove {
  height: 28px; padding: 0 12px; background: #fff; color: var(--text-tertiary);
  border: 1px solid var(--border-default); border-radius: var(--radius-sm); font-size: 12px; cursor: pointer;
  transition: all var(--transition-fast);
}
.btn-remove:hover { color: var(--color-danger); border-color: var(--color-danger); }

.pagination-wrap { display: flex; justify-content: center; margin-top: var(--spacing-lg); }
</style>