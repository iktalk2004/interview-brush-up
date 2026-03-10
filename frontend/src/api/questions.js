import request from './index'

// 获取分类树
export function getCategories() {
  return request.get('/categories/')
}

// 获取题目列表
export function getQuestions(params) {
  return request.get('/questions/', { params })
}

// 获取题目详情
export function getQuestionDetail(id) {
  return request.get(`/questions/${id}`)
}