<template>
  <div class="comment-form">
    <el-input
      v-model="content"
      type="textarea"
      :rows="3"
      :placeholder="placeholder"
      resize="none"
    />
    <div class="form-actions">
      <button v-if="showCancel" class="btn-secondary btn-sm" @click="$emit('cancel')">取消</button>
      <button class="btn-primary btn-sm" :disabled="!content.trim() || submitting" @click="handleSubmit">
        {{ submitting ? '发送中...' : '发表' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  placeholder: { type: String, default: '写下你的评论...' },
  showCancel: { type: Boolean, default: false },
})

const emit = defineEmits(['submit', 'cancel'])
const content = ref('')
const submitting = ref(false)

async function handleSubmit() {
  submitting.value = true
  try {
    await emit('submit', content.value)
    content.value = ''
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.comment-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
}

.btn-primary {
  height: 32px;
  padding: 0 16px;
  background: var(--btn-primary-bg);
  color: var(--btn-primary-text);
  border: none;
  border-radius: var(--radius-md);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background var(--transition-fast);
}
.btn-primary:hover { background: var(--btn-primary-hover); }
.btn-primary:disabled { background: #F2F3F5; color: #C9CDD4; cursor: not-allowed; }

.btn-secondary {
  height: 32px;
  padding: 0 16px;
  background: #fff;
  color: var(--text-primary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  font-size: 13px;
  cursor: pointer;
  transition: all var(--transition-fast);
}
.btn-secondary:hover { background: var(--bg-hover); }
.btn-sm { height: 32px; }
</style>