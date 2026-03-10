<template>
  <div class="session-page">
    <!-- 顶部进度条 -->
    <div class="session-header">
      <button class="btn-back" @click="handleBack">← 返回专题</button>
      <div class="session-progress">
        <span class="progress-label">进度 {{ currentIndex + 1 }}/{{ questions.length }}</span>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
        </div>
      </div>
      <div class="session-mode">
        <span class="mode-label">模式</span>
        <el-radio-group v-model="mode" size="small" @change="handleModeChange">
          <el-radio-button value="order">顺序</el-radio-button>
          <el-radio-button value="random">随机</el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <div class="session-body" v-loading="loading">
      <div v-if="questions.length === 0 && !loading" class="empty-state">
        <p>该专题暂无题目</p>
        <button class="btn-secondary" @click="$router.push('/practice')">返回专题列表</button>
      </div>

      <template v-if="currentQuestion">
        <!-- 题目列表侧边 -->
        <div class="question-nav">
          <div
            v-for="(q, idx) in questions"
            :key="q.id"
            class="nav-dot"
            :class="{
              active: idx === currentIndex,
              done: q.is_done,
              scored: q.sessionScore !== undefined
            }"
            @click="currentIndex = idx"
          >
            {{ idx + 1 }}
          </div>
        </div>

        <!-- 题目主体 -->
        <div class="question-area">
          <div class="question-header">
            <h2 class="question-title">{{ currentQuestion.title }}</h2>
            <div class="question-tags">
              <span class="cat-tag" v-if="currentQuestion.category">{{ currentQuestion.category.name }}</span>
              <span class="diff-tag" :class="currentQuestion.difficulty">{{ diffLabel(currentQuestion.difficulty) }}</span>
              <span class="type-tag">{{ currentQuestion.question_type === 'text' ? '简答题' : '代码题' }}</span>
              <span class="done-tag" v-if="currentQuestion.is_done">已做过 · 最高{{ currentQuestion.best_score }}分</span>
            </div>
          </div>

          <!-- 快捷跳转到详情页作答 -->
          <div class="action-area">
            <button class="btn-primary btn-lg" @click="goAnswer">前往作答</button>
            <div class="nav-buttons">
              <button class="btn-secondary" :disabled="currentIndex === 0" @click="currentIndex--">上一题</button>
              <button class="btn-secondary" :disabled="currentIndex === questions.length - 1" @click="currentIndex++">下一题</button>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getTopicQuestions } from '@/api/practice'
import { DIFFICULTY_OPTIONS } from '@/utils/constants'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const questions = ref([])
const currentIndex = ref(0)
const mode = ref('order')

const currentQuestion = computed(() => questions.value[currentIndex.value] || null)
const progressPercent = computed(() => {
  if (questions.value.length === 0) return 0
  return Math.round((currentIndex.value + 1) / questions.value.length * 100)
})

function diffLabel(val) {
  return DIFFICULTY_OPTIONS.find(d => d.value === val)?.label || val
}

function goAnswer() {
  if (!currentQuestion.value) return
  const q = currentQuestion.value
  router.push(q.question_type === 'text' ? `/question/text/${q.id}` : `/question/code/${q.id}`)
}

function handleBack() {
  router.push('/practice')
}

function handleModeChange() {
  fetchQuestions()
}

async function fetchQuestions() {
  loading.value = true
  try {
    const params = { mode: mode.value }
    if (route.query.category) params.category = route.query.category
    if (route.query.sub_category) params.sub_category = route.query.sub_category
    const res = await getTopicQuestions(params)
    questions.value = res.data
    currentIndex.value = 0
  } catch (e) {}
  finally { loading.value = false }
}

onMounted(fetchQuestions)
</script>

<style scoped>
.session-page { max-width: 960px; margin: 0 auto; }

.session-header {
  display: flex; align-items: center; gap: var(--spacing-lg);
  padding: var(--spacing-md) 0; margin-bottom: var(--spacing-lg);
  border-bottom: 1px solid var(--border-light);
}

.btn-back {
  background: none; border: none; font-size: 14px; color: var(--text-secondary); cursor: pointer;
  padding: 4px 0; white-space: nowrap;
}
.btn-back:hover { color: var(--text-primary); }

.session-progress { flex: 1; display: flex; align-items: center; gap: var(--spacing-sm); }
.progress-label { font-size: 13px; color: var(--text-secondary); min-width: 60px; }
.progress-bar { flex: 1; height: 4px; background: var(--border-light); border-radius: 2px; overflow: hidden; }
.progress-fill { height: 100%; background: var(--text-primary); border-radius: 2px; transition: width 0.3s ease; }

.session-mode { display: flex; align-items: center; gap: var(--spacing-sm); }
.mode-label { font-size: 13px; color: var(--text-tertiary); }

.session-body { display: flex; gap: var(--spacing-lg); min-height: 400px; }

.empty-state {
  flex: 1; text-align: center; color: var(--text-tertiary); padding: var(--spacing-xxl);
  display: flex; flex-direction: column; align-items: center; gap: var(--spacing-md);
}

.question-nav {
  display: flex; flex-wrap: wrap; gap: 6px; width: 200px; flex-shrink: 0;
  align-content: flex-start;
}

.nav-dot {
  width: 36px; height: 36px; border-radius: var(--radius-md);
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 500; color: var(--text-secondary);
  background: var(--bg-page); border: 1px solid var(--border-default);
  cursor: pointer; transition: all var(--transition-fast);
}
.nav-dot:hover { border-color: var(--text-primary); color: var(--text-primary); }
.nav-dot.active { background: var(--btn-primary-bg); color: #fff; border-color: var(--btn-primary-bg); }
.nav-dot.done { background: var(--color-easy-bg); color: var(--color-easy); border-color: var(--color-easy); }
.nav-dot.active.done { background: var(--btn-primary-bg); color: #fff; border-color: var(--btn-primary-bg); }

.question-area {
  flex: 1; background: var(--bg-card); border: 1px solid var(--border-default);
  border-radius: var(--radius-lg); padding: var(--spacing-xl); box-shadow: var(--shadow-card);
}

.question-header { margin-bottom: var(--spacing-xl); }
.question-title { font-size: 20px; font-weight: 600; color: var(--text-primary); line-height: 1.4; margin-bottom: var(--spacing-sm); }
.question-tags { display: flex; align-items: center; gap: var(--spacing-sm); flex-wrap: wrap; }
.cat-tag { font-size: 12px; color: var(--text-secondary); background: var(--color-info-bg); padding: 2px 10px; border-radius: var(--radius-sm); }
.diff-tag { font-size: 12px; font-weight: 500; padding: 2px 10px; border-radius: var(--radius-sm); }
.diff-tag.easy { color: var(--color-easy); background: var(--color-easy-bg); }
.diff-tag.medium { color: var(--color-medium); background: var(--color-medium-bg); }
.diff-tag.hard { color: var(--color-hard); background: var(--color-hard-bg); }
.type-tag { font-size: 12px; color: var(--text-tertiary); background: var(--color-info-bg); padding: 2px 10px; border-radius: var(--radius-sm); }
.done-tag { font-size: 12px; color: var(--color-easy); }

.action-area { display: flex; flex-direction: column; gap: var(--spacing-lg); }

.nav-buttons { display: flex; gap: var(--spacing-md); }

.btn-primary {
  height: 44px; padding: 0 32px; background: var(--btn-primary-bg); color: var(--btn-primary-text);
  border: none; border-radius: var(--radius-md); font-size: 15px; font-weight: 500; cursor: pointer;
  transition: background var(--transition-fast);
}
.btn-primary:hover { background: var(--btn-primary-hover); }
.btn-lg { height: 48px; font-size: 16px; }

.btn-secondary {
  height: 40px; padding: 0 24px; background: #fff; color: var(--text-primary);
  border: 1px solid var(--border-default); border-radius: var(--radius-md); font-size: 14px; cursor: pointer;
  transition: all var(--transition-fast);
}
.btn-secondary:hover { background: var(--bg-hover); }
.btn-secondary:disabled { color: var(--text-placeholder); cursor: not-allowed; }
</style>