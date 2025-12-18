import { request } from '@/utils/request';
import type { LoginParams, LoginResponse, UserUpdateParams, UserInfo } from './types';

export const authApi = {
  login: (data: LoginParams) => {
    return request<LoginResponse>({
      url: '/auth/login',
      method: 'POST',
      data,
    });
  },
  
  updateProfile: (data: UserUpdateParams) => {
    return request<UserInfo>({
      url: '/auth/profile',
      method: 'PUT',
      data,
    });
  }
};
