import request from '@/utils/request'

export function login(data) {
  return request({
    url: '/auth/admin/login',
    method: 'post',
    data
  })
}

export function logout() {
  return request({
    url: '/auth/logout', // 假设有 logout 接口，或者仅前端清除 Token
    method: 'post'
  })
}

export function getUserInfo() {
  return request({
    url: '/auth/profile', // 使用通用 profile 接口
    method: 'get'
  })
}
