import request from '@/utils/request'

// 获取店铺配置
export function getShopConfig() {
  return request({
    url: '/api/v1/admin/shop/config',
    method: 'get'
  })
}

// 更新店铺配置
export function updateShopConfig(data) {
  return request({
    url: '/api/v1/admin/shop/config',
    method: 'post',
    data
  })
}
