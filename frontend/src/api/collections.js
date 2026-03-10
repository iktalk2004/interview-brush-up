import request from './index'

export function getCollections(params) {
  return request.get('/collections/', { params })
}

export function addCollection(questionId) {
  return request.post('/collections/', { question_id: questionId })
}

export function removeCollection(questionId) {
  return request.delete(`/collections/${questionId}`)
}

export function checkCollection(questionId) {
  return request.get(`/collections/${questionId}/check`)
}