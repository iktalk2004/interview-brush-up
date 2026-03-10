import request from './index'

// 注册
export function register(data) {
  return request.post('/auth/register', data)
}

// 登录
export function login(data) {
  return request.post('/auth/login', data)
}

// 刷新Token
export function refreshToken(data) {
  return request.post('/auth/token/refresh', data)
}

// 发送验证码
export function forgotPassword(data) {
  return request.post('/auth/forgot-password', data)
}

// 重置密码
export function resetPassword(data) {
  return request.post('/auth/reset-password', data)
}

// 获取个人信息
export function getUserProfile() {
  return request.get('/user/profile')
}

// 修改个人信息
export function updateUserProfile(data) {
  return request.put('/user/profile', data)
}

// 修改密码
export function changePassword(data) {
  return request.post('/user/change-password', data)
}

// 上传头像
export function uploadAvatar(file) {
  const formData = new FormData()
  formData.append('avatar', file)
  return request.post('/user/avatar', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}