<template>
  <div class="home-page">
    <div class="welcome-section">
      <h1 class="welcome-title">八股文刷题系统</h1>
      <p class="welcome-desc">高效备战技术面试，个性化推荐助你查漏补缺</p>
      <div class="welcome-actions">
        <button class="btn-primary btn-lg" @click="$router.push('/questions')">开始刷题</button>
        <button class="btn-secondary btn-lg" @click="$router.push('/daily')">每日推荐</button>
      </div>
    </div>

    <!-- 推荐题目 -->
    <div class="section" v-if="userStore.isLoggedIn">
      <div class="section-header">
        <h2 class="section-title">为你推荐</h2>
        <span class="section-link" @click="$router.push('/questions')">查看更多 →</span>
      </div>
      <div class="recommend-grid" v-loading="recLoading">
        <div v-if="recommendations.length === 0 && !recLoading" class="empty-hint">暂无推荐，先去刷几道题吧</div>
        <div
          v-for="item in recommendations"
          :key="item.id"
          class="rec-card"
          @click="goDetail(item)"
        >
          <h4 class="rec-title">{{ item.title }}</h4>
          <div class="rec-meta">
            <span class="rec-cat" v-if="item.category">{{ item.category.name }}</span>
            <span class="rec-diff" :class="item.difficulty">{{ diffLabel(item.difficulty) }}</span>
            <span class="rec-type">{{ item.question_type === 'text' ? '简答' : '代码' }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 公告 -->
    <div class="section" v-if="announcements.length">
      <h2 class="section-title">最新公告</h2>
      <div class="announcement-list">
        <div v-for="item in announcements" :key="item.id" class="announcement-item" @click="expandedId = expandedId === item.id ? null : item.id">
          <div class="ann-header">
            <h4 class="ann-title">{{ item.title }}</h4>
            <span class="ann-time">{{ formatDateTime(item.created_at) }}</span>
          </div>
          <p class="ann-content" v-show="expandedId === item.id">{{ item.content }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getHomeRecommend } from '@/api/recommend'
import { getAnnouncements } from '@/api/announcements'
import { DIFFICULTY_OPTIONS } from '@/utils/constants'
import { formatDateTime } from '@/utils/format'

const router = useRouter()
const userStore = useUserStore()
const recommendations = ref([])
const recLoading = ref(false)
const announcements = ref([])
const expandedId = ref(null)

function diffLabel(val) {
  return DIFFICULTY_OPTIONS.find(d => d.value === val)?.label || val
}

function goDetail(item) {
  router.push(item.question_type === 'text' ? `/question/text/${item.id}` : `/question/code/${item.id}`)
}

onMounted(async () => {
  // 加载公告
  try {
    const res = await getAnnouncements({ page_size: 5 })
    announcements.value = res.data.results
  } catch (e) {}

  // 加载推荐
  if (userStore.isLoggedIn) {
    recLoading.value = true
    try {
      const res = await getHomeRecommend()
      recommendations.value = res.data
    } catch (e) {}
    finally { recLoading.value = false }
  }
})
</script>

<style scoped>
.home-page { max-width: 900px; margin: 0 auto; }

.welcome-section { text-align: center; padding: var(--spacing-xxl) 0 var(--spacing-xl); }
.welcome-title { font-size: 32px; font-weight: 700; color: var(--text-primary); margin-bottom: var(--spacing-sm); }
.welcome-desc { font-size: 16px; color: var(--text-secondary); margin-bottom: var(--spacing-xl); }
.welcome-actions { display: flex; justify-content: center; gap: var(--spacing-md); }

.btn-primary {
  background: var(--btn-primary-bg); color: var(--btn-primary-text);
  border: none; border-radius: var(--radius-md); font-size: 15px; font-weight: 500; cursor: pointer;
  transition: background var(--transition-fast);
}
.btn-primary:hover { background: var(--btn-primary-hover); }
.btn-secondary {
  background: #fff; color: var(--text-primary);
  border: 1px solid var(--border-default); border-radius: var(--radius-md); font-size: 15px; font-weight: 500; cursor: pointer;
}
.btn-secondary:hover { background: var(--bg-hover); }
.btn-lg { height: 48px; padding: 0 32px; }

.section { margin-bottom: var(--spacing-xl); }
.section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--spacing-md); }
.section-title { font-size: 18px; font-weight: 600; color: var(--text-primary); }
.section-link { font-size: 13px; color: var(--text-tertiary); cursor: pointer; }
.section-link:hover { color: var(--text-primary); }

.recommend-grid {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--spacing-md); min-height: 100px;
}
.empty-hint { grid-column: 1 / -1; text-align: center; color: var(--text-tertiary); font-size: 14px; padding: var(--spacing-lg); }

.rec-card {
  background: var(--bg-card); border: 1px solid var(--border-default); border-radius: var(--radius-lg);
  padding: var(--spacing-lg); cursor: pointer; transition: all var(--transition-base);
  box-shadow: var(--shadow-card);
}
.rec-card:hover { box-shadow: var(--shadow-card-hover); }

.rec-title {
  font-size: 15px; font-weight: 500; color: var(--text-primary); margin-bottom: var(--spacing-sm);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.rec-meta { display: flex; align-items: center; gap: var(--spacing-sm); flex-wrap: wrap; }
.rec-cat { font-size: 12px; color: var(--text-secondary); background: var(--color-info-bg); padding: 2px 8px; border-radius: var(--radius-sm); }
.rec-diff { font-size: 12px; font-weight: 500; padding: 2px 8px; border-radius: var(--radius-sm); }
.rec-diff.easy { color: var(--color-easy); background: var(--color-easy-bg); }
.rec-diff.medium { color: var(--color-medium); background: var(--color-medium-bg); }
.rec-diff.hard { color: var(--color-hard); background: var(--color-hard-bg); }
.rec-type { font-size: 11px; color: var(--text-tertiary); }

.announcement-list {
  border: 1px solid var(--border-default); border-radius: var(--radius-lg);
  overflow: hidden; background: var(--border-light); display: flex; flex-direction: column; gap: 1px;
}
.announcement-item {
  padding: var(--spacing-md) var(--spacing-lg); background: var(--bg-card);
  cursor: pointer; transition: background var(--transition-fast);
}
.announcement-item:hover { background: var(--bg-hover); }
.ann-header { display: flex; align-items: center; justify-content: space-between; }
.ann-title { font-size: 15px; font-weight: 500; color: var(--text-primary); }
.ann-time { font-size: 12px; color: var(--text-tertiary); }
.ann-content {
  font-size: 14px; color: var(--text-secondary); line-height: 1.7;
  margin-top: var(--spacing-sm); padding-top: var(--spacing-sm); border-top: 1px solid var(--border-light);
}
</style>