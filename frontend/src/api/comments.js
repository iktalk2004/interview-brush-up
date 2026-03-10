import request from './index'

export function getComments(questionId) {
  return request.get(`/comments/${questionId}`)
}

export function createComment(data) {
  return request.post('/comments/', data)
}

export function deleteComment(commentId) {
  return request.delete(`/comments/${commentId}/delete`)
}