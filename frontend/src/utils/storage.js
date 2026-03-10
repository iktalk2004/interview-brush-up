/**
 * 本地存储工具函数, 用于操作 localStorage
 */
export const getItem = (key) => localStorage.getItem(key)
export const setItem = (key, value) => localStorage.setItem(key, value)
export const removeItem = (key) => localStorage.removeItem(key)
