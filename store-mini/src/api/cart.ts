import { request } from '@/utils/request';
import type { CartListResponse, AddToCartParams, UpdateCartParams } from './types';

export const cartApi = {
  list: () => {
    return request<CartListResponse>({
      url: '/cart/list',
      method: 'GET',
    });
  },
  add: (data: AddToCartParams) => {
    return request({
      url: '/cart/add',
      method: 'POST',
      data,
    });
  },
  update: (data: UpdateCartParams & { id: number }) => {
    return request({
      url: '/cart/update',
      method: 'PUT',
      data,
    });
  },
  delete: (ids: number[]) => {
    return request({
      url: '/cart/delete',
      method: 'DELETE',
      data: { ids },
    });
  },
};
