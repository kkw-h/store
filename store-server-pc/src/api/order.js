import request from '@/utils/request'

// 获取订单列表
export function getOrderList(params) {
  return request({
    url: '/api/v1/admin/order/list',
    method: 'get',
    params
  })
}

// 获取订单详情
export function getOrderDetail(order_id) {
  return request({
    url: '/api/v1/admin/order/detail',
    method: 'get',
    params: { order_id }
  })
}

// 审核订单 (接单/拒单)
export function auditOrder(data) {
  return request({
    url: '/api/v1/admin/order/audit',
    method: 'post',
    data
  })
}

// 确认送达
export function completeDelivery(data) {
  return request({
    url: '/api/v1/admin/order/complete_delivery',
    method: 'post',
    data
  })
}

// 核销自提码
export function verifyPickup(data) {
  return request({
    url: '/api/v1/admin/order/verify',
    method: 'post',
    data
  })
}
