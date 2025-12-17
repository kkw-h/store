import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login, logout, getUserInfo } from '@/api/auth'
import { getToken, setToken, removeToken } from '@/utils/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(getToken())
  const userInfo = ref({})

  function loginAction(loginForm) {
    return new Promise((resolve, reject) => {
      login(loginForm).then(res => {
        // res 是 response.data (因为拦截器里返回了 res.data)
        // 假设返回结构: { token: '...', userInfo: { ... } }
        const { token: accessToken, userInfo: user } = res
        
        token.value = accessToken
        userInfo.value = user
        setToken(accessToken)
        
        resolve()
      }).catch(error => {
        reject(error)
      })
    })
  }

  function getUserInfoAction() {
    return new Promise((resolve, reject) => {
      getUserInfo().then(res => {
        userInfo.value = res // 假设返回的是 userInfo 对象
        resolve(res)
      }).catch(error => {
        reject(error)
      })
    })
  }

  function logoutAction() {
    return new Promise((resolve) => {
      // 如果后端有 logout 接口，可以调用
      // logout().then(...)
      
      token.value = ''
      userInfo.value = {}
      removeToken()
      resolve()
    })
  }

  return { 
    token, 
    userInfo, 
    login: loginAction, 
    getUserInfo: getUserInfoAction, 
    logout: logoutAction 
  }
})
