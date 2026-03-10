import request from './index'

// ============ 分类管理 ============

export function getAdminCategories() {
  return request.get('/admin/categories')
}

export function createCategory(data) {
  return request.post('/admin/categories', data)
}

export function updateCategory(id, data) {
  return request.put(`/admin/categories/${id}`, data)
}

export function deleteCategory(id) {
  return request.delete(`/admin/categories/${id}`)
}

export function createSubCategory(data) {
  return request.post('/admin/sub-categories', data)
}

export function updateSubCategory(id, data) {
  return request.put(`/admin/sub-categories/${id}`, data)
}

export function deleteSubCategory(id) {
  return request.delete(`/admin/sub-categories/${id}`)
}

// ============ 题目管理 ============

export function getAdminQuestions(params) {
  return request.get('/admin/questions', { params })
}

export function getAdminQuestionDetail(id) {
  return request.get(`/admin/questions/${id}`)
}

export function createQuestion(data) {
  return request.post('/admin/questions', data)
}

export function updateQuestion(id, data) {
  return request.put(`/admin/questions/${id}`, data)
}

export function deleteQuestion(id) {
  return request.delete(`/admin/questions/${id}`)
}

export function importQuestions(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/admin/questions/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

// ============ 用户管理 ============

export function getAdminUsers(params) {
  return request.get('/admin/users', { params })
}

export function toggleUserStatus(userId) {
  return request.put(`/admin/users/${userId}/status`)
}

export function getAdminUserDetail(userId) {
  return request.get(`/admin/users/${userId}`)
}