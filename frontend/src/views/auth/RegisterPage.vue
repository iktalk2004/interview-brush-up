<template>
  <div class="register-page">
    <h2 class="page-title">注册</h2>
    <p class="page-desc">创建账号，开始你的刷题之旅</p>

    <!-- 步骤指示器 -->
    <div class="steps">
      <div class="step" :class="{ active: step >= 1, done: step > 1 }">
        <span class="step-num">1</span>
        <span class="step-label">基本信息</span>
      </div>
      <div class="step-line" :class="{ active: step > 1 }"></div>
      <div class="step" :class="{ active: step >= 2 }">
        <span class="step-num">2</span>
        <span class="step-label">偏好设置</span>
      </div>
    </div>

    <!-- 步骤1: 基本信息 -->
    <el-form
      v-show="step === 1"
      ref="step1Ref"
      :model="form"
      :rules="step1Rules"
      label-position="top"
      size="large"
    >
      <el-form-item label="用户名" prop="username">
        <el-input v-model="form.username" placeholder="请输入用户名" />
      </el-form-item>

      <el-form-item label="邮箱" prop="email">
        <el-input v-model="form.email" placeholder="请输入邮箱" />
      </el-form-item>

      <el-form-item label="密码" prop="password">
        <el-input v-model="form.password" type="password" placeholder="至少8位，包含字母和数字" show-password />
      </el-form-item>

      <el-form-item label="确认密码" prop="confirm_password">
        <el-input v-model="form.confirm_password" type="password" placeholder="再次输入密码" show-password />
      </el-form-item>

      <el-form-item>
        <button type="button" class="btn-primary btn-full" @click="nextStep">下一步</button>
      </el-form-item>
    </el-form>

    <!-- 步骤2: 偏好设置 -->
    <el-form
      v-show="step === 2"
      ref="step2Ref"
      :model="form"
      :rules="step2Rules"
      label-position="top"
      size="large"
    >
      <el-form-item label="技术水平" prop="tech_level">
        <el-radio-group v-model="form.tech_level">
          <el-radio v-for="item in TECH_LEVEL_OPTIONS" :key="item.value" :value="item.value">
            {{ item.label }}
          </el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="学历" prop="education">
        <el-select v-model="form.education" placeholder="请选择学历（选填）" clearable style="width: 100%">
          <el-option v-for="item in EDUCATION_OPTIONS" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
      </el-form-item>

      <el-form-item label="GitHub ID">
        <el-input v-model="form.github_id" placeholder="选填" />
      </el-form-item>

      <el-form-item label="感兴趣的方向（至少选1个）" prop="interests">
        <el-checkbox-group v-model="form.interests">
          <el-checkbox v-for="item in interestOptions" :key="item" :label="item" :value="item">
            {{ item }}
          </el-checkbox>
        </el-checkbox-group>
      </el-form-item>

      <el-form-item>
        <div class="btn-group">
          <button type="button" class="btn-secondary" @click="step = 1">上一步</button>
          <button type="button" class="btn-primary" :disabled="loading" @click="handleRegister">
            {{ loading ? '注册中...' : '完成注册' }}
          </button>
        </div>
      </el-form-item>
    </el-form>

    <div class="form-footer">
      <span>已有账号？</span>
      <router-link to="/login" class="link">立即登录</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { register } from '@/api/auth'
import { TECH_LEVEL_OPTIONS, EDUCATION_OPTIONS } from '@/utils/constants'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const step1Ref = ref(null)
const step2Ref = ref(null)
const step = ref(1)
const loading = ref(false)

const interestOptions = [
  'Python后端', 'Java后端', '前端开发', '算法',
  '计算机网络', '操作系统', '数据库', '设计模式',
]

const form = reactive({
  username: '',
  email: '',
  password: '',
  confirm_password: '',
  tech_level: 'beginner',
  education: '',
  github_id: '',
  interests: [],
})

const step1Rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 20, message: '长度在2到20个字符', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, message: '密码至少8位', trigger: 'blur' },
  ],
  confirm_password: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== form.password) {
          callback(new Error('两次密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
}

const step2Rules = {
  tech_level: [{ required: true, message: '请选择技术水平', trigger: 'change' }],
  interests: [
    {
      type: 'array',
      required: true,
      min: 1,
      message: '请至少选择一个方向',
      trigger: 'change',
    },
  ],
}

async function nextStep() {
  const valid = await step1Ref.value.validate().catch(() => false)
  if (valid) step.value = 2
}

async function handleRegister() {
  const valid = await step2Ref.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const res = await register(form)
    userStore.setToken(res.data.access, res.data.refresh)
    userStore.setUserInfo(res.data.user)
    ElMessage.success('注册成功')
    router.push('/')
  } catch (e) {
    // 错误已在拦截器处理
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.page-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--spacing-sm);
}

.page-desc {
  font-size: 14px;
  color: var(--text-tertiary);
  margin-bottom: var(--spacing-lg);
}

.steps {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--spacing-xl);
}

.step {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.step-num {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  background: var(--bg-page);
  color: var(--text-placeholder);
  border: 1px solid var(--border-default);
  transition: all var(--transition-base);
}

.step.active .step-num {
  background: var(--btn-primary-bg);
  color: #fff;
  border-color: var(--btn-primary-bg);
}

.step.done .step-num {
  background: var(--color-easy);
  border-color: var(--color-easy);
  color: #fff;
}

.step-label {
  font-size: 13px;
  color: var(--text-placeholder);
}

.step.active .step-label {
  color: var(--text-primary);
  font-weight: 500;
}

.step-line {
  width: 60px;
  height: 1px;
  background: var(--border-default);
  margin: 0 var(--spacing-md);
  transition: background var(--transition-base);
}

.step-line.active {
  background: var(--btn-primary-bg);
}

.btn-primary {
  flex: 1;
  height: 44px;
  background: var(--btn-primary-bg);
  color: var(--btn-primary-text);
  border: none;
  border-radius: var(--radius-md);
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: background var(--transition-fast);
}

.btn-primary:hover { background: var(--btn-primary-hover); }
.btn-primary:disabled { background: #F2F3F5; color: #C9CDD4; cursor: not-allowed; }

.btn-full { width: 100%; }

.btn-secondary {
  flex: 1;
  height: 44px;
  background: #fff;
  color: var(--text-primary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-secondary:hover { background: var(--bg-hover); }

.btn-group {
  display: flex;
  gap: var(--spacing-md);
  width: 100%;
}

.form-footer {
  text-align: center;
  font-size: 14px;
  color: var(--text-tertiary);
  margin-top: var(--spacing-lg);
}

.link {
  color: var(--text-primary);
  font-weight: 500;
  margin-left: 4px;
}
</style>