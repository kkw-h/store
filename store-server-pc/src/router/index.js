import { createRouter, createWebHistory } from 'vue-router'
import { getToken } from '@/utils/auth'
import Layout from '@/layout/index.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/login/index.vue'),
      meta: { hidden: true }
    },
    {
      path: '/',
      component: Layout,
      redirect: '/dashboard',
      children: [
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: () => import('@/views/dashboard/index.vue'),
          meta: { title: '工作台', icon: 'DataBoard' }
        }
      ]
    },
    {
      path: '/product',
      component: Layout,
      redirect: '/product/list',
      name: 'Product',
      meta: { title: '商品管理', icon: 'Goods' },
      children: [
        {
          path: 'category',
          name: 'CategoryList',
          component: () => import('@/views/product/category.vue'),
          meta: { title: '分类管理', icon: 'Operation' }
        },
        {
          path: 'list',
          name: 'ProductList',
          component: () => import('@/views/product/index.vue'),
          meta: { title: '商品列表', icon: 'List' }
        },
        {
          path: 'add',
          name: 'ProductAdd',
          component: () => import('@/views/product/edit.vue'),
          meta: { title: '发布商品', hidden: true, activeMenu: '/product/list' }
        },
        {
          path: 'edit/:id',
          name: 'ProductEdit',
          component: () => import('@/views/product/edit.vue'),
          meta: { title: '编辑商品', hidden: true, activeMenu: '/product/list' }
        }
      ]
    },
    {
      path: '/order',
      component: Layout,
      redirect: '/order/list',
      name: 'Order',
      meta: { title: '订单管理', icon: 'List' },
      children: [
        {
          path: 'list',
          name: 'OrderList',
          component: () => import('@/views/order/index.vue'),
          meta: { title: '全部订单', icon: 'List' }
        },
        {
          path: 'detail/:id',
          name: 'OrderDetail',
          component: () => import('@/views/order/detail.vue'),
          meta: { title: '订单详情', hidden: true, activeMenu: '/order/list' }
        }
      ]
    },
    {
      path: '/user',
      component: Layout,
      redirect: '/user/list',
      name: 'User',
      meta: { title: '用户管理', icon: 'User' },
      children: [
        {
          path: 'list',
          name: 'UserList',
          component: () => import('@/views/user/index.vue'),
          meta: { title: '用户列表', icon: 'UserFilled' }
        }
      ]
    },
    {
      path: '/shop',
      component: Layout,
      redirect: '/shop/index',
      name: 'Shop',
      meta: { title: '店铺设置', icon: 'Setting' },
      children: [
        {
          path: 'index',
          name: 'ShopIndex',
          component: () => import('@/views/shop/index.vue'),
          meta: { title: '基础设置', icon: 'Setting' }
        }
      ]
    }
  ]
})

const whiteList = ['/login']

router.beforeEach(async (to, from, next) => {
  const hasToken = getToken()

  if (hasToken) {
    if (to.path === '/login') {
      next({ path: '/' })
    } else {
      next()
    }
  } else {
    if (whiteList.indexOf(to.path) !== -1) {
      next()
    } else {
      next(`/login?redirect=${to.path}`)
    }
  }
})

export default router
