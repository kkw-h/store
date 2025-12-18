import { request } from '@/utils/request';
import type { Category } from './types';

export const categoryApi = {
  list: () => {
    return request<Category[]>({
      url: '/category/list',
      method: 'GET',
    });
  },
};
