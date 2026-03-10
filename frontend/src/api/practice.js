import request from './index'

export function submitTextAnswer(data) {
  return request.post('/submit/text', data)
}

export function getQuestionHistory(questionId) {
  return request.get(`/practice/history/${questionId}`)
}

export function getMistakes(params) {
  return request.get('/practice/mistakes', { params })
}

export function removeMistake(questionId) {
  return request.delete(`/practice/mistakes/${questionId}`)
}

export function getTopicList() {
  return request.get('/practice/topics')
}

export function getTopicQuestions(params) {
  return request.get('/practice/topics/questions', { params })
}