import { defineStore } from 'pinia';
import { authApi } from '@/api/auth';
import type { UserInfo, UserUpdateParams } from '@/api/types';

export const useUserStore = defineStore('user', {
  state: () => ({
    token: uni.getStorageSync('token') || '',
    userInfo: (uni.getStorageSync('userInfo') ? JSON.parse(uni.getStorageSync('userInfo')) : null) as UserInfo | null,
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
  },
  actions: {
    async login() {
      return new Promise((resolve, reject) => {
        // 1. Get Wechat Code
        uni.login({
          provider: 'weixin',
          success: async (loginRes) => {
            if (loginRes.code) {
              try {
                // 2. Call Backend Login API
                const res = await authApi.login({ code: loginRes.code });
                
                // 3. Save Token & UserInfo
                this.token = res.token;
                this.userInfo = res.userInfo;
                
                uni.setStorageSync('token', res.token);
                uni.setStorageSync('userInfo', JSON.stringify(res.userInfo));
                
                console.log('Login success:', this.userInfo);
                resolve(res);
              } catch (error) {
                console.error('Login failed:', error);
                reject(error);
              }
            } else {
              console.error('uni.login failed:', loginRes.errMsg);
              reject(loginRes.errMsg);
            }
          },
          fail: (err) => {
            console.error('uni.login call failed:', err);
            reject(err);
          },
        });
      });
    },
    
    async updateUserInfo(data: UserUpdateParams) {
      try {
        const res = await authApi.updateProfile(data);
        this.userInfo = { ...this.userInfo, ...res };
        uni.setStorageSync('userInfo', JSON.stringify(this.userInfo));
        return res;
      } catch (error) {
        console.error('Update profile failed:', error);
        throw error;
      }
    },

    logout() {
      this.token = '';
      this.userInfo = null;
      uni.removeStorageSync('token');
      uni.removeStorageSync('userInfo');
    },
  },
});
