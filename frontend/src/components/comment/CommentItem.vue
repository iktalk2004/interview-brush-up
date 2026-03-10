<template>
  <div class="comment-item">
    <div class="comment-main">
      <el-avatar :size="32" :src="comment.avatar || '/default-avatar.png'" />
      <div class="comment-body">
        <div class="comment-header">
          <span class="comment-user">{{ comment.username }}</span>
          <span class="comment-time">{{ formatDateTime(comment.created_at) }}</span>
        </div>
        <p class="comment-content">{{ comment.content }}</p>
        <div class="comment-actions">
          <span class="action-btn" @click="showReplyForm = !showReplyForm">回复</span>
          <span v-if="canDelete" class="action-btn danger" @click="handleDelete">删除</span>
        </div>

        <!-- 回复输入框 -->
        <CommentForm
          v-if="showReplyForm"
          :placeholder="`回复 ${comment.username}...`"
          :show-cancel="true"
          @submit="handleReply"
          @cancel="showReplyForm = false"
        />

        <!-- 回复列表 -->
        <div class="replies" v-if="comment.replies && comment.replies.length">
          <div v-for="reply in comment.replies" :key="reply.id" class="reply-item">
            <el-avatar :size="24" :src="reply.avatar || '/default-avatar.png'" />
            <div class="reply-body">
              <div class="reply-header">
                <span class="reply-user">{{ reply.username }}</span>
                <span class="reply-to" v-if="reply.reply_to">回复 {{ reply.reply_to }}</span>
                <span class="reply-time">{{ formatDateTime(reply.created_at) }}</span>
              </div>
              <p class="reply-content">{{ reply.content }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { formatDateTime } from '@/utils/format'
import CommentForm from './CommentForm.vue'

const props = defineProps({
  comment: { type: Object, required: true },
  canDelete: { type: Boolean, default: false },
})

const emit = defineEmits(['reply', 'delete'])
const showReplyForm = ref(false)

function handleReply(content) {
  emit('reply', { parentId: props.comment.id, content })
  showReplyForm.value = false
}

function handleDelete() {
  emit('delete', props.comment.id)
}
</script>

<style scoped>
.comment-item {
  padding: var(--spacing-md) 0;
}

.comment-item + .comment-item {
  border-top: 1px solid var(--border-light);
}

.comment-main {
  display: flex;
  gap: var(--spacing-sm);
}

.comment-body {
  flex: 1;
  min-width: 0;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: 4px;
}

.comment-user {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.comment-time {
  font-size: 12px;
  color: var(--text-placeholder);
}

.comment-content {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: var(--spacing-sm);
}

.comment-actions {
  display: flex;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-sm);
}

.action-btn {
  font-size: 12px;
  color: var(--text-tertiary);
  cursor: pointer;
}

.action-btn:hover { color: var(--text-primary); }
.action-btn.danger:hover { color: var(--color-danger); }

.replies {
  margin-top: var(--spacing-sm);
  padding-left: var(--spacing-md);
  border-left: 2px solid var(--border-light);
}

.reply-item {
  display: flex;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) 0;
}

.reply-item + .reply-item {
  border-top: 1px solid var(--border-light);
}

.reply-body { flex: 1; }

.reply-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: 2px;
}

.reply-user {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

.reply-to {
  font-size: 12px;
  color: var(--text-tertiary);
}

.reply-time {
  font-size: 12px;
  color: var(--text-placeholder);
}

.reply-content {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
}
</style>