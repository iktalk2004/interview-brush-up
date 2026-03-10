<template>
  <div class="admin-dashboard" v-loading="loading">
    <!-- 数据卡片 -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-icon user-icon"><el-icon :size="22"><User /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.total_users }}</span>
          <span class="stat-label">注册用户</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon question-icon"><el-icon :size="22"><Document /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.total_questions }}</span>
          <span class="stat-label">题目总数</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon text-icon"><el-icon :size="22"><EditPen /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.text_questions }}</span>
          <span class="stat-label">简答题</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon code-icon"><el-icon :size="22"><Monitor /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.code_questions }}</span>
          <span class="stat-label">代码题</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon submit-icon"><el-icon :size="22"><Finished /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.total_submissions }}</span>
          <span class="stat-label">总提交数</span>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-row">
      <div class="chart-card">
        <h4 class="chart-title">近14天提交趋势</h4>
        <div class="chart-container" ref="submissionChartRef"></div>
      </div>
      <div class="chart-card">
        <h4 class="chart-title">近14天新增用户</h4>
        <div class="chart-container" ref="userChartRef"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, onUnmounted } from 'vue'
import request from '@/api/index'
import * as echarts from 'echarts'

const loading = ref(false)
const submissionChartRef = ref(null)
const userChartRef = ref(null)
let submissionChart = null
let userChart = null

const stats = reactive({
  total_users: 0,
  total_questions: 0,
  total_submissions: 0,
  text_questions: 0,
  code_questions: 0,
  submission_trend: [],
  user_trend: [],
})

function renderLineChart(el, data, color) {
  if (!el) return null
  const chart = echarts.init(el)
  const dates = data.map(d => d.date.slice(5))
  const values = data.map(d => d.count)

  chart.setOption({
    grid: { top: 16, right: 16, bottom: 28, left: 40 },
    xAxis: {
      type: 'category',
      data: dates,
      axisLine: { lineStyle: { color: '#E5E6EB' } },
      axisLabel: { color: '#86909C', fontSize: 11 },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: '#86909C', fontSize: 11 },
      splitLine: { lineStyle: { color: '#F2F3F5' } },
    },
    series: [{
      type: 'line',
      data: values,
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: { color, width: 2 },
      itemStyle: { color },
      areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: color + '20' },
        { offset: 1, color: color + '02' },
      ])},
    }],
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#fff',
      borderColor: '#E5E6EB',
      textStyle: { color: '#1D2129', fontSize: 13 },
    },
  })
  return chart
}

onMounted(async () => {
  loading.value = true
  try {
    const res = await request.get('/admin/stats/overview')
    Object.assign(stats, res.data)
    await nextTick()
    submissionChart = renderLineChart(submissionChartRef.value, stats.submission_trend, '#1D2129')
    userChart = renderLineChart(userChartRef.value, stats.user_trend, '#00874C')
  } catch (e) {}
  finally { loading.value = false }
})

onUnmounted(() => {
  submissionChart?.dispose()
  userChart?.dispose()
})
</script>

<style scoped>
.stats-row {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.stat-card {
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  box-shadow: var(--shadow-card);
}

.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.user-icon { background: #E8F5EE; color: #00874C; }
.question-icon { background: #F2F3F5; color: #1D2129; }
.text-icon { background: #FFF3E0; color: #D4740C; }
.code-icon { background: #EDF4FF; color: #3370FF; }
.submit-icon { background: #FDEAEC; color: #CB2634; }

.stat-info { display: flex; flex-direction: column; gap: 2px; }
.stat-value { font-size: 22px; font-weight: 700; color: var(--text-primary); }
.stat-label { font-size: 12px; color: var(--text-tertiary); }

.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
}

.chart-card {
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-card);
}

.chart-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--spacing-md);
}

.chart-container {
  width: 100%;
  height: 260px;
}
</style>