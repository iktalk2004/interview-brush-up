import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const getItem = (key) => localStorage.getItem(key)
const setItem = (key, value) => localStorage.setItem(key, value)
const removeItem = (key) => localStorage.removeItem(key)

export const useUserStore = defineStore('user', () => {
  const token = ref(getItem('access_token') || '')  // 访问令牌
  const refreshToken = ref(getItem('refresh_token') || '')  // 刷新令牌
  const userInfo = ref(JSON.parse(getItem('user_info') || 'null'))  // 用户信息

  const isLoggedIn = computed(() => !!token.value)  // 是否登录
  const isAdmin = computed(() => userInfo.value?.role === 'admin')  // 是否管理员
  const username = computed(() => userInfo.value?.username || '')  // 用户名
  const avatar = computed(() => userInfo.value?.avatar || '/default-avatar.png')  // 头像

  // 设置访问令牌和刷新令牌
  function setToken(access, refresh) {
    token.value = access
    refreshToken.value = refresh
    setItem('access_token', access)
    setItem('refresh_token', refresh)
  }

  // 设置用户信息
  function setUserInfo(info) {
    userInfo.value = info
    setItem('user_info', JSON.stringify(info))
  }

  // 注销登录
  function logout() {
    token.value = ''
    refreshToken.value = ''
    userInfo.value = null
    removeItem('access_token')
    removeItem('refresh_token')
    removeItem('user_info')
  }

  return {
    token, refreshToken, userInfo,
    isLoggedIn, isAdmin, username, avatar,
    setToken, setUserInfo, logout,
  }
})