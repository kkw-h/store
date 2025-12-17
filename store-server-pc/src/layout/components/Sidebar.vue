<template>
  <el-aside class="sidebar-container" width="220px">
    <div class="logo">
      <span>商家后台管理</span>
    </div>
    <el-menu
      :default-active="activeMenu"
      class="el-menu-vertical"
      background-color="#304156"
      text-color="#bfcbd9"
      active-text-color="#409EFF"
      :collapse="isCollapse"
      router
    >
      <template v-for="route in routes" :key="route.path">
        <!-- 单个菜单项 (没有子路由或只有一个子路由且不显示父级) -->
        <el-menu-item
          v-if="!route.meta?.hidden && !route.hidden && hasOneShowingChild(route.children, route)"
          :index="resolvePath(route.path, getTargetRoute(route).path)"
        >
          <el-icon v-if="getTargetRoute(route).meta && getTargetRoute(route).meta.icon">
            <component :is="getTargetRoute(route).meta.icon" />
          </el-icon>
          <template #title>
            <span>{{ getTargetRoute(route).meta.title }}</span>
          </template>
        </el-menu-item>

        <!-- 嵌套菜单 (有多个子路由) -->
        <el-sub-menu
          v-else-if="!route.meta?.hidden && !route.hidden"
          :index="route.path"
        >
          <template #title>
            <el-icon v-if="route.meta && route.meta.icon">
              <component :is="route.meta.icon" />
            </el-icon>
            <span>{{ route.meta.title }}</span>
          </template>
          
          <template v-for="child in route.children" :key="child.path">
            <el-menu-item
              v-if="!child.meta?.hidden && !child.hidden"
              :index="resolvePath(route.path, child.path)"
            >
              <el-icon v-if="child.meta && child.meta.icon">
                <component :is="child.meta.icon" />
              </el-icon>
              <template #title>
                <span>{{ child.meta.title }}</span>
              </template>
            </el-menu-item>
          </template>
        </el-sub-menu>
      </template>
    </el-menu>
  </el-aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const isCollapse = false // TODO: support collapse

const routes = computed(() => {
  return router.options.routes
})

const activeMenu = computed(() => {
  const { meta, path } = route
  if (meta.activeMenu) {
    return meta.activeMenu
  }
  return path
})

const hasOneShowingChild = (children = [], parent) => {
  const showingChildren = children.filter(item => {
    if (item.hidden) return false
    if (item.meta && item.meta.hidden) return false
    return true
  })
  
  if (showingChildren.length === 1) {
    return true
  }

  if (showingChildren.length === 0) {
    return true
  }

  return false
}

const getTargetRoute = (route) => {
  const children = route.children || []
  const showingChildren = children.filter(item => {
    if (item.hidden) return false
    if (item.meta && item.meta.hidden) return false
    return true
  })
  
  if (showingChildren.length === 1) {
    return showingChildren[0]
  }
  
  if (showingChildren.length === 0) {
    return { ...route, path: '', meta: route.meta || {} }
  }
  
  return null
}

const resolvePath = (basePath, routePath) => {
  if (!routePath) return basePath
  if (basePath === '/') return '/' + routePath
  return basePath + '/' + routePath
}
</script>

<style scoped>
.sidebar-container {
  background-color: #304156;
  height: 100%;
  overflow-x: hidden;
  transition: width 0.3s;
}

.logo {
  height: 50px;
  line-height: 50px;
  text-align: center;
  color: #fff;
  font-weight: bold;
  font-size: 16px;
  background-color: #2b2f3a;
  overflow: hidden;
}

.el-menu-vertical {
  border-right: none;
}
</style>
