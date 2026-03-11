<template>
  <div class="history-page">
    <div class="page-header">
      <h2>刷题记录</h2>
      <div class="filter-group">
        <el-select v-model="filterStatus" placeholder="筛选结果" style="width: 120px" @change="handleFilterChange">
          <el-option label="全部" value="" />
          <el-option label="正确" value="true" />
          <el-option label="错误" value="false" />
        </el-select>
      </div>
    </div>

    <div v-loading="loading" class="content-wrapper">
      <el-table :data="records" style="width: 100%" stripe>
        <el-table-column prop="question_title" label="题目" min-width="200">
          <template #default="{ row }">
            <router-link :to="getQuestionLink(row)" class="question-link">
              {{ row.question_title }}
            </router-link>
          </template>
        </el-table-column>
        
        <el-table-column prop="is_correct" label="结果" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_correct ? 'success' : 'danger'" effect="dark">
              {{ row.is_correct ? '通过' : '未通过' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="score" label="得分" width="80" align="center">
          <template #default="{ row }">
            <span :class="getScoreClass(row.score)">{{ row.score }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="time_spent" label="耗时" width="120" align="center">
          <template #default="{ row }">
            {{ formatDuration(row.time_spent) }}
          </template>
        </el-table-column>

        <el-table-column prop="created_at" label="提交时间" width="180" align="center">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper" v-if="total > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
      
      <el-empty v-else description="暂无刷题记录" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getPracticeHistory } from '@/api/practice'
import { formatDateTime, formatDuration } from '@/utils/format'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const records = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const filterStatus = ref('')

const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
    }
    if (filterStatus.value) {
      params.is_correct = filterStatus.value
    }
    
    const res = await getPracticeHistory(params)
    const payload = res?.data || {}
    records.value = payload.results || []
    total.value = payload.count || 0
  } catch (error) {
    console.error('Failed to fetch history:', error)
    ElMessage.error('获取刷题记录失败')
  } finally {
    loading.value = false
  }
}

const handleFilterChange = () => {
  currentPage.value = 1
  fetchData()
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  fetchData()
}

const handlePageChange = (val) => {
  currentPage.value = val
  fetchData()
}

const getScoreClass = (score) => {
  if (score >= 90) return 'score-high'
  if (score >= 60) return 'score-pass'
  return 'score-fail'
}

const getQuestionLink = (row) => {
  if (row.question_type === 'code') {
    return `/question/code/${row.question_id}`
  }
  return `/question/text/${row.question_id}`
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.history-page {
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  min-height: 500px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  color: #333;
}

.question-link {
  color: var(--el-color-primary);
  text-decoration: none;
  font-weight: 500;
}

.question-link:hover {
  text-decoration: underline;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.score-high {
  color: #67c23a;
  font-weight: bold;
}

.score-pass {
  color: #e6a23c;
  font-weight: bold;
}

.score-fail {
  color: #f56c6c;
  font-weight: bold;
}
</style>
