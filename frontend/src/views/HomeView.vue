<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const isAuthenticated = computed(() => authStore.isAuthenticated)
const user = computed(() => authStore.user)
</script>

<template>
  <div class="home">
    <!-- 欢迎横幅 -->
    <div class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">
          <el-icon class="hero-icon"><Location /></el-icon>
          AI旅行规划师
        </h1>
        <p class="hero-subtitle">
          让人工智能为您规划完美的旅行体验
        </p>
        <div class="hero-description">
          <p>智能推荐 • 个性化定制 • 实时更新</p>
        </div>
        
        <div class="hero-actions" v-if="!isAuthenticated">
          <router-link to="/register">
            <el-button type="primary" size="large" color="#4f7942">
              开始规划旅行
            </el-button>
          </router-link>
          <router-link to="/login">
            <el-button size="large" plain color="#4f7942">
              已有账号登录
            </el-button>
          </router-link>
        </div>
        
        <div class="welcome-back" v-else>
          <h2>欢迎回来，{{ user?.username }}！</h2>
          <p>准备好开始您的下一次旅行了吗？</p>
          <router-link to="/dashboard">
            <el-button type="primary" size="large" color="#4f7942">
              进入我的行程
            </el-button>
          </router-link>
        </div>
      </div>
    </div>
    
    <!-- 功能特色 -->
    <div class="features-section">
      <div class="container">
        <h2 class="section-title">为什么选择AI旅行规划师？</h2>
        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon">
              <el-icon><Compass /></el-icon>
            </div>
            <h3>智能推荐</h3>
            <p>基于您的偏好和历史数据，AI为您推荐最适合的目的地和活动</p>
          </div>
          
          <div class="feature-card">
            <div class="feature-icon">
              <el-icon><User /></el-icon>
            </div>
            <h3>个性化定制</h3>
            <p>根据您的兴趣、预算和时间，量身定制专属的旅行方案</p>
          </div>
          
          <div class="feature-card">
            <div class="feature-icon">
              <el-icon><Clock /></el-icon>
            </div>
            <h3>实时更新</h3>
            <p>获取最新的天气、交通和景点信息，确保您的旅行顺利进行</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 使用步骤 -->
    <div class="steps-section">
      <div class="container">
        <h2 class="section-title">三步开启您的智能旅行</h2>
        <div class="steps-grid">
          <div class="step-item">
            <div class="step-number">1</div>
            <h3>注册账号</h3>
            <p>创建您的专属账号，开始个性化旅行规划</p>
          </div>
          
          <div class="step-item">
            <div class="step-number">2</div>
            <h3>设置偏好</h3>
            <p>告诉我们您的旅行偏好、预算和时间安排</p>
          </div>
          
          <div class="step-item">
            <div class="step-number">3</div>
            <h3>获取方案</h3>
            <p>AI为您生成详细的旅行计划，随时调整优化</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home {
  min-height: calc(100vh - 60px);
  padding: 20px;
}

/* 英雄区域 */
.hero-section {
  background: 
    linear-gradient(135deg, rgba(143, 188, 143, 0.8) 0%, rgba(122, 157, 122, 0.8) 100%),
    url('/pictures/naturepic1.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  color: white;
  padding: 80px 20px;
  text-align: center;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.hero-icon {
  font-size: 4rem;
  color: #ffd700;
}

.hero-subtitle {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  opacity: 0.9;
}

.hero-description {
  font-size: 1.1rem;
  margin-bottom: 2.5rem;
  opacity: 0.8;
}

.hero-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

.welcome-back {
  background: rgba(255, 255, 255, 0.1);
  padding: 2rem;
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.welcome-back h2 {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.welcome-back p {
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
  opacity: 0.9;
}

/* 容器 */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 功能特色区域 */
.features-section {
  padding: 80px 0;
  background: white;
}

.section-title {
  text-align: center;
  font-size: 2.5rem;
  font-weight: 600;
  color: #303133;
  margin-bottom: 3rem;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.feature-card {
  text-align: center;
  padding: 2rem;
  border-radius: 12px;
  background: #f8f9fa;
  transition: transform 0.3s, box-shadow 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #8fbc8f 0%, #7a9d7a 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  font-size: 32px;
  color: white;
}

.feature-card h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #303133;
  margin-bottom: 1rem;
}

.feature-card p {
  color: #606266;
  line-height: 1.6;
}

/* 使用步骤区域 */
.steps-section {
  padding: 80px 0;
  background: #f5f7fa;
}

.steps-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.step-item {
  text-align: center;
  padding: 2rem;
}

.step-number {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #8fbc8f 0%, #7a9d7a 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0 auto 1.5rem;
}

.step-item h3 {
  font-size: 1.3rem;
  font-weight: 600;
  color: #303133;
  margin-bottom: 1rem;
}

.step-item p {
  color: #606266;
  line-height: 1.6;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
    flex-direction: column;
    gap: 8px;
  }
  
  .hero-icon {
    font-size: 3rem;
  }
  
  .hero-subtitle {
    font-size: 1.2rem;
  }
  
  .hero-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .section-title {
    font-size: 2rem;
  }
  
  .features-grid,
  .steps-grid {
    grid-template-columns: 1fr;
  }
  
  .welcome-back {
    padding: 1.5rem;
  }
  
  .welcome-back h2 {
    font-size: 1.5rem;
    font-weight: bold;
  }
}

@media (max-width: 480px) {
  .hero-section {
    padding: 60px 15px;
  }
  
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
  
  .features-section,
  .steps-section {
    padding: 60px 0;
  }
  
  .feature-card,
  .step-item {
    padding: 1.5rem;
  }
}
</style>
