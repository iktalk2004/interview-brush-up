<template>
  <div class="settings-page">
    <h2 class="page-title">个人设置</h2>

    <div class="settings-card">
      <!-- 头像区域 -->
      <div class="avatar-section">
        <el-avatar :size="80" :src="userStore.avatar" />
        <div class="avatar-action">
          <button class="btn-secondary btn-sm" @click="triggerUpload">更换头像</button>
          <input ref="fileInput" type="file" accept="image/*" hidden @change="handleAvatarChange" />
          <p class="avatar-tip">支持 jpg、png 格式，最大 2MB</p>
        </div>
      </div>

      <div class="divider"></div>

      <!-- 基本信息 -->
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        size="large"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" />
        </el-form-item>

        <el-form-item label="邮箱">
          <el-input :model-value="userStore.userInfo?.email" disabled />
        </el-form-item>

        <el-form-item label="GitHub ID">
          <el-input v-model="form.github_id" placeholder="选填" />
        </el-form-item>

        <el-form-item label="技术水平" prop="tech_level">
          <el-radio-group v-model="form.tech_level">
            <el-radio v-for="item in TECH_LEVEL_OPTIONS" :key="item.value" :value="item.value">
              {{ item.label }}
            </el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="学历">
          <el-select v-model="form.education" placeholder="请选择" clearable style="width: 100%">
            <el-option v-for="item in EDUCATION_OPTIONS" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>

        <el-form-item label="感兴趣的方向" prop="interests">
          <el-checkbox-group v-model="form.interests">
            <el-checkbox v-for="item in interestOptions" :key="item" :label="item" :value="item">
              {{ item }}
            </el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item>
          <button type="button" class="btn-primary" :disabled="saving" @click="handleSave">
            {{ saving ? '保存中...' : '保存修改' }}
          </button>
        </el-form-item>
      </el-form>

      <div class="divider"></div>

      <!-- 修改密码 -->
      <h3 class="section-title">修改密码</h3>
      <el-form
        ref="pwdFormRef"
        :model="pwdForm"
        :rules="pwdRules"
        label-position="top"
        size="large"
      >
        <el-form-item label="原密码" prop="old_password">
          <el-input v-model="pwdForm.old_password" type="password" show-password />
        </el-form-item>

        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="pwdForm.new_password" type="password" placeholder="至少8位" show-password />
        </el-form-item>

        <el-form-item>
          <button type="button" class="btn-primary" :disabled="changingPwd" @click="handleChangePwd">
            {{ changingPwd ? '修改中...' : '修改密码' }}
          </button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { getUserProfile, updateUserProfile, uploadAvatar, changePassword } from '@/api/auth'
import { TECH_LEVEL_OPTIONS, EDUCATION_OPTIONS } from '@/utils/constants'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()
const formRef = ref(null)
const pwdFormRef = ref(null)
const fileInput = ref(null)
const saving = ref(false)
const changingPwd = ref(false)

const interestOptions = [
  'Python后端', 'Java后端', '前端开发', '算法',
  '计算机网络', '操作系统', '数据库', '设计模式',
]

const form = reactive({
  username: '',
  github_id: '',
  tech_level: 'beginner',
  education: '',
  interests: [],
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 20, message: '长度在2到20个字符', trigger: 'blur' },
  ],
  tech_level: [{ required: true, message: '请选择技术水平', trigger: 'change' }],
  interests: [{ type: 'array', required: true, min: 1, message: '请至少选择一个方向', trigger: 'change' }],
}

const pwdForm = reactive({
  old_password: '',
  new_password: '',
})

const pwdRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 8, message: '密码至少8位', trigger: 'blur' },
  ],
}

onMounted(async () => {
  try {
    const res = await getUserProfile()
    const data = res.data
    form.username = data.username
    form.github_id = data.github_id || ''
    form.tech_level = data.tech_level
    form.education = data.education || ''
    form.interests = data.interests || []
  } catch (e) {}
})

function triggerUpload() {
  fileInput.value.click()
}

async function handleAvatarChange(e) {
  const file = e.target.files[0]
  if (!file) return

  try {
    const res = await uploadAvatar(file)
    const newInfo = { ...userStore.userInfo, avatar: res.data.avatar }
    userStore.setUserInfo(newInfo)
    ElMessage.success('头像更新成功')
  } catch (err) {}

  e.target.value = ''
}

async function handleSave() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    const res = await updateUserProfile(form)
    userStore.setUserInfo(res.data)
    ElMessage.success('保存成功')
  } catch (e) {}
  finally { saving.value = false }
}

async function handleChangePwd() {
  const valid = await pwdFormRef.value.validate().catch(() => false)
  if (!valid) return

  changingPwd.value = true
  try {
    await changePassword(pwdForm)
    ElMessage.success('密码修改成功')
    pwdForm.old_password = ''
    pwdForm.new_password = ''
  } catch (e) {}
  finally { changingPwd.value = false }
}
</script>

<style scoped>
.settings-page {
  max-width: 640px;
  margin: 0 auto;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--spacing-lg);
}

.settings-card {
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  padding: var(--spacing-xl);
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
}

.avatar-action {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.avatar-tip {
  font-size: 12px;
  color: var(--text-tertiary);
}

.divider {
  height: 1px;
  background: var(--border-light);
  margin: var(--spacing-lg) 0;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--spacing-md);
}

.btn-primary {
  height: 40px;
  padding: 0 24px;
  background: var(--btn-primary-bg);
  color: var(--btn-primary-text);
  border: none;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background var(--transition-fast);
}
.btn-primary:hover { background: var(--btn-primary-hover); }
.btn-primary:disabled { background: #F2F3F5; color: #C9CDD4; cursor: not-allowed; }

.btn-secondary {
  background: #fff;
  color: var(--text-primary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  font-size: 13px;
  cursor: pointer;
  transition: all var(--transition-fast);
}
.btn-secondary:hover { background: var(--bg-hover); }
.btn-sm { height: 32px; padding: 0 14px; }
</style>