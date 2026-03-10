<template>
  <div class="comment-list-wrap">
    <h3 class="section-title">评论 ({{ comments.length }})</h3>

    <!-- 发表评论 -->
    <CommentForm placeholder="写下你的评论..." @submit="handleCreate" />

    <!-- 评论列表 -->
    <div class="comment-list" v-if="comments.length">
      <CommentItem
        v-for="item in comments"
        :key="item.id"
        :comment="item"
        :can-delete="item.username === currentUsername"
        @reply="handleReply"
        @delete="handleDelete"
      />
    </div>
    <div v-else class="empty-hint">暂无评论，来发表第一条吧</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getComments, createComment, deleteComment } from '@/api/comments'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import CommentForm from './CommentForm.vue'
import CommentItem from './CommentItem.vue'

const props = defineProps({
  questionId: { type: Number, required: true },
})

const userStore = useUserStore()
const currentUsername = userStore.username
const comments = ref([])

async function fetchComments() {
  try {
    const res = await getComments(props.questionId)
    comments.value = res.data
  } catch (e) {}
}

async function handleCreate(content) {
  try {
    await createComment({
      question_id: props.questionId,
      content,
    })
    ElMessage.success('评论成功')
    fetchComments()
  } catch (e) {}
}

async function handleReply({ parentId, content }) {
  try {
    await createComment({
      question_id: props.questionId,
      parent_id: parentId,
      content,
    })
    ElMessage.success('回复成功')
    fetchComments()
  } catch (e) {}
}

async function handleDelete(commentId) {
  try {
    await ElMessageBox.confirm('确定删除这条评论吗？', '提示', { type: 'warning' })
    await deleteComment(commentId)
    ElMessage.success('已删除')
    fetchComments()
  } catch (e) {}
}

onMounted(fetchComments)
</script>

<style scoped>
.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--spacing-md);
}

.comment-list {
  margin-top: var(--spacing-md);
}

.empty-hint {
  text-align: center;
  color: var(--text-tertiary);
  font-size: 14px;
  padding: var(--spacing-lg);
}
</style>