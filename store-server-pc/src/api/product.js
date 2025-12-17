import request from '@/utils/request'

// --- Category ---

export function getCategoryList() {
  return request({
    url: '/api/v1/admin/category/list',
    method: 'get'
  })
}

export function createCategory(data) {
  return request({
    url: '/api/v1/admin/category/create',
    method: 'post',
    data
  })
}

export function updateCategory(id, data) {
  return request({
    url: '/api/v1/admin/category/update',
    method: 'post',
    params: { id },
    data
  })
}

export function deleteCategory(id) {
  return request({
    url: '/api/v1/admin/category/delete',
    method: 'post',
    params: { id }
  })
}

// --- Product ---

export function getProductList(params) {
  return request({
    url: '/api/v1/admin/product/list',
    method: 'get',
    params
  })
}

export function getProductDetail(id) {
  // Admin doesn't have a specific detail endpoint in admin.py?
  // Wait, I saw `read_product` in product.py but not in admin.py.
  // The admin.py only had list, save, delete, status, stock.
  // But usually save needs to load data first.
  // The product.py `read_product` is public? No, usually public is for users.
  // Let's check api.py again. `product.router` is mapped to `/product`.
  // `admin.router` is mapped to `/admin`.
  // If `product.router` has `read_product`, it is accessible at `/api/v1/product/{id}`.
  // Is it protected? `read_product` in `product.py` uses `deps.get_db` but no user dependency?
  // Wait, `product.py` `read_product` signature:
  // async def read_product(product_id: int, session: AsyncSession = Depends(deps.get_db)) -> Any
  // It seems public. So I can use it for admin too.
  return request({
    url: `/api/v1/product/${id}`,
    method: 'get'
  })
}

export function saveProduct(data, id) {
  return request({
    url: '/api/v1/admin/product/save',
    method: 'post',
    params: id ? { id } : undefined,
    data
  })
}

export function deleteProduct(id) {
  return request({
    url: '/api/v1/admin/product/delete',
    method: 'post',
    params: { id }
  })
}

export function updateProductStatus(id, status) {
  return request({
    url: '/api/v1/admin/product/status',
    method: 'post',
    params: { id, status }
  })
}
