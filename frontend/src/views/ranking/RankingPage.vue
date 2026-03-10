<template>
  <div class="ranking-page">
    <h2 class="page-title">排行榜</h2>

    <!-- 切换栏 -->
    <div class="filter-row">
      <div class="tab-group">
        <span
          v-for="p in RANKING_PERIOD_OPTIONS"
          :key="p.value"
          class="tab-item"
          :class="{ active: period === p.value }"
          @click="period = p.value; fetchRanking()"
        >{{ p.label }}</span>
      </div>
      <div class="tab-group">
        <span class="tab-item" :class="{ active: metric === 'count' }" @click="metric = 'count'; fetchRanking()">按刷题数</span>
        <span class="tab-item" :class="{ active: metric === 'accuracy' }" @click="metric = 'accuracy'; fetchRanking()">按正确率</span>
      </div>
    </div>

    <!-- 排行榜表格 -->
    <div class="ranking-list" v-loading="loading">
      <div v-if="list.length === 0 && !loading" class="empty-state">
        <p>暂无排行数据</p>
      </div>

      <div v-for="item in list" :key="item.user_id" class="rank-item" :class="{ 'top-three': item.rank <= 3 }">
        <div class="rank-left">
          <span class="rank-num" :class="`rank-${item.rank}`">
            {{ item.rank <= 3 ? ['🥇', '🥈', '🥉'][item.rank - 1] : item.rank }}
          </span>
          <el-avatar :size="36" :src="item.avatar || '/default-avatar.png'" />
          <span class="rank-username">{{ item.username }}</span>
        </div>
        <div class="rank-right">
          <div class="rank-stat">
            <span class="rank-value">{{ item.total_questions }}</span>
            <span class="rank-label">题目数</span>
          </div>
          <div class="rank-stat">
            <span class="rank-value">{{ item.accuracy }}%</span>
            <span class="rank-label">正确率</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getRanking } from '@/api/stats'
import { RANKING_PERIOD_OPTIONS } from '@/utils/constants'

const loading = ref(false)
const list = ref([])
const period = ref('all')
const metric = ref('count')

async function fetchRanking() {
  loading.value = true
  try {
    const res = await getRanking({ period: period.value, metric: metric.value, page_size: 50 })
    list.value = res.data.results
  } catch (e) {}
  finally { loading.value = false }
}

onMounted(fetchRanking)
</script>

<style scoped>
.ranking-page { max-width: 800px; margin: 0 auto; }
.page-title { font-size: 20px; font-weight: 600; color: var(--text-primary); margin-bottom: var(--spacing-lg); }

.filter-row {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: var(--spacing-lg);
}
.tab-group { display: flex; gap: 4px; background: var(--bg-sidebar); border-radius: var(--radius-md); padding: 3px; }
.tab-item {
  padding: 6px 16px; border-radius: var(--radius-sm); font-size: 13px;
  color: var(--text-secondary); cursor: pointer; transition: all var(--transition-fast);
}
.tab-item:hover { color: var(--text-primary); }
.tab-item.active { background: var(--bg-card); color: var(--text-primary); font-weight: 500; box-shadow: var(--shadow-card); }

.ranking-list {
  border: 1px solid var(--border-default); border-radius: var(--radius-lg); overflow: hidden;
  background: var(--border-light); display: flex; flex-direction: column; gap: 1px; min-height: 200px;
}
.empty-state { padding: var(--spacing-xxl); text-align: center; color: var(--text-tertiary); background: var(--bg-card); }

.rank-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: var(--spacing-sm) var(--spacing-lg); background: var(--bg-card);
  transition: background var(--transition-fast);
}
.rank-item:hover { background: var(--bg-hover); }
.rank-item.top-three { background: var(--bg-hover); }

.rank-left { display: flex; align-items: center; gap: var(--spacing-md); }
.rank-num {
  width: 32px; text-align: center; font-size: 14px; font-weight: 600; color: var(--text-tertiary);
}
.rank-num.rank-1, .rank-num.rank-2, .rank-num.rank-3 { font-size: 20px; }
.rank-username { font-size: 14px; font-weight: 500; color: var(--text-primary); }

.rank-right { display: flex; gap: var(--spacing-xl); }
.rank-stat { display: flex; flex-direction: column; align-items: center; gap: 2px; }
.rank-value { font-size: 15px; font-weight: 600; color: var(--text-primary); }
.rank-label { font-size: 11px; color: var(--text-tertiary); }
</style>