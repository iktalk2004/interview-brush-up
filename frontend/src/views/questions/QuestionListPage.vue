<template>
  <div class="question-list-page">
    <h2 class="page-title">题库</h2>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input
        v-model="searchText"
        placeholder="搜索题目..."
        size="large"
        clearable
        @keyup.enter="handleSearch"
        @clear="handleSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </div>

    <!-- 筛选条件 -->
    <div class="filter-bar">
      <div class="filter-group">
        <span class="filter-label">分类</span>
        <div class="filter-tags">
          <span class="tag" :class="{ active: !filters.category }" @click="setCategory(null)">全部</span>
          <span
            v-for="cat in categories"
            :key="cat.id"
            class="tag"
            :class="{ active: filters.category === cat.id }"
            @click="setCategory(cat.id)"
          >
            {{ cat.name }}
          </span>
        </div>
      </div>

      <div class="filter-group" v-if="subCategories.length">
        <span class="filter-label">子分类</span>
        <div class="filter-tags">
          <span class="tag" :class="{ active: !filters.sub_category }" @click="filters.sub_category = null; fetchQuestions()">全部</span>
          <span
            v-for="sub in subCategories"
            :key="sub.id"
            class="tag"
            :class="{ active: filters.sub_category === sub.id }"
            @click="filters.sub_category = sub.id; fetchQuestions()"
          >
            {{ sub.name }}
          </span>
        </div>
      </div>

      <div class="filter-group">
        <span class="filter-label">难度</span>
        <div class="filter-tags">
          <span class="tag" :class="{ active: !filters.difficulty }" @click="filters.difficulty = null; fetchQuestions()">全部</span>
          <span
            v-for="d in DIFFICULTY_OPTIONS"
            :key="d.value"
            class="tag"
            :class="{ active: filters.difficulty === d.value }"
            @click="filters.difficulty = d.value; fetchQuestions()"
          >
            {{ d.label }}
          </span>
        </div>
      </div>

      <div class="filter-group">
        <span class="filter-label">题型</span>
        <div class="filter-tags">
          <span class="tag" :class="{ active: !filters.question_type }" @click="filters.question_type = null; fetchQuestions()">全部</span>
          <span
            v-for="t in QUESTION_TYPE_OPTIONS"
            :key="t.value"
            class="tag"
            :class="{ active: filters.question_type === t.value }"
            @click="filters.question_type = t.value; fetchQuestions()"
          >
            {{ t.label }}
          </span>
        </div>
      </div>
    </div>

    <!-- 题目列表 -->
    <div class="question-list" v-loading="loading">
      <div v-if="questions.length === 0 && !loading" class="empty-state">
        <p>暂无题目</p>
      </div>

      <div
        v-for="item in questions"
        :key="item.id"
        class="question-card"
        @click="goDetail(item)"
      >
        <div class="card-left">
          <h3 class="card-title">{{ item.title }}</h3>
          <div class="card-meta">
            <span class="meta-item" v-if="item.category">{{ item.category.name }}</span>
            <span class="meta-dot" v-if="item.category && item.sub_category">·</span>
            <span class="meta-item" v-if="item.sub_category">{{ item.sub_category.name }}</span>
          </div>
          <div class="card-stats" v-if="item.stat">
            <span class="stat-item">
              <span class="stat-label">提交</span>
              <span class="stat-value">{{ item.stat.submission_count || 0 }}</span>
            </span>
            <span class="stat-item">
              <span class="stat-label">通过率</span>
              <span class="stat-value">{{ (item.stat.pass_rate || 0).toFixed(1) }}%</span>
            </span>
            <span class="stat-item">
              <span class="stat-label">平均分</span>
              <span class="stat-value">{{ (item.stat.average_score || 0).toFixed(1) }}</span>
            </span>
          </div>
        </div>
        <div class="card-right">
          <span v-if="item.is_done" class="done-tag">已完成</span>
          <span class="type-tag">{{ item.question_type === 'text' ? '简答题' : '代码题' }}</span>
          <span class="diff-tag" :class="item.difficulty">
            {{ difficultyLabel(item.difficulty) }}
          </span>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrap" v-if="total > 0">
      <el-pagination
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="fetchQuestions"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getQuestions, getCategories } from '@/api/questions'
import { DIFFICULTY_OPTIONS, QUESTION_TYPE_OPTIONS } from '@/utils/constants'

const router = useRouter()
const loading = ref(false)
const searchText = ref('')
const categories = ref([])
const questions = ref([])
const page = ref(1)
const pageSize = 20
const total = ref(0)

const filters = reactive({
  category: null,
  sub_category: null,
  difficulty: null,
  question_type: null,
})

const subCategories = computed(() => {
  if (!filters.category) return []
  const cat = categories.value.find(c => c.id === filters.category)
  return cat?.sub_categories || []
})

function difficultyLabel(val) {
  const item = DIFFICULTY_OPTIONS.find(d => d.value === val)
  return item ? item.label : val
}

function setCategory(id) {
  filters.category = id
  filters.sub_category = null
  fetchQuestions()
}

function handleSearch() {
  page.value = 1
  fetchQuestions()
}

function goDetail(item) {
  if (item.question_type === 'text') {
    router.push(`/question/text/${item.id}`)
  } else {
    router.push(`/question/code/${item.id}`)
  }
}

async function fetchCategories() {
  try {
    const res = await getCategories()
    categories.value = res.data
  } catch (e) {}
}

async function fetchQuestions() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize }
    if (filters.category) params.category = filters.category
    if (filters.sub_category) params.sub_category = filters.sub_category
    if (filters.difficulty) params.difficulty = filters.difficulty
    if (filters.question_type) params.question_type = filters.question_type
    if (searchText.value) params.search = searchText.value

    const res = await getQuestions(params)
    questions.value = res.data.results
    total.value = res.data.count
  } catch (e) {}
  finally { loading.value = false }
}

onMounted(() => {
  fetchCategories()
  fetchQuestions()
})
</script>

<style scoped>
.question-list-page {
  max-width: 960px;
  margin: 0 auto;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--spacing-lg);
}

.search-bar {
  margin-bottom: var(--spacing-lg);
}

.filter-bar {
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.filter-group {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md);
}

.filter-label {
  font-size: 13px;
  color: var(--text-tertiary);
  min-width: 44px;
  padding-top: 5px;
}

.filter-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
}

.tag {
  padding: 4px 14px;
  border-radius: var(--radius-sm);
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
  border: 1px solid transparent;
}

.tag:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}

.tag.active {
  color: var(--text-primary);
  font-weight: 500;
  background: var(--bg-card);
  border-color: var(--border-default);
  box-shadow: var(--shadow-card);
}

.question-list {
  display: flex;
  flex-direction: column;
  gap: 1px;
  background: var(--border-light);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  overflow: hidden;
  min-height: 200px;
}

.question-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md) var(--spacing-lg);
  background: var(--bg-card);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.question-card:hover {
  background: var(--bg-hover);
}

.card-left {
  flex: 1;
  min-width: 0;
}

.card-title {
  font-size: 15px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--text-tertiary);
}

.meta-dot {
  color: var(--text-placeholder);
}

.card-stats {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-top: 6px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
}

.stat-label {
  color: var(--text-tertiary);
}

.stat-value {
  color: var(--text-secondary);
  font-weight: 500;
}

.card-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  flex-shrink: 0;
  margin-left: var(--spacing-md);
}

.type-tag {
  font-size: 12px;
  color: var(--text-secondary);
  background: var(--color-info-bg);
  padding: 2px 10px;
  border-radius: var(--radius-sm);
}

.done-tag {
  font-size: 12px;
  color: var(--color-easy);
  background: var(--color-easy-bg);
  padding: 2px 10px;
  border-radius: var(--radius-sm);
  font-weight: 500;
}

.diff-tag {
  font-size: 12px;
  font-weight: 500;
  padding: 2px 10px;
  border-radius: var(--radius-sm);
}

.diff-tag.easy {
  color: var(--color-easy);
  background: var(--color-easy-bg);
}

.diff-tag.medium {
  color: var(--color-medium);
  background: var(--color-medium-bg);
}

.diff-tag.hard {
  color: var(--color-hard);
  background: var(--color-hard-bg);
}

.empty-state {
  padding: var(--spacing-xxl);
  text-align: center;
  color: var(--text-tertiary);
  background: var(--bg-card);
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: var(--spacing-lg);
}
</style>
