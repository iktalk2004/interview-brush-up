<template>
  <div class="text-question-page" v-loading="loading">
    <template v-if="question">
      <!-- 题目头部 -->
      <div class="question-header">
        <h1 class="question-title">{{ question.title }}</h1>
        <div class="question-header-row">
          <div class="question-tags">
            <span class="cat-tag" v-if="question.category">{{ question.category.name }}</span>
            <span class="cat-tag" v-if="question.sub_category">{{ question.sub_category.name }}</span>
            <span class="diff-tag" :class="question.difficulty">{{ difficultyLabel(question.difficulty) }}</span>
          </div>
          <button class="btn-collect" :class="{ collected: isCollected }" @click="toggleCollect">
            <el-icon :size="16"><Star /></el-icon>
            {{ isCollected ? '已收藏' : '收藏' }}
          </button>
        </div>
      </div>

      <!-- 题干 -->
      <div class="section" v-if="question.text_detail?.content">
        <div class="content-text">{{ question.text_detail.content }}</div>
      </div>

      <div class="divider"></div>

      <!-- 答题区 -->
      <div class="section">
        <h3 class="section-title">你的答案</h3>
        <el-input v-model="userAnswer" type="textarea" :rows="8" placeholder="请输入你的答案..." resize="vertical" />
        <div class="submit-row">
          <div class="scoring-select">
            <span class="scoring-label">评分方式</span>
            <el-radio-group v-model="scoringMethod" size="small">
              <el-radio-button value="model">内嵌模型</el-radio-button>
              <el-radio-button value="deepseek">DeepSeek AI</el-radio-button>
            </el-radio-group>
          </div>
          <button class="btn-primary" :disabled="!userAnswer.trim() || submitting" @click="handleSubmit">
            {{ submitting ? '评分中...' : '提交答案' }}
          </button>
        </div>
      </div>

      <!-- 评分结果 -->
      <div class="section result-section" v-if="scoreResult">
        <h3 class="section-title">评分结果</h3>
        <div class="score-display">
          <span class="score-number" :class="scoreClass">{{ scoreResult.score }}</span>
          <span class="score-unit">分</span>
        </div>
        <p class="score-feedback" v-if="scoreResult.feedback">{{ scoreResult.feedback }}</p>
        <div class="score-meta">
          <span>评分方式：{{ scoreResult.scoring_method === 'model' ? '内嵌模型' : 'DeepSeek AI' }}</span>
          <span :class="scoreResult.is_correct ? 'status-pass' : 'status-fail'">
            {{ scoreResult.is_correct ? '已掌握' : '未掌握' }}
          </span>
        </div>
      </div>

      <div class="divider"></div>

      <!-- 参考答案 -->
      <div class="section">
        <div class="collapse-header" @click="showAnswer = !showAnswer">
          <h3 class="section-title">参考答案与解析</h3>
          <el-icon :class="{ rotated: showAnswer }"><ArrowDown /></el-icon>
        </div>
        <div class="collapse-body" v-show="showAnswer">
          <div class="answer-block">
            <h4>标准答案</h4>
            <p>{{ question.text_detail?.standard_answer }}</p>
          </div>
          <div class="answer-block" v-if="question.text_detail?.explanation">
            <h4>详细解析</h4>
            <p>{{ question.text_detail.explanation }}</p>
          </div>
        </div>
      </div>

      <div class="divider"></div>

      <!-- 历史作答记录 -->
      <div class="section">
        <div class="collapse-header" @click="toggleHistory">
          <h3 class="section-title">历史作答记录 ({{ historyList.length }})</h3>
          <el-icon :class="{ rotated: showHistory }"><ArrowDown /></el-icon>
        </div>
        <div class="collapse-body" v-show="showHistory">
          <div v-if="historyList.length === 0" class="empty-hint">暂无作答记录</div>
          <div v-else class="history-list">
            <div v-for="item in historyList" :key="item.id" class="history-item">
              <div class="history-left">
                <span class="history-score" :class="item.score >= 60 ? 'high' : 'low'">{{ item.score }}分</span>
                <span class="history-method">{{ item.scoring_method === 'model' ? '内嵌模型' : 'DeepSeek' }}</span>
              </div>
              <span class="history-time">{{ formatTime(item.created_at) }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="divider"></div>

      <!-- 评论区 -->
      <CommentList :question-id="question.id" />
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getQuestionDetail } from '@/api/questions'
import { submitTextAnswer, getQuestionHistory } from '@/api/practice'
import { checkCollection, addCollection, removeCollection } from '@/api/collections'
import { DIFFICULTY_OPTIONS } from '@/utils/constants'
import { formatDateTime } from '@/utils/format'
import { ElMessage } from 'element-plus'
import CommentList from '@/components/comment/CommentList.vue'

const route = useRoute()
const loading = ref(false)
const question = ref(null)
const userAnswer = ref('')
const scoringMethod = ref('model')
const submitting = ref(false)
const scoreResult = ref(null)
const showAnswer = ref(false)
const showHistory = ref(false)
const historyList = ref([])
const isCollected = ref(false)

function difficultyLabel(val) {
  return DIFFICULTY_OPTIONS.find(d => d.value === val)?.label || val
}

function formatTime(val) {
  return formatDateTime(val)
}

const scoreClass = computed(() => {
  if (!scoreResult.value) return ''
  const s = parseFloat(scoreResult.value.score)
  if (s >= 80) return 'high'
  if (s >= 60) return 'mid'
  return 'low'
})

async function handleSubmit() {
  submitting.value = true
  try {
    const res = await submitTextAnswer({
      question_id: question.value.id,
      user_answer: userAnswer.value,
      scoring_method: scoringMethod.value,
      time_spent: 0,
    })
    scoreResult.value = res.data
    ElMessage.success('评分完成')
    fetchHistory()
  } catch (e) {}
  finally { submitting.value = false }
}

async function fetchHistory() {
  try {
    const res = await getQuestionHistory(route.params.id)
    historyList.value = res.data
  } catch (e) {}
}

function toggleHistory() {
  showHistory.value = !showHistory.value
  if (showHistory.value && historyList.value.length === 0) {
    fetchHistory()
  }
}

async function toggleCollect() {
  try {
    if (isCollected.value) {
      await removeCollection(question.value.id)
      isCollected.value = false
      ElMessage.success('已取消收藏')
    } else {
      await addCollection(question.value.id)
      isCollected.value = true
      ElMessage.success('收藏成功')
    }
  } catch (e) {}
}

async function fetchCollectionStatus() {
  try {
    const res = await checkCollection(route.params.id)
    isCollected.value = res.data.is_collected
  } catch (e) {}
}

onMounted(async () => {
  loading.value = true
  try {
    const res = await getQuestionDetail(route.params.id)
    question.value = res.data
    fetchCollectionStatus()
  } catch (e) {}
  finally { loading.value = false }
})
</script>

<style scoped>
.text-question-page {
  max-width: 800px;
  margin: 0 auto;
  min-height: 400px;
}

.question-header { margin-bottom: var(--spacing-lg); }

.question-title {
  font-size: 22px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--spacing-sm);
  line-height: 1.4;
}

.question-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.question-tags {
  display: flex;
  gap: var(--spacing-sm);
}

.cat-tag {
  font-size: 12px;
  color: var(--text-secondary);
  background: var(--color-info-bg);
  padding: 2px 10px;
  border-radius: var(--radius-sm);
}

.diff-tag { font-size: 12px; font-weight: 500; padding: 2px 10px; border-radius: var(--radius-sm); }
.diff-tag.easy { color: var(--color-easy); background: var(--color-easy-bg); }
.diff-tag.medium { color: var(--color-medium); background: var(--color-medium-bg); }
.diff-tag.hard { color: var(--color-hard); background: var(--color-hard-bg); }

.btn-collect {
  display: flex;
  align-items: center;
  gap: 4px;
  height: 32px;
  padding: 0 14px;
  background: #fff;
  color: var(--text-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  font-size: 13px;
  cursor: pointer;
  transition: all var(--transition-fast);
}
.btn-collect:hover { border-color: var(--color-medium); color: var(--color-medium); }
.btn-collect.collected { background: var(--color-medium-bg); color: var(--color-medium); border-color: var(--color-medium); }

.section { margin-bottom: var(--spacing-lg); }
.section-title { font-size: 16px; font-weight: 600; color: var(--text-primary); margin-bottom: var(--spacing-md); }
.content-text { font-size: 15px; color: var(--text-secondary); line-height: 1.7; }
.divider { height: 1px; background: var(--border-light); margin: var(--spacing-lg) 0; }

.submit-row { display: flex; align-items: center; justify-content: space-between; margin-top: var(--spacing-md); }
.scoring-select { display: flex; align-items: center; gap: var(--spacing-sm); }
.scoring-label { font-size: 13px; color: var(--text-tertiary); }

.btn-primary {
  height: 40px; padding: 0 24px; background: var(--btn-primary-bg); color: var(--btn-primary-text);
  border: none; border-radius: var(--radius-md); font-size: 14px; font-weight: 500; cursor: pointer;
  transition: background var(--transition-fast);
}
.btn-primary:hover { background: var(--btn-primary-hover); }
.btn-primary:disabled { background: #F2F3F5; color: #C9CDD4; cursor: not-allowed; }

.result-section { background: var(--bg-card); border: 1px solid var(--border-default); border-radius: var(--radius-lg); padding: var(--spacing-lg); }
.score-display { display: flex; align-items: baseline; gap: 4px; margin-bottom: var(--spacing-sm); }
.score-number { font-size: 36px; font-weight: 700; }
.score-number.high { color: var(--color-easy); }
.score-number.mid { color: var(--color-medium); }
.score-number.low { color: var(--color-hard); }
.score-unit { font-size: 14px; color: var(--text-tertiary); }
.score-feedback { font-size: 14px; color: var(--text-secondary); margin-bottom: var(--spacing-sm); }
.score-meta { display: flex; gap: var(--spacing-lg); font-size: 13px; color: var(--text-tertiary); }
.status-pass { color: var(--color-easy); font-weight: 500; }
.status-fail { color: var(--color-hard); font-weight: 500; }

.collapse-header { display: flex; align-items: center; justify-content: space-between; cursor: pointer; }
.collapse-header .el-icon { transition: transform var(--transition-base); color: var(--text-tertiary); }
.collapse-header .el-icon.rotated { transform: rotate(180deg); }
.collapse-body { margin-top: var(--spacing-md); }

.answer-block { margin-bottom: var(--spacing-md); }
.answer-block h4 { font-size: 14px; font-weight: 600; color: var(--text-primary); margin-bottom: var(--spacing-sm); }
.answer-block p { font-size: 14px; color: var(--text-secondary); line-height: 1.7; }

.empty-hint { font-size: 14px; color: var(--text-tertiary); text-align: center; padding: var(--spacing-lg); }

.history-list {
  display: flex; flex-direction: column; gap: 1px; background: var(--border-light);
  border: 1px solid var(--border-default); border-radius: var(--radius-md); overflow: hidden;
}
.history-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: var(--spacing-sm) var(--spacing-md); background: var(--bg-card);
}
.history-left { display: flex; align-items: center; gap: var(--spacing-md); }
.history-score { font-size: 15px; font-weight: 600; }
.history-score.high { color: var(--color-easy); }
.history-score.low { color: var(--color-hard); }
.history-method {
  font-size: 12px;
  color: var(--text-tertiary);
  background: var(--color-info-bg);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
}
.history-time {
  font-size: 12px;
  color: var(--text-tertiary);
}
</style>