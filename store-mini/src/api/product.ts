import { request } from '@/utils/request';
import type { ProductListParams, ProductListResponse, Product } from './types';

export const productApi = {
  list: (params: ProductListParams) => {
    return request<ProductListResponse>({
      url: '/product/list',
      method: 'GET',
      data: params,
    });
  },
  detail: (id: number) => {
    return request<Product>({
      url: `/product/${id}`,
      method: 'GET',
    });
  },
};
