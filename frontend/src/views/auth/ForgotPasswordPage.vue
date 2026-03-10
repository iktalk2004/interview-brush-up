<template>
  <div class="forgot-page">
    <h2 class="page-title">找回密码</h2>
    <p class="page-desc">通过邮箱验证码重置密码</p>

    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-position="top"
      size="large"
    >
      <el-form-item label="注册邮箱" prop="email">
        <el-input v-model="form.email" placeholder="请输入注册时使用的邮箱" />
      </el-form-item>

      <el-form-item label="验证码" prop="code">
        <div class="code-row">
          <el-input v-model="form.code" placeholder="6位验证码" maxlength="6" />
          <button type="button" class="btn-secondary btn-code" :disabled="countdown > 0 || sendingCode" @click="handleSendCode">
            {{ countdown > 0 ? `${countdown}s后重试` : (sendingCode ? '发送中...' : '发送验证码') }}
          </button>
        </div>
      </el-form-item>

      <el-form-item label="新密码" prop="new_password">
        <el-input v-model="form.new_password" type="password" placeholder="至少8位" show-password />
      </el-form-item>

      <el-form-item>
        <button type="button" class="btn-primary btn-full" :disabled="loading" @click="handleReset">
          {{ loading ? '重置中...' : '重置密码' }}
        </button>
      </el-form-item>
    </el-form>

    <div class="form-footer">
      <router-link to="/login" class="link">返回登录</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { forgotPassword, resetPassword } from '@/api/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)
const sendingCode = ref(false)
const countdown = ref(0)
let timer = null

const form = reactive({
  email: '',
  code: '',
  new_password: '',
})

const rules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' },
  ],
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 6, message: '验证码为6位', trigger: 'blur' },
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 8, message: '密码至少8位', trigger: 'blur' },
  ],
}

async function handleSendCode() {
  if (!form.email) {
    ElMessage.warning('请先输入邮箱')
    return
  }

  sendingCode.value = true
  try {
    await forgotPassword({ email: form.email })
    ElMessage.success('验证码已发送，请查收邮箱')
    startCountdown()
  } catch (e) {
    // 错误已在拦截器处理
  } finally {
    sendingCode.value = false
  }
}

function startCountdown() {
  countdown.value = 60
  timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(timer)
      timer = null
    }
  }, 1000)
}

async function handleReset() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await resetPassword(form)
    ElMessage.success('密码重置成功，请重新登录')
    router.push('/login')
  } catch (e) {
    // 错误已在拦截器处理
  } finally {
    loading.value = false
  }
}

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
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
  margin-bottom: var(--spacing-xl);
}

.code-row {
  display: flex;
  gap: var(--spacing-sm);
  width: 100%;
}

.code-row .el-input {
  flex: 1;
}

.btn-code {
  white-space: nowrap;
  height: 40px;
  padding: 0 16px;
  font-size: 13px;
}

.btn-primary {
  width: 100%;
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
  background: #fff;
  color: var(--text-primary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  font-size: 14px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-secondary:hover { background: var(--bg-hover); }
.btn-secondary:disabled { color: #C9CDD4; cursor: not-allowed; }

.form-footer {
  text-align: center;
  margin-top: var(--spacing-lg);
}

.link {
  font-size: 14px;
  color: var(--text-secondary);
}

.link:hover {
  color: var(--text-primary);
}
</style>