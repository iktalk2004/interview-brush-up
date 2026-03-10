import request from './index'

export function getDashboard() {
  return request.get('/stats/dashboard')
}

export function reportLearningTime(data) {
  return request.post('/stats/learning-time', data)
}

export function getRanking(params) {
  return request.get('/stats/ranking', { params })
}

export function getPracticeHistory(params) {
  return request.get('/stats/history', { params })
}