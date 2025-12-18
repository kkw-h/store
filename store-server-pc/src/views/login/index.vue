<template>
  <div class="login-container">
    <div class="login-content">
      <div class="login-header">
        <div class="logo">
          <el-icon><Shop /></el-icon>
        </div>
        <h2 class="title">商家后台管理系统</h2>
        <p class="subtitle">专业的社区团购管理平台</p>
      </div>
      
      <el-card class="login-card">
        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          class="login-form"
          size="large"
          @keyup.enter="handleLogin"
        >
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="请输入用户名"
              prefix-icon="User"
            />
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              prefix-icon="Lock"
              show-password
            />
          </el-form-item>
          
          <div class="form-actions">
            <el-checkbox v-model="rememberMe">记住我</el-checkbox>
            <el-link type="primary" :underline="false">忘记密码？</el-link>
          </div>

          <el-form-item>
            <el-button
              :loading="loading"
              type="primary"
              class="login-button"
              @click="handleLogin"
            >
              登录
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
      
      <div class="login-footer">
        <p>© 2024 Store Server PC. All Rights Reserved.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { User, Lock, Shop } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const loginFormRef = ref(null)
const loading = ref(false)
const rememberMe = ref(true)

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules = {
  username: [{ required: true, trigger: 'blur', message: '请输入用户名' }],
  password: [{ required: true, trigger: 'blur', message: '请输入密码' }]
}

const handleLogin = () => {
  loginFormRef.value.validate((valid) => {
    if (valid) {
      loading.value = true
      userStore.login(loginForm)
        .then(() => {
          ElMessage.success('登录成功')
          router.push('/')
        })
        .catch((err) => {
          console.error(err)
        })
        .finally(() => {
          loading.value = false
        })
    }
  })
}
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.login-container {
  height: 100vh;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #2d3a4b;
  background-image: linear-gradient(135deg, #2d3a4b 0%, #1d2530 100%);
  overflow: hidden;
}

.login-content {
  width: 100%;
  max-width: 420px;
  padding: 20px;
  animation: fadeInDown 0.5s ease-out;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
  color: #fff;
  
  .logo {
    width: 60px;
    height: 60px;
    background: $color-primary;
    border-radius: 12px;
    margin: 0 auto 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 32px;
    box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
  }
  
  .title {
    margin: 0;
    font-size: 32px;
    font-weight: 600;
    letter-spacing: 2px;
  }
  
  .subtitle {
    margin-top: 10px;
    font-size: 14px;
    color: rgba(255, 255, 255, 0.6);
  }
}

.login-card {
  border-radius: 8px;
  border: none;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2) !important;
  background: rgba(255, 255, 255, 0.98);
  
  :deep(.el-card__body) {
    padding: 30px 40px;
  }
}

.login-form {
  .el-input {
    --el-input-height: 48px;
    
    :deep(.el-input__wrapper) {
      box-shadow: none;
      border: 1px solid $border-color-base;
      background-color: #f5f7fa;
      transition: all 0.3s;
      
      &.is-focus {
        border-color: $color-primary;
        background-color: #fff;
        box-shadow: 0 0 0 1px $color-primary;
      }
      
      &:hover {
        border-color: #c0c4cc;
      }
    }
  }
}

.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.login-button {
  width: 100%;
  height: 48px;
  font-size: 16px;
  letter-spacing: 4px;
  border-radius: 4px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
  transition: all 0.3s;
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(64, 158, 255, 0.5);
  }
}

.login-footer {
  margin-top: 40px;
  text-align: center;
  color: rgba(255, 255, 255, 0.3);
  font-size: 12px;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
