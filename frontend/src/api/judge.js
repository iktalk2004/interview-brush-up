import request from './index'

export function submitCode(data) {
  return request.post('/judge/submit', data)
}

export function getJudgeTask(taskId) {
  return request.get(`/judge/task/${taskId}`)
}

export function getJudgeHistory(questionId) {
  return request.get(`/judge/history/${questionId}`)
}