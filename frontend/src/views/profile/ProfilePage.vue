<template>
  <div class="profile-page">
    <!-- 用户信息卡片 -->
    <div class="user-card">
      <el-avatar :size="64" :src="userStore.avatar" />
      <div class="user-info">
        <h2 class="user-name">{{ userStore.username }}</h2>
        <p class="user-meta">{{ userStore.userInfo?.email }}</p>
      </div>
      <button class="btn-secondary btn-sm" @click="$router.push('/profile/settings')">编辑资料</button>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid" v-loading="loading">
      <div class="stat-card">
        <span class="stat-value">{{ dashboard.total_questions }}</span>
        <span class="stat-label">刷题总数</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">{{ dashboard.accuracy }}%</span>
        <span class="stat-label">正确率</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">{{ formatDuration(dashboard.total_time) }}</span>
        <span class="stat-label">累计学习</span>
      </div>
      <div class="stat-card highlight">
        <span class="stat-value">{{ dashboard.today_count }}</span>
        <span class="stat-label">今日刷题</span>
      </div>
    </div>

    <!-- 分类掌握度 -->
    <div class="section-card" v-if="dashboard.category_stats && dashboard.category_stats.length">
      <h3 class="section-title">分类掌握度</h3>
      <div class="chart-container" ref="chartRef"></div>
    </div>

    <!-- 快捷入口 -->
    <div class="quick-links">
      <div class="link-card" @click="$router.push('/profile/history')">
        <el-icon :size="20"><Document /></el-icon>
        <span>刷题记录</span>
        <el-icon :size="14"><ArrowRight /></el-icon>
      </div>
      <div class="link-card" @click="$router.push('/profile/collections')">
        <el-icon :size="20"><Star /></el-icon>
        <span>我的收藏</span>
        <el-icon :size="14"><ArrowRight /></el-icon>
      </div>
      <div class="link-card" @click="$router.push('/mistakes')">
        <el-icon :size="20"><Warning /></el-icon>
        <span>错题本</span>
        <el-icon :size="14"><ArrowRight /></el-icon>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, watch } from 'vue'
import { useUserStore } from '@/stores/user'
import { getDashboard } from '@/api/stats'
import { formatDuration } from '@/utils/format'
import * as echarts from 'echarts'

const userStore = useUserStore()
const loading = ref(false)
const chartRef = ref(null)
let chartInstance = null

const dashboard = reactive({
  total_questions: 0,
  accuracy: 0,
  total_time: 0,
  today_count: 0,
  today_time: 0,
  category_stats: [],
})

function renderChart() {
  if (!chartRef.value || !dashboard.category_stats.length) return

  if (chartInstance) chartInstance.dispose()
  chartInstance = echarts.init(chartRef.value)

  const names = dashboard.category_stats.map(c => c.category_name)
  const values = dashboard.category_stats.map(c => c.mastery)

  chartInstance.setOption({
    radar: {
      indicator: names.map(n => ({ name: n, max: 100 })),
      shape: 'polygon',
      splitArea: { show: false },
      axisLine: { lineStyle: { color: '#E5E6EB' } },
      splitLine: { lineStyle: { color: '#F2F3F5' } },
      axisName: { color: '#4E5969', fontSize: 12 },
    },
    series: [{
      type: 'radar',
      data: [{
        value: values,
        areaStyle: { color: 'rgba(29, 33, 41, 0.06)' },
        lineStyle: { color: '#1D2129' },
        itemStyle: { color: '#1D2129' },
      }],
    }],
  })
}

onMounted(async () => {
  loading.value = true
  try {
    const res = await getDashboard()
    Object.assign(dashboard, res.data)
    await nextTick()
    renderChart()
  } catch (e) {}
  finally { loading.value = false }
})
</script>

<style scoped>
.profile-page { max-width: 800px; margin: 0 auto; }

.user-card {
  display: flex; align-items: center; gap: var(--spacing-lg);
  background: var(--bg-card); border: 1px solid var(--border-default); border-radius: var(--radius-lg);
  padding: var(--spacing-lg); margin-bottom: var(--spacing-lg); box-shadow: var(--shadow-card);
}
.user-info { flex: 1; }
.user-name { font-size: 20px; font-weight: 600; color: var(--text-primary); margin-bottom: 4px; }
.user-meta { font-size: 13px; color: var(--text-tertiary); }

.btn-secondary {
  height: 32px; padding: 0 14px; background: #fff; color: var(--text-primary);
  border: 1px solid var(--border-default); border-radius: var(--radius-md); font-size: 13px; cursor: pointer;
  transition: all var(--transition-fast);
}
.btn-secondary:hover { background: var(--bg-hover); }
.btn-sm { height: 32px; }

.stats-grid {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}
.stat-card {
  background: var(--bg-card); border: 1px solid var(--border-default); border-radius: var(--radius-lg);
  padding: var(--spacing-lg); text-align: center; display: flex; flex-direction: column;
  gap: var(--spacing-xs); box-shadow: var(--shadow-card);
}
.stat-card.highlight { border-color: var(--text-primary); }
.stat-value { font-size: 24px; font-weight: 700; color: var(--text-primary); }
.stat-label { font-size: 13px; color: var(--text-tertiary); }

.section-card {
  background: var(--bg-card); border: 1px solid var(--border-default); border-radius: var(--radius-lg);
  padding: var(--spacing-lg); margin-bottom: var(--spacing-lg); box-shadow: var(--shadow-card);
}
.section-title { font-size: 16px; font-weight: 600; color: var(--text-primary); margin-bottom: var(--spacing-md); }
.chart-container { width: 100%; height: 320px; }

.quick-links { display: flex; flex-direction: column; gap: 1px; background: var(--border-light);
  border: 1px solid var(--border-default); border-radius: var(--radius-lg); overflow: hidden; }
.link-card {
  display: flex; align-items: center; gap: var(--spacing-sm); padding: var(--spacing-md) var(--spacing-lg);
  background: var(--bg-card); cursor: pointer; transition: background var(--transition-fast);
  font-size: 14px; color: var(--text-primary);
}
.link-card:hover { background: var(--bg-hover); }
.link-card span { flex: 1; }
.link-card .el-icon:last-child { color: var(--text-placeholder); }
</style>