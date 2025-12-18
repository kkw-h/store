<template>
  <el-aside class="sidebar-container" :width="variables.sidebarWidth">
    <div class="logo">
      <el-icon class="logo-icon"><Shop /></el-icon>
      <span v-if="!isCollapse">商家后台管理</span>
    </div>
    <el-menu
      :default-active="activeMenu"
      class="el-menu-vertical"
      :background-color="variables.sidebarBg"
      :text-color="variables.sidebarText"
      :active-text-color="variables.sidebarActiveText"
      :collapse="isCollapse"
      router
    >
      <template v-for="route in routes" :key="route.path">
        <!-- Single Item -->
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

        <!-- Sub Menu -->
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
import { Shop } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const isCollapse = false // TODO: support collapse state from store

// CSS Variables from SCSS
const variables = {
  sidebarBg: '#304156',
  sidebarText: '#bfcbd9',
  sidebarActiveText: '#409eff',
  sidebarWidth: '220px'
}

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

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.sidebar-container {
  background-color: $sidebar-bg;
  height: 100%;
  overflow-x: hidden;
  transition: width $transition-duration;
  box-shadow: 2px 0 6px rgba(0, 21, 41, 0.35);
  z-index: 1001;
  
  &::-webkit-scrollbar {
    display: none;
  }
}

.logo {
  height: $sidebar-logo-height;
  line-height: $sidebar-logo-height;
  text-align: center;
  color: #fff;
  font-weight: 600;
  font-size: 18px;
  background-color: #2b2f3a;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  
  .logo-icon {
    font-size: 24px;
    color: $color-primary;
  }
}

.el-menu-vertical {
  border-right: none;
  
  :deep(.el-menu-item) {
    &.is-active {
      background-color: #263445 !important;
      border-right: 3px solid $color-primary;
    }
    
    &:hover {
      background-color: #263445 !important;
    }
  }
  
  :deep(.el-sub-menu__title) {
    &:hover {
      background-color: #263445 !important;
    }
  }
}
</style>
