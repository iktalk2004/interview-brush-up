<template>
  <div class="category-manage">
    <div class="page-header">
      <h3>分类管理</h3>
      <button class="btn-primary" @click="openCreateCategory">新增一级分类</button>
    </div>

    <div class="category-list" v-loading="loading">
      <div v-if="categories.length === 0 && !loading" class="empty-state">暂无分类</div>

      <div v-for="cat in categories" :key="cat.id" class="cat-group">
        <div class="cat-header">
          <div class="cat-info">
            <h4>{{ cat.name }}</h4>
            <span class="cat-desc" v-if="cat.description">{{ cat.description }}</span>
          </div>
          <div class="cat-actions">
            <button class="btn-text" @click="openAddSub(cat)">添加子分类</button>
            <button class="btn-text" @click="openEditCategory(cat)">编辑</button>
            <button class="btn-text danger" @click="handleDeleteCategory(cat.id)">删除</button>
          </div>
        </div>
        <div class="sub-list" v-if="cat.sub_categories && cat.sub_categories.length">
          <div v-for="sub in cat.sub_categories" :key="sub.id" class="sub-item">
            <span class="sub-name">{{ sub.name }}</span>
            <div class="sub-actions">
              <button class="btn-text" @click="openEditSub(sub, cat.id)">编辑</button>
              <button class="btn-text danger" @click="handleDeleteSub(sub.id)">删除</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 一级分类弹窗 -->
    <el-dialog v-model="catDialogVisible" :title="editCatId ? '编辑分类' : '新增分类'" width="480px" :close-on-click-modal="false">
      <el-form ref="catFormRef" :model="catForm" :rules="catRules" label-position="top">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="catForm.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="catForm.description" placeholder="选填" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="catForm.sort_order" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <button class="btn-secondary" @click="catDialogVisible = false">取消</button>
        <button class="btn-primary" @click="handleSaveCategory" style="margin-left: 12px">保存</button>
      </template>
    </el-dialog>

    <!-- 子分类弹窗 -->
    <el-dialog v-model="subDialogVisible" :title="editSubId ? '编辑子分类' : '添加子分类'" width="480px" :close-on-click-modal="false">
      <el-form ref="subFormRef" :model="subForm" :rules="subRules" label-position="top">
        <el-form-item label="子分类名称" prop="name">
          <el-input v-model="subForm.name" placeholder="请输入子分类名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="subForm.description" placeholder="选填" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="subForm.sort_order" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <button class="btn-secondary" @click="subDialogVisible = false">取消</button>
        <button class="btn-primary" @click="handleSaveSub" style="margin-left: 12px">保存</button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import {
  getAdminCategories, createCategory, updateCategory, deleteCategory,
  createSubCategory, updateSubCategory, deleteSubCategory,
} from '@/api/admin'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const categories = ref([])

// 一级分类
const catDialogVisible = ref(false)
const editCatId = ref(null)
const catFormRef = ref(null)
const catForm = reactive({ name: '', description: '', sort_order: 0 })
const catRules = { name: [{ required: true, message: '请输入名称', trigger: 'blur' }] }

// 子分类
const subDialogVisible = ref(false)
const editSubId = ref(null)
const subParentId = ref(null)
const subFormRef = ref(null)
const subForm = reactive({ name: '', description: '', sort_order: 0 })
const subRules = { name: [{ required: true, message: '请输入名称', trigger: 'blur' }] }

function openCreateCategory() {
  editCatId.value = null; catForm.name = ''; catForm.description = ''; catForm.sort_order = 0
  catDialogVisible.value = true
}
function openEditCategory(cat) {
  editCatId.value = cat.id; catForm.name = cat.name; catForm.description = cat.description || ''; catForm.sort_order = cat.sort_order || 0
  catDialogVisible.value = true
}
function openAddSub(cat) {
  editSubId.value = null; subParentId.value = cat.id; subForm.name = ''; subForm.description = ''; subForm.sort_order = 0
  subDialogVisible.value = true
}
function openEditSub(sub, catId) {
  editSubId.value = sub.id; subParentId.value = catId; subForm.name = sub.name; subForm.description = sub.description || ''; subForm.sort_order = sub.sort_order || 0
  subDialogVisible.value = true
}

async function handleSaveCategory() {
  const valid = await catFormRef.value.validate().catch(() => false)
  if (!valid) return
  try {
    if (editCatId.value) { await updateCategory(editCatId.value, catForm); ElMessage.success('更新成功') }
    else { await createCategory(catForm); ElMessage.success('创建成功') }
    catDialogVisible.value = false; fetchList()
  } catch (e) {}
}
async function handleDeleteCategory(id) {
  try {
    await ElMessageBox.confirm('确定删除此分类吗？', '提示', { type: 'warning' })
    await deleteCategory(id); ElMessage.success('已删除'); fetchList()
  } catch (e) {}
}
async function handleSaveSub() {
  const valid = await subFormRef.value.validate().catch(() => false)
  if (!valid) return
  try {
    const data = { ...subForm, category: subParentId.value }
    if (editSubId.value) { await updateSubCategory(editSubId.value, data); ElMessage.success('更新成功') }
    else { await createSubCategory(data); ElMessage.success('创建成功') }
    subDialogVisible.value = false; fetchList()
  } catch (e) {}
}
async function handleDeleteSub(id) {
  try {
    await ElMessageBox.confirm('确定删除此子分类吗？', '提示', { type: 'warning' })
    await deleteSubCategory(id); ElMessage.success('已删除'); fetchList()
  } catch (e) {}
}

async function fetchList() {
  loading.value = true
  try { const res = await getAdminCategories(); categories.value = res.data } catch (e) {}
  finally { loading.value = false }
}

onMounted(fetchList)
</script>

<style scoped>
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--spacing-lg); }
.page-header h3 { font-size: 16px; font-weight: 600; color: var(--text-primary); }
.empty-state { padding: var(--spacing-xxl); text-align: center; color: var(--text-tertiary); }

.category-list { display: flex; flex-direction: column; gap: var(--spacing-md); }
.cat-group {
  background: var(--bg-card); border: 1px solid var(--border-default); border-radius: var(--radius-lg);
  overflow: hidden; box-shadow: var(--shadow-card);
}
.cat-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: var(--spacing-md) var(--spacing-lg); border-bottom: 1px solid var(--border-light);
}
.cat-info h4 { font-size: 15px; font-weight: 600; color: var(--text-primary); margin-bottom: 2px; }
.cat-desc { font-size: 12px; color: var(--text-tertiary); }
.cat-actions { display: flex; gap: var(--spacing-xs); }

.sub-list { padding: var(--spacing-sm) var(--spacing-lg); }
.sub-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: var(--spacing-sm) var(--spacing-md); border-radius: var(--radius-sm);
}
.sub-item:hover { background: var(--bg-hover); }
.sub-name { font-size: 14px; color: var(--text-secondary); }
.sub-actions { display: flex; gap: var(--spacing-xs); }

.btn-primary {
  height: 36px; padding: 0 20px; background: var(--btn-primary-bg); color: var(--btn-primary-text);
  border: none; border-radius: var(--radius-md); font-size: 14px; font-weight: 500; cursor: pointer;
}
.btn-primary:hover { background: var(--btn-primary-hover); }
.btn-secondary {
  height: 36px; padding: 0 20px; background: #fff; color: var(--text-primary);
  border: 1px solid var(--border-default); border-radius: var(--radius-md); font-size: 14px; cursor: pointer;
}
.btn-secondary:hover { background: var(--bg-hover); }
.btn-text {
  background: none; border: none; font-size: 12px; color: var(--text-tertiary); cursor: pointer;
  padding: 4px 8px; border-radius: var(--radius-sm); transition: all var(--transition-fast);
}
.btn-text:hover { color: var(--text-primary); background: var(--bg-hover); }
.btn-text.danger:hover { color: var(--color-danger); }
</style>