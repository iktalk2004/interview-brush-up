<template>
  <div class="recommend-compare">
    <div class="page-header">
      <h3>推荐算法对比</h3>
      <div class="header-actions">
        <button class="btn-secondary btn-sm" :disabled="triggering" @click="handleTrigger">
          {{ triggering ? '计算中...' : '重新计算相似度' }}
        </button>
        <button class="btn-primary btn-sm" :disabled="loading" @click="fetchCompare">
          {{ loading ? '评估中...' : '运行评估' }}
        </button>
      </div>
    </div>

    <div class="compare-content" v-loading="loading">
      <div v-if="!results" class="empty-state">点击"运行评估"查看各算法效果对比</div>

      <template v-if="results">
        <!-- 指标表格 -->
        <div class="table-wrap">
          <table class="data-table">
            <thead>
              <tr><th>算法</th><th>Hit Rate</th><th>Precision</th><th>Recall</th><th>F1</th><th>Coverage</th><th>有效用户</th></tr>
            </thead>
            <tbody>
              <tr v-for="(metrics, name) in results" :key="name">
                <td class="algo-name">{{ name }}</td>
                <td class="highlight-cell">{{ (metrics.hit_rate * 100).toFixed(1) }}%</td>
                <td>{{ metrics.precision }}</td>
                <td>{{ metrics.recall }}</td>
                <td class="f1-cell">{{ metrics.f1 }}</td>
                <td>{{ metrics.coverage }}%</td>
                <td>{{ metrics.valid_users }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 图表 -->
        <div class="chart-card">
          <h4 class="chart-title">算法指标对比</h4>
          <div class="chart-container" ref="chartRef"></div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onUnmounted } from 'vue'
import { getAlgorithmCompare, triggerSimilarity } from '@/api/recommend'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const loading = ref(false)
const triggering = ref(false)
const results = ref(null)
const chartRef = ref(null)
let chartInstance = null

async function handleTrigger() {
  triggering.value = true
  try {
    const res = await triggerSimilarity()
    ElMessage.success(res.message || '相似度计算完成')
  } catch (e) {}
  finally { triggering.value = false }
}

async function fetchCompare() {
  loading.value = true
  try {
    const res = await getAlgorithmCompare()
    results.value = res.data
    await nextTick()
    renderChart()
  } catch (e) {}
  finally { loading.value = false }
}

function renderChart() {
  if (!chartRef.value || !results.value) return
  if (chartInstance) chartInstance.dispose()
  chartInstance = echarts.init(chartRef.value)

  const names = Object.keys(results.value)
  const metrics = ['hit_rate', 'precision', 'recall', 'f1']
  const colors = ['#3370FF', '#1D2129', '#00874C', '#D4740C']

  chartInstance.setOption({
    legend: { data: ['Hit Rate', 'Precision', 'Recall', 'F1'], bottom: 0, textStyle: { fontSize: 12, color: '#4E5969' } },
    grid: { top: 16, right: 16, bottom: 40, left: 48 },
    xAxis: {
      type: 'category', data: names,
      axisLine: { lineStyle: { color: '#E5E6EB' } },
      axisLabel: { color: '#4E5969', fontSize: 12 },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value', max: 1,
      axisLine: { show: false }, axisTick: { show: false },
      axisLabel: { color: '#86909C', fontSize: 11 },
      splitLine: { lineStyle: { color: '#F2F3F5' } },
    },
    series: metrics.map((m, i) => ({
      name: m === 'hit_rate' ? 'Hit Rate' : m.charAt(0).toUpperCase() + m.slice(1),
      type: 'bar',
      data: names.map(n => results.value[n][m]),
      barWidth: 20,
      itemStyle: { color: colors[i], borderRadius: [4, 4, 0, 0] },
    })),
    tooltip: { trigger: 'axis', backgroundColor: '#fff', borderColor: '#E5E6EB', textStyle: { color: '#1D2129', fontSize: 13 } },
  })
}

onUnmounted(() => { chartInstance?.dispose() })
</script>

<style scoped>
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--spacing-lg); }
.page-header h3 { font-size: 16px; font-weight: 600; color: var(--text-primary); }
.header-actions { display: flex; gap: var(--spacing-sm); }

.compare-content { min-height: 300px; }
.empty-state { text-align: center; color: var(--text-tertiary); padding: var(--spacing-xxl); }

.table-wrap {
  background: var(--bg-card); border: 1px solid var(--border-default); border-radius: var(--radius-lg);
  overflow: hidden; box-shadow: var(--shadow-card); margin-bottom: var(--spacing-lg);
}
.data-table { width: 100%; border-collapse: collapse; }
.data-table th {
  text-align: left; padding: var(--spacing-sm) var(--spacing-md);
  font-size: 13px; font-weight: 500; color: var(--text-secondary); background: var(--bg-table-header);
  border-bottom: 1px solid var(--border-default);
}
.data-table td {
  padding: var(--spacing-sm) var(--spacing-md); font-size: 14px; color: var(--text-primary);
  border-bottom: 1px solid var(--border-light);
}
.algo-name { font-weight: 500; }
.f1-cell { font-weight: 600; color: var(--color-easy); }

.chart-card {
  background: var(--bg-card); border: 1px solid var(--border-default); border-radius: var(--radius-lg);
  padding: var(--spacing-lg); box-shadow: var(--shadow-card);
}
.chart-title { font-size: 14px; font-weight: 600; color: var(--text-primary); margin-bottom: var(--spacing-md); }
.chart-container { width: 100%; height: 320px; }

.btn-primary {
  height: 32px; padding: 0 16px; background: var(--btn-primary-bg); color: var(--btn-primary-text);
  border: none; border-radius: var(--radius-md); font-size: 13px; font-weight: 500; cursor: pointer;
}
.btn-primary:hover { background: var(--btn-primary-hover); }
.btn-primary:disabled { background: #F2F3F5; color: #C9CDD4; cursor: not-allowed; }
.btn-secondary {
  height: 32px; padding: 0 16px; background: #fff; color: var(--text-primary);
  border: 1px solid var(--border-default); border-radius: var(--radius-md); font-size: 13px; cursor: pointer;
}
.btn-secondary:hover { background: var(--bg-hover); }
.btn-secondary:disabled { color: #C9CDD4; cursor: not-allowed; }
.btn-sm { height: 32px; }

.highlight-cell { font-weight: 600; color: var(--color-easy); }
</style>