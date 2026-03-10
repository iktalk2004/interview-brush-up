import request from './index'

export function getHomeRecommend() {
  return request.get('/recommend/home')
}

export function getDailyRecommend() {
  return request.get('/recommend/daily')
}

export function getAlgorithmCompare() {
  return request.get('/admin/recommend/compare')
}

export function triggerSimilarity() {
  return request.post('/admin/recommend/trigger')
}