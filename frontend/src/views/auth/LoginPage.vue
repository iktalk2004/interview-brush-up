<template>
  <div class="login-page">
    <h2 class="page-title">登录</h2>
    <p class="page-desc">欢迎回来，请登录你的账号</p>

    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-position="top"
      size="large"
      @keyup.enter="handleLogin"
    >
      <el-form-item label="用户名或邮箱" prop="account">
        <el-input v-model="form.account" placeholder="请输入用户名或邮箱" />
      </el-form-item>

      <el-form-item label="密码" prop="password">
        <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
      </el-form-item>

      <div class="form-actions">
        <router-link to="/forgot-password" class="forgot-link">忘记密码？</router-link>
      </div>

      <el-form-item>
        <button type="button" class="btn-primary btn-full" :disabled="loading" @click="handleLogin">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </el-form-item>
    </el-form>

    <div class="form-footer">
      <span>还没有账号？</span>
      <router-link to="/register" class="link">立即注册</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { login } from '@/api/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  account: '',
  password: '',
})

const rules = {
  account: [{ required: true, message: '请输入用户名或邮箱', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const res = await login(form)
    userStore.setToken(res.data.access, res.data.refresh)
    userStore.setUserInfo(res.data.user)
    ElMessage.success('登录成功')

    const redirect = route.query.redirect || '/'
    router.push(redirect)
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
  margin-bottom: var(--spacing-xl);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-bottom: var(--spacing-md);
}

.forgot-link {
  font-size: 13px;
  color: var(--text-secondary);
  text-decoration: none;
}

.forgot-link:hover {
  color: var(--text-primary);
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

.btn-primary:hover {
  background: var(--btn-primary-hover);
}

.btn-primary:disabled {
  background: var(--btn-disabled-bg, #F2F3F5);
  color: var(--btn-disabled-text, #C9CDD4);
  cursor: not-allowed;
}

.btn-full {
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