<template>
  <div class="code-question-page" v-loading="loading">
    <template v-if="question">
      <div class="code-layout">
        <!-- 左侧：题目描述 -->
        <div class="left-panel">
          <h1 class="question-title">{{ question.title }}</h1>
          <div class="question-tags">
            <span class="cat-tag" v-if="question.category">{{ question.category.name }}</span>
            <span class="diff-tag" :class="question.difficulty">{{ difficultyLabel(question.difficulty) }}</span>
          </div>
          <div class="divider"></div>
          <div class="description">{{ question.code_detail?.description }}</div>

          <!-- 测试用例预览 -->
          <div class="test-preview" v-if="question.code_detail?.test_cases?.length">
            <h4>测试用例</h4>
            <div v-for="(tc, idx) in question.code_detail.test_cases.slice(0, 2)" :key="idx" class="tc-block">
              <div class="tc-row"><span class="tc-label">输入</span><pre>{{ tc.input }}</pre></div>
              <div class="tc-row"><span class="tc-label">输出</span><pre>{{ tc.output }}</pre></div>
            </div>
          </div>

          <!-- 判题历史 -->
          <div class="history-section">
            <div class="collapse-header" @click="toggleHistory">
              <h4>提交记录 ({{ historyList.length }})</h4>
              <el-icon :class="{ rotated: showHistory }"><ArrowDown /></el-icon>
            </div>
            <div class="history-list" v-show="showHistory">
              <div v-if="historyList.length === 0" class="empty-hint">暂无提交记录</div>
              <div v-for="item in historyList" :key="item.id" class="history-item">
                <span class="h-status" :class="item.status">{{ statusLabel(item.status) }}</span>
                <span class="h-lang">{{ item.language }}</span>
                <span class="h-pass">{{ item.passed_count }}/{{ item.total_count }}</span>
                <span class="h-time">{{ formatDateTime(item.created_at) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧：代码编辑器 -->
        <div class="right-panel">
          <div class="editor-toolbar">
            <el-select v-model="language" size="small" style="width: 130px" @change="loadTemplate">
              <el-option v-for="lang in LANGUAGE_OPTIONS" :key="lang.value" :label="lang.label" :value="lang.value" />
            </el-select>
            <div class="toolbar-actions">
              <button class="btn-primary btn-sm" @click="handleSubmit" :disabled="submitting || !code.trim()">
                {{ submitting ? '判题中...' : '提交代码' }}
              </button>
            </div>
          </div>

          <div class="editor-area">
            <el-input
              v-model="code"
              type="textarea"
              :rows="20"
              placeholder="在此编写你的代码..."
              resize="none"
              class="code-input"
            />
          </div>

          <!-- 判题结果 -->
          <div class="result-panel" v-if="result">
            <div class="result-header">
              <span class="result-status" :class="result.status">{{ statusLabel(result.status) }}</span>
              <span class="result-info">
                通过 {{ result.passed_count }}/{{ result.total_count }} 个测试用例
                <template v-if="result.time_used"> · {{ result.time_used }}ms</template>
                <template v-if="result.memory_used"> · {{ (result.memory_used / 1024).toFixed(1) }}MB</template>
              </span>
            </div>

            <!-- 错误信息 -->
            <div class="result-error" v-if="result.error_message">
              <pre>{{ result.error_message }}</pre>
            </div>

            <!-- 各用例详情 -->
            <div class="case-list" v-if="result.detail?.length">
              <div v-for="c in result.detail" :key="c.index" class="case-item" :class="{ passed: c.passed }">
                <span class="case-idx">#{{ c.index }}</span>
                <span class="case-status">{{ c.passed ? '✓' : '✗' }}</span>
                <span class="case-time" v-if="c.time">{{ c.time }}ms</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getQuestionDetail } from '@/api/questions'
import { submitCode, getJudgeHistory } from '@/api/judge'
import { DIFFICULTY_OPTIONS, LANGUAGE_OPTIONS } from '@/utils/constants'
import { formatDateTime } from '@/utils/format'
import { ElMessage } from 'element-plus'

const route = useRoute()
const loading = ref(false)
const question = ref(null)
const language = ref('python')
const code = ref('')
const submitting = ref(false)
const result = ref(null)
const showHistory = ref(false)
const historyList = ref([])

function difficultyLabel(val) {
  return DIFFICULTY_OPTIONS.find(d => d.value === val)?.label || val
}

const STATUS_MAP = {
  pending: '等待中', running: '运行中', accepted: '通过',
  wrong_answer: '答案错误', time_limit: '超时', memory_limit: '内存超限',
  runtime_error: '运行错误', compile_error: '编译错误', system_error: '系统错误',
}

function statusLabel(s) {
  return STATUS_MAP[s] || s
}

function loadTemplate() {
  const tpl = question.value?.code_detail?.code_template
  if (tpl && tpl[language.value]) {
    code.value = tpl[language.value]
  }
}

async function handleSubmit() {
  submitting.value = true
  result.value = null
  try {
    const res = await submitCode({
      question_id: question.value.id,
      language: language.value,
      source_code: code.value,
      time_spent: 0,
    })
    result.value = res.data
    if (res.data.status === 'accepted') {
      ElMessage.success('所有测试用例通过！')
    } else {
      ElMessage.warning(statusLabel(res.data.status))
    }
    fetchHistory()
  } catch (e) {
    console.error(e)
    ElMessage.error(e.response?.data?.message || e.message || '提交失败')
  }
  finally { submitting.value = false }
}

function toggleHistory() {
  showHistory.value = !showHistory.value
  if (showHistory.value && historyList.value.length === 0) {
    fetchHistory()
  }
}

async function fetchHistory() {
  try {
    const res = await getJudgeHistory(route.params.id)
    historyList.value = res.data
  } catch (e) {}
}

onMounted(async () => {
  loading.value = true
  try {
    const res = await getQuestionDetail(route.params.id)
    question.value = res.data
    loadTemplate()
  } catch (e) {}
  finally { loading.value = false }
})
</script>

<style scoped>
.code-question-page { min-height: 500px; }

.code-layout {
  display: flex; gap: 1px; background: var(--border-default);
  border: 1px solid var(--border-default); border-radius: var(--radius-lg);
  overflow: hidden; min-height: 650px;
}

.left-panel {
  width: 42%; background: var(--bg-card); padding: var(--spacing-lg);
  overflow-y: auto; max-height: 80vh;
}
.right-panel { flex: 1; background: var(--bg-card); display: flex; flex-direction: column; }

.question-title { font-size: 20px; font-weight: 600; color: var(--text-primary); margin-bottom: var(--spacing-sm); line-height: 1.4; }
.question-tags { display: flex; gap: var(--spacing-sm); }
.cat-tag { font-size: 12px; color: var(--text-secondary); background: var(--color-info-bg); padding: 2px 10px; border-radius: var(--radius-sm); }
.diff-tag { font-size: 12px; font-weight: 500; padding: 2px 10px; border-radius: var(--radius-sm); }
.diff-tag.easy { color: var(--color-easy); background: var(--color-easy-bg); }
.diff-tag.medium { color: var(--color-medium); background: var(--color-medium-bg); }
.diff-tag.hard { color: var(--color-hard); background: var(--color-hard-bg); }

.divider { height: 1px; background: var(--border-light); margin: var(--spacing-md) 0; }
.description { font-size: 14px; color: var(--text-secondary); line-height: 1.8; white-space: pre-wrap; }

.test-preview { margin-top: var(--spacing-lg); }
.test-preview h4 { font-size: 14px; font-weight: 600; color: var(--text-primary); margin-bottom: var(--spacing-sm); }
.tc-block { background: var(--bg-page); border-radius: var(--radius-sm); padding: var(--spacing-sm); margin-bottom: var(--spacing-sm); }
.tc-row { display: flex; gap: var(--spacing-sm); align-items: flex-start; margin-bottom: 4px; }
.tc-label { font-size: 12px; color: var(--text-tertiary); min-width: 32px; padding-top: 2px; }
.tc-block pre { font-size: 13px; font-family: 'Consolas', monospace; color: var(--text-primary); margin: 0; white-space: pre-wrap; }

.history-section { margin-top: var(--spacing-lg); border-top: 1px solid var(--border-light); padding-top: var(--spacing-md); }
.collapse-header { display: flex; align-items: center; justify-content: space-between; cursor: pointer; }
.collapse-header h4 { font-size: 14px; font-weight: 600; color: var(--text-primary); }
.collapse-header .el-icon { transition: transform var(--transition-base); color: var(--text-tertiary); }
.collapse-header .el-icon.rotated { transform: rotate(180deg); }

.history-list { margin-top: var(--spacing-sm); }
.empty-hint { font-size: 13px; color: var(--text-tertiary); text-align: center; padding: var(--spacing-md); }
.history-item {
  display: flex; align-items: center; gap: var(--spacing-md); padding: var(--spacing-xs) 0;
  font-size: 13px; border-bottom: 1px solid var(--border-light);
}
.h-status { font-weight: 500; min-width: 60px; }
.h-status.accepted { color: var(--color-easy); }
.h-status.wrong_answer, .h-status.runtime_error, .h-status.compile_error { color: var(--color-hard); }
.h-status.time_limit, .h-status.memory_limit { color: var(--color-medium); }
.h-lang { color: var(--text-tertiary); }
.h-pass { color: var(--text-secondary); }
.h-time { color: var(--text-placeholder); font-size: 12px; margin-left: auto; }

.editor-toolbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: var(--spacing-sm) var(--spacing-md); border-bottom: 1px solid var(--border-light);
}
.toolbar-actions { display: flex; gap: var(--spacing-sm); }

.editor-area { flex: 1; }
.code-input :deep(.el-textarea__inner) {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px; line-height: 1.6; border: none; border-radius: 0;
  resize: none; height: 100%; background: #FAFBFC;
}

.result-panel { border-top: 1px solid var(--border-light); padding: var(--spacing-md); max-height: 240px; overflow-y: auto; }
.result-header { display: flex; align-items: center; gap: var(--spacing-md); margin-bottom: var(--spacing-sm); }
.result-status { font-size: 15px; font-weight: 600; padding: 4px 14px; border-radius: var(--radius-sm); }
.result-status.accepted { color: var(--color-easy); background: var(--color-easy-bg); }
.result-status.wrong_answer { color: var(--color-hard); background: var(--color-hard-bg); }
.result-status.runtime_error, .result-status.compile_error { color: var(--color-hard); background: var(--color-hard-bg); }
.result-status.time_limit, .result-status.memory_limit { color: var(--color-medium); background: var(--color-medium-bg); }
.result-status.system_error { color: var(--text-tertiary); background: var(--color-info-bg); }
.result-info { font-size: 13px; color: var(--text-secondary); }

.result-error { margin-bottom: var(--spacing-sm); }
.result-error pre {
  font-size: 12px; font-family: 'Consolas', monospace; color: var(--color-hard);
  background: var(--color-hard-bg); padding: var(--spacing-sm); border-radius: var(--radius-sm);
  white-space: pre-wrap; word-break: break-all; max-height: 120px; overflow-y: auto;
}

.case-list { display: flex; flex-wrap: wrap; gap: var(--spacing-xs); }
.case-item {
  display: flex; align-items: center; gap: 4px; padding: 4px 10px;
  background: var(--color-hard-bg); border-radius: var(--radius-sm); font-size: 12px; color: var(--color-hard);
}
.case-item.passed { background: var(--color-easy-bg); color: var(--color-easy); }
.case-idx { font-weight: 500; }
.case-time { color: var(--text-tertiary); }

.btn-primary {
  height: 32px; padding: 0 16px; background: var(--btn-primary-bg); color: var(--btn-primary-text);
  border: none; border-radius: var(--radius-md); font-size: 13px; font-weight: 500; cursor: pointer;
  transition: background var(--transition-fast);
}
.btn-primary:hover { background: var(--btn-primary-hover); }
.btn-primary:disabled { background: #F2F3F5; color: #C9CDD4; cursor: not-allowed; }
.btn-sm { height: 32px; }
</style>