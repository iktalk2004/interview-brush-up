<template>
  <div class="announcement-manage">
    <div class="page-header">
      <h3>公告管理</h3>
      <button class="btn-primary" @click="openCreate">新增公告</button>
    </div>

    <div class="list-wrap" v-loading="loading">
      <div v-if="list.length === 0 && !loading" class="empty-state">暂无公告</div>
      <div v-for="item in list" :key="item.id" class="item-card">
        <div class="item-left">
          <h4 class="item-title">{{ item.title }}</h4>
          <div class="item-meta">
            <span>{{ item.author_name }}</span>
            <span class="meta-dot">·</span>
            <span>{{ formatDateTime(item.created_at) }}</span>
            <span class="status-tag" :class="item.is_published ? 'published' : 'draft'">
              {{ item.is_published ? '已发布' : '草稿' }}
            </span>
          </div>
        </div>
        <div class="item-actions">
          <button class="btn-text" @click="openEdit(item)">编辑</button>
          <button class="btn-text danger" @click="handleDelete(item.id)">删除</button>
        </div>
      </div>
    </div>

    <div class="pagination-wrap" v-if="total > pageSize">
      <el-pagination v-model:current-page="page" :page-size="pageSize" :total="total" layout="prev, pager, next" @current-change="fetchList" />
    </div>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="editId ? '编辑公告' : '新增公告'" width="600px" :close-on-click-modal="false">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入公告标题" />
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input v-model="form.content" type="textarea" :rows="6" placeholder="请输入公告内容" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.is_published" active-text="发布" inactive-text="草稿" />
        </el-form-item>
      </el-form>
      <template #footer>
        <button class="btn-secondary" @click="dialogVisible = false">取消</button>
        <button class="btn-primary" :disabled="submitting" @click="handleSubmit" style="margin-left: 12px">
          {{ submitting ? '保存中...' : '保存' }}
        </button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getAdminAnnouncements, createAnnouncement, updateAnnouncement, deleteAnnouncement } from '@/api/announcements'
import { formatDateTime } from '@/utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const list = ref([])
const page = ref(1)
const pageSize = 20
const total = ref(0)

const dialogVisible = ref(false)
const editId = ref(null)
const formRef = ref(null)
const submitting = ref(false)

const form = reactive({ title: '', content: '', is_published: true })
const rules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入内容', trigger: 'blur' }],
}

function openCreate() {
  editId.value = null
  form.title = ''
  form.content = ''
  form.is_published = true
  dialogVisible.value = true
}

function openEdit(item) {
  editId.value = item.id
  form.title = item.title
  form.content = item.content
  form.is_published = item.is_published
  dialogVisible.value = true
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (editId.value) {
      await updateAnnouncement(editId.value, form)
      ElMessage.success('更新成功')
    } else {
      await createAnnouncement(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchList()
  } catch (e) {}
  finally { submitting.value = false }
}

async function handleDelete(id) {
  try {
    await ElMessageBox.confirm('确定删除这条公告吗？', '提示', { type: 'warning' })
    await deleteAnnouncement(id)
    ElMessage.success('已删除')
    fetchList()
  } catch (e) {}
}

async function fetchList() {
  loading.value = true
  try {
    const res = await getAdminAnnouncements({ page: page.value, page_size: pageSize })
    list.value = res.data.results
    total.value = res.data.count
  } catch (e) {}
  finally { loading.value = false }
}

onMounted(fetchList)
</script>

<style scoped>
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--spacing-lg); }
.page-header h3 { font-size: 16px; font-weight: 600; color: var(--text-primary); }

.list-wrap {
  border: 1px solid var(--border-default); border-radius: var(--radius-lg); overflow: hidden;
  background: var(--border-light); display: flex; flex-direction: column; gap: 1px; min-height: 200px;
}
.empty-state { padding: var(--spacing-xxl); text-align: center; color: var(--text-tertiary); background: var(--bg-card); }

.item-card {
  display: flex; align-items: center; justify-content: space-between;
  padding: var(--spacing-md) var(--spacing-lg); background: var(--bg-card);
}
.item-left { flex: 1; min-width: 0; }
.item-title { font-size: 15px; font-weight: 500; color: var(--text-primary); margin-bottom: 4px; }
.item-meta { display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--text-tertiary); }
.meta-dot { color: var(--text-placeholder); }
.status-tag { padding: 1px 8px; border-radius: var(--radius-sm); font-size: 11px; font-weight: 500; }
.status-tag.published { color: var(--color-easy); background: var(--color-easy-bg); }
.status-tag.draft { color: var(--text-tertiary); background: var(--color-info-bg); }

.item-actions { display: flex; gap: var(--spacing-sm); flex-shrink: 0; }

.btn-text {
  background: none; border: none; font-size: 13px; color: var(--text-secondary); cursor: pointer;
  padding: 4px 8px; border-radius: var(--radius-sm); transition: all var(--transition-fast);
}
.btn-text:hover { color: var(--text-primary); background: var(--bg-hover); }
.btn-text.danger:hover { color: var(--color-danger); }

.btn-primary {
  height: 36px; padding: 0 20px; background: var(--btn-primary-bg); color: var(--btn-primary-text);
  border: none; border-radius: var(--radius-md); font-size: 14px; font-weight: 500; cursor: pointer;
  transition: background var(--transition-fast);
}
.btn-primary:hover { background: var(--btn-primary-hover); }
.btn-primary:disabled { background: #F2F3F5; color: #C9CDD4; cursor: not-allowed; }

.btn-secondary {
  height: 36px; padding: 0 20px; background: #fff; color: var(--text-primary);
  border: 1px solid var(--border-default); border-radius: var(--radius-md); font-size: 14px; cursor: pointer;
}
.btn-secondary:hover { background: var(--bg-hover); }

.pagination-wrap { display: flex; justify-content: center; margin-top: var(--spacing-lg); }
</style>