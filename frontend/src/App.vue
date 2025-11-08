<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const isAuthenticated = computed(() => authStore.isAuthenticated)
const user = computed(() => authStore.user)

const handleLogin = () => {
  router.push('/login')
}

const handleRegister = () => {
  router.push('/register')
}

const handleLogout = async () => {
  try {
    await authStore.logout()
    ElMessage.success('退出登录成功')
    router.push('/')
  } catch (error) {
    ElMessage.error('退出登录失败')
  }
}
</script>

<template>
  <div class="app">
    <!-- 导航栏 -->
    <el-header class="header">
      <div class="header-content">
        <div class="logo">
          <router-link to="/" class="logo-link">
            <el-icon class="logo-icon"><Location /></el-icon>
            <span class="logo-text">AI旅行规划师</span>
          </router-link>
        </div>
        
        <nav class="nav">
          <router-link to="/" class="nav-link">首页</router-link>
          <router-link v-if="isAuthenticated" to="/dashboard" class="nav-link">我的行程</router-link>
          <router-link to="/about" class="nav-link">关于</router-link>
        </nav>
        
        <div class="auth-section">
          <template v-if="!isAuthenticated">
            <el-button @click="handleLogin" type="primary" plain color="#4f7942">登录</el-button>
            <el-button @click="handleRegister" type="primary" color="#4f7942">注册</el-button>
          </template>
          <template v-else>
            <el-dropdown @command="handleLogout">
              <span class="user-info">
                <el-icon><User /></el-icon>
                {{ user?.username }}
                <el-icon class="el-icon--right"><arrow-down /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="logout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </div>
      </div>
    </el-header>
    
    <!-- 主要内容区域 -->
    <el-main class="main">
      <router-view />
    </el-main>
  </div>
</template>

<style scoped>
/* 全局重置和基础样式 */
* {
  box-sizing: border-box;
}

.app {
  min-height: 100vh;
  width: 100%;
  display: flex;
  flex-direction: column;
  margin: 0;
  padding: 0;
}

.header {
  background: white;
  border-bottom: 1px solid #edf2ed;
  box-shadow: 0 2px 12px 0 rgba(143, 188, 143, 0.08);
  height: 60px;
  padding: 0;
  width: 100%;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  width: 100%;
}

.logo {
  display: flex;
  align-items: center;
}

.logo-link {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: #8fbc8f;
  font-size: 20px;
  font-weight: 600;
}

.logo-icon {
  font-size: 24px;
  margin-right: 8px;
  color: #8fbc8f;
}

.logo-text {
  color: #6b8e6b;
}

.nav {
  display: flex;
  align-items: center;
  gap: 30px;
}

.nav-link {
  text-decoration: none;
  color: #606266;
  font-weight: 500;
  padding: 8px 16px;
  border-radius: 6px;
  transition: all 0.3s;
}

.nav-link:hover,
.nav-link.router-link-active {
  color: #8fbc8f;
  background-color: #f8faf8;
}

.auth-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 6px;
  transition: all 0.3s;
}

.user-info:hover {
  background-color: #f8faf8;
  color: #8fbc8f;
}

.main {
  flex: 1;
  background-color: #f8faf8;
  padding: 0;
  width: 100%;
  min-height: calc(100vh - 60px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    padding: 0 15px;
  }
  
  .nav {
    display: none;
  }
  
  .logo-text {
    font-size: 18px;
  }
  
  .auth-section {
    gap: 8px;
  }
  
  .auth-section .el-button {
    padding: 8px 12px;
    font-size: 14px;
  }
}

@media (max-width: 480px) {
  .header-content {
    padding: 0 10px;
  }
  
  .logo-text {
    display: none;
  }
  
  .auth-section .el-button span {
    display: none;
  }
  
  .auth-section .el-button {
    padding: 8px;
    min-width: auto;
  }
}
</style>
