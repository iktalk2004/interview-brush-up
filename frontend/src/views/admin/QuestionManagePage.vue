<template>
  <div class="question-manage">
    <div class="page-header">
      <h3>题目管理</h3>
      <div class="header-actions">
        <el-input v-model="search" placeholder="搜索题目" clearable style="width: 220px" @keyup.enter="fetchList" @clear="fetchList">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <button class="btn-secondary btn-sm" @click="$router.push('/admin/categories')">管理分类</button>
        <button class="btn-primary btn-sm" @click="openCreate">新增题目</button>
      </div>
    </div>

    <!-- 筛选 -->
    <div class="filter-row">
      <el-select v-model="filters.category" placeholder="分类" clearable style="width: 140px" @change="fetchList">
        <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
      </el-select>
      <el-select v-model="filters.difficulty" placeholder="难度" clearable style="width: 120px" @change="fetchList">
        <el-option v-for="d in DIFFICULTY_OPTIONS" :key="d.value" :label="d.label" :value="d.value" />
      </el-select>
      <el-select v-model="filters.question_type" placeholder="题型" clearable style="width: 120px" @change="fetchList">
        <el-option v-for="t in QUESTION_TYPE_OPTIONS" :key="t.value" :label="t.label" :value="t.value" />
      </el-select>
    </div>

    <!-- 表格 -->
    <div class="table-wrap" v-loading="loading">
      <table class="data-table">
        <thead>
          <tr><th>ID</th><th>标题</th><th>分类</th><th>题型</th><th>难度</th><th>创建时间</th><th>操作</th></tr>
        </thead>
        <tbody>
          <tr v-if="list.length === 0 && !loading"><td colspan="7" class="empty-cell">暂无数据</td></tr>
          <tr v-for="item in list" :key="item.id">
            <td>{{ item.id }}</td>
            <td class="title-cell">{{ item.title }}</td>
            <td>{{ item.category?.name || '-' }}</td>
            <td>{{ item.question_type === 'text' ? '简答题' : '代码题' }}</td>
            <td><span class="diff-tag" :class="item.difficulty">{{ diffLabel(item.difficulty) }}</span></td>
            <td>{{ formatDateTime(item.created_at) }}</td>
            <td class="action-cell">
              <button class="btn-text" @click="openDetail(item.id)">查看</button>
              <button class="btn-text" @click="openEdit(item.id)">编辑</button>
              <button class="btn-text danger" @click="handleDelete(item.id)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="pagination-wrap" v-if="total > pageSize">
      <el-pagination v-model:current-page="page" :page-size="pageSize" :total="total" layout="prev, pager, next" @current-change="fetchList" />
    </div>

    <!-- 查看详情弹窗 -->
    <el-dialog v-model="detailVisible" title="题目详情" width="700px">
      <div v-if="detailData" class="detail-content">
        <div class="detail-row"><span class="detail-label">标题</span><span>{{ detailData.title }}</span></div>
        <div class="detail-row"><span class="detail-label">类型</span><span>{{ detailData.question_type === 'text' ? '简答题' : '代码题' }}</span></div>
        <div class="detail-row"><span class="detail-label">分类</span><span>{{ detailData.category?.name }} {{ detailData.sub_category ? '/ ' + detailData.sub_category.name : '' }}</span></div>
        <div class="detail-row"><span class="detail-label">难度</span><span class="diff-tag" :class="detailData.difficulty">{{ diffLabel(detailData.difficulty) }}</span></div>
        <template v-if="detailData.question_type === 'text' && detailData.text_detail">
          <div class="detail-row" v-if="detailData.text_detail.content"><span class="detail-label">题干</span><span class="detail-text">{{ detailData.text_detail.content }}</span></div>
          <div class="detail-row"><span class="detail-label">标准答案</span><span class="detail-text">{{ detailData.text_detail.standard_answer }}</span></div>
          <div class="detail-row" v-if="detailData.text_detail.explanation"><span class="detail-label">解析</span><span class="detail-text">{{ detailData.text_detail.explanation }}</span></div>
        </template>
        <template v-if="detailData.question_type === 'code' && detailData.code_detail">
          <div class="detail-row"><span class="detail-label">描述</span><span class="detail-text">{{ detailData.code_detail.description }}</span></div>
          <div class="detail-row"><span class="detail-label">测试用例数</span><span>{{ detailData.code_detail.test_cases?.length || 0 }}</span></div>
          <div class="detail-row"><span class="detail-label">时间限制</span><span>{{ detailData.code_detail.time_limit }}ms</span></div>
          <div class="detail-row"><span class="detail-label">内存限制</span><span>{{ detailData.code_detail.memory_limit }}MB</span></div>
        </template>
      </div>
    </el-dialog>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="formVisible" :title="editId ? '编辑题目' : '新增题目'" width="720px" :close-on-click-modal="false">
      <el-form ref="formRef" :model="form" :rules="formRules" label-position="top">
        <el-form-item label="题目类型" prop="question_type">
          <el-radio-group v-model="form.question_type" :disabled="!!editId">
            <el-radio value="text">简答题</el-radio>
            <el-radio value="code">代码题</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入题目标题" />
        </el-form-item>

        <div class="form-inline">
          <el-form-item label="一级分类" prop="category_id" style="flex:1">
            <el-select v-model="form.category_id" placeholder="选择分类" style="width:100%" @change="onCategoryChange">
              <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="二级分类" style="flex:1">
            <el-select v-model="form.sub_category_id" placeholder="选择子分类（选填）" clearable style="width:100%">
              <el-option v-for="s in subCategories" :key="s.id" :label="s.name" :value="s.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="难度" prop="difficulty" style="flex:0.6">
            <el-select v-model="form.difficulty" style="width:100%">
              <el-option v-for="d in DIFFICULTY_OPTIONS" :key="d.value" :label="d.label" :value="d.value" />
            </el-select>
          </el-form-item>
        </div>

        <!-- 简答题字段 -->
        <template v-if="form.question_type === 'text'">
          <el-form-item label="题干补充">
            <el-input v-model="form.content" type="textarea" :rows="3" placeholder="选填，可为空" />
          </el-form-item>
          <el-form-item label="标准答案" prop="standard_answer">
            <el-input v-model="form.standard_answer" type="textarea" :rows="4" placeholder="请输入标准答案" />
          </el-form-item>
          <el-form-item label="详细解析">
            <el-input v-model="form.explanation" type="textarea" :rows="3" placeholder="选填" />
          </el-form-item>
        </template>

        <!-- 代码题字段 -->
        <template v-if="form.question_type === 'code'">
          <el-form-item label="题目描述" prop="description">
            <el-input v-model="form.description" type="textarea" :rows="4" placeholder="请输入题目描述" />
          </el-form-item>
          <el-form-item label="参考代码">
            <el-input v-model="form.reference_code" type="textarea" :rows="4" placeholder="选填" />
          </el-form-item>
          <div class="form-inline">
            <el-form-item label="时间限制(ms)" style="flex:1">
              <el-input-number v-model="form.time_limit" :min="100" :max="10000" />
            </el-form-item>
            <el-form-item label="内存限制(MB)" style="flex:1">
              <el-input-number v-model="form.memory_limit" :min="16" :max="1024" />
            </el-form-item>
          </div>
          <!-- 测试用例 -->
          <el-form-item label="测试用例">
            <div class="test-cases">
              <div v-for="(tc, idx) in form.test_cases" :key="idx" class="test-case-item">
                <div class="tc-fields">
                  <el-input v-model="tc.input" type="textarea" :rows="2" placeholder="输入" />
                  <el-input v-model="tc.output" type="textarea" :rows="2" placeholder="期望输出" />
                </div>
                <button class="btn-text danger" @click="form.test_cases.splice(idx, 1)">删除</button>
              </div>
              <button class="btn-secondary btn-sm" @click="form.test_cases.push({ input: '', output: '' })">+ 添加测试用例</button>
            </div>
          </el-form-item>
        </template>
      </el-form>

      <template #footer>
        <button class="btn-secondary" @click="formVisible = false">取消</button>
        <button class="btn-primary" :disabled="submitting" @click="handleSubmitForm" style="margin-left: 12px">
          {{ submitting ? '保存中...' : '保存' }}
        </button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import {
  getAdminQuestions, getAdminQuestionDetail, createQuestion, updateQuestion,
  deleteQuestion, getAdminCategories,
} from '@/api/admin'
import { DIFFICULTY_OPTIONS, QUESTION_TYPE_OPTIONS } from '@/utils/constants'
import { formatDateTime } from '@/utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const list = ref([])
const categories = ref([])
const search = ref('')
const page = ref(1)
const pageSize = 20
const total = ref(0)
const filters = reactive({ category: null, difficulty: null, question_type: null })

// 详情弹窗
const detailVisible = ref(false)
const detailData = ref(null)

// 新增/编辑弹窗
const formVisible = ref(false)
const editId = ref(null)
const formRef = ref(null)
const submitting = ref(false)

const form = reactive({
  question_type: 'text',
  title: '',
  category_id: null,
  sub_category_id: null,
  difficulty: 'medium',
  // 简答题
  content: '',
  standard_answer: '',
  explanation: '',
  // 代码题
  description: '',
  reference_code: '',
  test_cases: [{ input: '', output: '' }],
  time_limit: 1000,
  memory_limit: 256,
})

const formRules = {
  question_type: [{ required: true, message: '请选择题目类型', trigger: 'change' }],
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  category_id: [{ required: true, message: '请选择分类', trigger: 'change' }],
  difficulty: [{ required: true, message: '请选择难度', trigger: 'change' }],
  standard_answer: [{ required: true, message: '请输入标准答案', trigger: 'blur' }],
  description: [{ required: true, message: '请输入题目描述', trigger: 'blur' }],
}

const subCategories = computed(() => {
  if (!form.category_id) return []
  const cat = categories.value.find(c => c.id === form.category_id)
  return cat?.sub_categories || []
})

function diffLabel(val) { return DIFFICULTY_OPTIONS.find(d => d.value === val)?.label || val }

function onCategoryChange() { form.sub_category_id = null }

function resetForm() {
  editId.value = null
  form.question_type = 'text'
  form.title = ''
  form.category_id = null
  form.sub_category_id = null
  form.difficulty = 'medium'
  form.content = ''
  form.standard_answer = ''
  form.explanation = ''
  form.description = ''
  form.reference_code = ''
  form.test_cases = [{ input: '', output: '' }]
  form.time_limit = 1000
  form.memory_limit = 256
}

function openCreate() {
  resetForm()
  formVisible.value = true
}

async function openDetail(id) {
  try {
    const res = await getAdminQuestionDetail(id)
    detailData.value = res.data
    detailVisible.value = true
  } catch (e) {}
}

async function openEdit(id) {
  try {
    const res = await getAdminQuestionDetail(id)
    const d = res.data
    editId.value = d.id
    form.question_type = d.question_type
    form.title = d.title
    form.category_id = d.category?.id || null
    form.sub_category_id = d.sub_category?.id || null
    form.difficulty = d.difficulty

    if (d.question_type === 'text' && d.text_detail) {
      form.content = d.text_detail.content || ''
      form.standard_answer = d.text_detail.standard_answer || ''
      form.explanation = d.text_detail.explanation || ''
    }
    if (d.question_type === 'code' && d.code_detail) {
      form.description = d.code_detail.description || ''
      form.reference_code = d.code_detail.reference_code || ''
      form.test_cases = d.code_detail.test_cases?.length ? d.code_detail.test_cases : [{ input: '', output: '' }]
      form.time_limit = d.code_detail.time_limit || 1000
      form.memory_limit = d.code_detail.memory_limit || 256
    }

    formVisible.value = true
  } catch (e) {}
}

async function handleSubmitForm() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const payload = {
      question_type: form.question_type,
      title: form.title,
      category_id: form.category_id,
      sub_category_id: form.sub_category_id,
      difficulty: form.difficulty,
    }

    if (form.question_type === 'text') {
      payload.content = form.content
      payload.standard_answer = form.standard_answer
      payload.explanation = form.explanation
    } else {
      payload.description = form.description
      payload.reference_code = form.reference_code
      payload.test_cases = form.test_cases
      payload.time_limit = form.time_limit
      payload.memory_limit = form.memory_limit
    }

    if (editId.value) {
      await updateQuestion(editId.value, payload)
      ElMessage.success('更新成功')
    } else {
      await createQuestion(payload)
      ElMessage.success('创建成功')
    }
    formVisible.value = false
    fetchList()
  } catch (e) {}
  finally { submitting.value = false }
}

async function handleDelete(id) {
  try {
    await ElMessageBox.confirm('确定删除此题目吗？', '提示', { type: 'warning' })
    await deleteQuestion(id)
    ElMessage.success('已删除')
    fetchList()
  } catch (e) {}
}

async function fetchList() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize }
    if (search.value) params.search = search.value
    if (filters.category) params.category = filters.category
    if (filters.difficulty) params.difficulty = filters.difficulty
    if (filters.question_type) params.question_type = filters.question_type
    const res = await getAdminQuestions(params)
    list.value = res.data.results
    total.value = res.data.count
  } catch (e) {}
  finally { loading.value = false }
}

async function fetchCategories() {
  try { const res = await getAdminCategories(); categories.value = res.data } catch (e) {}
}

onMounted(() => { fetchCategories(); fetchList() })
</script>

<style scoped>
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--spacing-md); }
.page-header h3 { font-size: 16px; font-weight: 600; color: var(--text-primary); }
.header-actions { display: flex; gap: var(--spacing-sm); }
.filter-row { display: flex; gap: var(--spacing-sm); margin-bottom: var(--spacing-md); }

.table-wrap {
  background: var(--bg-card); border: 1px solid var(--border-default); border-radius: var(--radius-lg);
  overflow: hidden; box-shadow: var(--shadow-card);
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
.data-table tr:hover td { background: var(--bg-hover); }
.empty-cell { text-align: center; color: var(--text-tertiary); padding: var(--spacing-xxl) !important; }
.title-cell { max-width: 280px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.action-cell { white-space: nowrap; }

.diff-tag { font-size: 12px; font-weight: 500; padding: 2px 10px; border-radius: var(--radius-sm); }
.diff-tag.easy { color: var(--color-easy); background: var(--color-easy-bg); }
.diff-tag.medium { color: var(--color-medium); background: var(--color-medium-bg); }
.diff-tag.hard { color: var(--color-hard); background: var(--color-hard-bg); }

/* 详情弹窗 */
.detail-content { display: flex; flex-direction: column; gap: var(--spacing-md); }
.detail-row { display: flex; gap: var(--spacing-md); }
.detail-label { min-width: 80px; font-size: 13px; color: var(--text-tertiary); flex-shrink: 0; padding-top: 2px; }
.detail-text { font-size: 14px; color: var(--text-secondary); line-height: 1.6; white-space: pre-wrap; word-break: break-all; }

/* 表单 */
.form-inline { display: flex; gap: var(--spacing-md); }

.test-cases { display: flex; flex-direction: column; gap: var(--spacing-sm); width: 100%; }
.test-case-item { display: flex; align-items: flex-start; gap: var(--spacing-sm); }
.tc-fields { flex: 1; display: flex; gap: var(--spacing-sm); }
.tc-fields .el-input { flex: 1; }

/* 按钮 */
.btn-primary {
  height: 36px; padding: 0 20px; background: var(--btn-primary-bg); color: var(--btn-primary-text);
  border: none; border-radius: var(--radius-md); font-size: 14px; font-weight: 500; cursor: pointer;
  transition: background var(--transition-fast);
}
.btn-primary:hover { background: var(--btn-primary-hover); }
.btn-primary:disabled { background: #F2F3F5; color: #C9CDD4; cursor: not-allowed; }
.btn-primary.btn-sm { height: 32px; padding: 0 16px; font-size: 13px; }

.btn-secondary {
  height: 36px; padding: 0 20px; background: #fff; color: var(--text-primary);
  border: 1px solid var(--border-default); border-radius: var(--radius-md); font-size: 14px; cursor: pointer;
}
.btn-secondary:hover { background: var(--bg-hover); }
.btn-secondary.btn-sm { height: 32px; padding: 0 16px; font-size: 13px; }

.btn-text {
  background: none; border: none; font-size: 13px; color: var(--text-secondary); cursor: pointer;
  padding: 4px 8px; border-radius: var(--radius-sm); transition: all var(--transition-fast);
}
.btn-text:hover { color: var(--text-primary); background: var(--bg-hover); }
.btn-text.danger:hover { color: var(--color-danger); }

.pagination-wrap { display: flex; justify-content: center; margin-top: var(--spacing-lg); }
</style>