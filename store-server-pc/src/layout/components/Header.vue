<template>
  <div class="navbar">
    <div class="left-menu">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item v-for="(item, index) in matched" :key="index">
          {{ item.meta.title }}
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <div class="right-menu">
      <div class="right-menu-item hover-effect">
        <el-tooltip content="全屏" effect="dark" placement="bottom">
          <el-icon class="icon-btn"><FullScreen /></el-icon>
        </el-tooltip>
      </div>
      
      <el-dropdown class="avatar-container right-menu-item hover-effect" trigger="click" @command="handleCommand">
        <div class="avatar-wrapper">
          <el-avatar :size="30" class="user-avatar" :src="userStore.userInfo.avatar || 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'" />
          <span class="user-name">{{ userStore.userInfo.nickname || 'Admin' }}</span>
          <el-icon class="el-icon--right"><CaretBottom /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">个人中心</el-dropdown-item>
            <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { CaretBottom, FullScreen } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const matched = computed(() => route.matched.filter(item => item.meta && item.meta.title && item.meta.title !== '工作台'))

const handleCommand = (command) => {
  if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗?', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      userStore.logout().then(() => {
        router.push('/login')
        ElMessage.success('已退出登录')
      })
    })
  } else if (command === 'profile') {
    router.push('/shop') // Redirect to shop/profile settings for now
  }
}
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.navbar {
  height: $header-height;
  overflow: hidden;
  position: relative;
  background: $header-bg;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  z-index: 1000;
}

.left-menu {
  display: flex;
  align-items: center;
}

.right-menu {
  display: flex;
  align-items: center;
  height: 100%;
  
  .right-menu-item {
    display: flex;
    align-items: center;
    padding: 0 8px;
    height: 100%;
    font-size: 18px;
    color: #5a5e66;
    vertical-align: text-bottom;
    cursor: pointer;
    transition: background .3s;
    
    &:hover {
      background: rgba(0, 0, 0, .025);
    }
  }
}

.avatar-container {
  margin-right: 30px;
  
  .avatar-wrapper {
    display: flex;
    align-items: center;
    position: relative;
    
    .user-avatar {
      cursor: pointer;
      margin-right: 8px;
    }
    
    .user-name {
      font-size: 14px;
      color: #333;
      margin-right: 4px;
    }
    
    .el-icon--right {
      font-size: 12px;
    }
  }
}

.icon-btn {
  font-size: 20px;
  cursor: pointer;
}
</style>
