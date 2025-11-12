<template>
  <div class="about">
    <div class="container">
      <!-- 页面标题 -->
      <div class="header-section">
        <el-card class="title-card" shadow="hover">
          <div class="title-content">
            <el-icon class="title-icon" size="48"><Location /></el-icon>
            <h1>关于 AI 旅行规划助手</h1>
            <p class="subtitle">让人工智能为您规划完美的旅行体验</p>
          </div>
        </el-card>
      </div>

      <!-- 项目介绍 -->
      <div class="intro-section">
        <el-row :gutter="24">
          <el-col :xs="24" :md="12">
            <el-card class="info-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <el-icon><InfoFilled /></el-icon>
                  <span>项目简介</span>
                </div>
              </template>
              <p>基于阿里云大模型的智能旅行规划系统，支持语音交互、自然语言理解和个性化行程推荐。通过先进的AI技术，为用户提供便捷、智能的旅行规划服务。</p>
            </el-card>
          </el-col>
          
          <el-col :xs="24" :md="12">
            <el-card class="info-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <el-icon><Star /></el-icon>
                  <span>核心功能</span>
                </div>
              </template>
              <div class="tags-grid">
                <el-tag type="success" size="large" class="feature-tag">智能行程规划</el-tag>
                <el-tag type="success" size="large" class="feature-tag">语音识别输入</el-tag>
                <el-tag type="success" size="large" class="feature-tag">地图可视化</el-tag>
                <el-tag type="success" size="large" class="feature-tag">费用管理和分析</el-tag>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 技术栈 -->
      <div class="tech-section">
        <el-card class="tech-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Setting /></el-icon>
              <span>技术架构</span>
            </div>
          </template>
          <el-row :gutter="16">
            <el-col :xs="12" :sm="6">
              <div class="tech-item">
                <el-icon class="tech-icon"><Monitor /></el-icon>
                <h4>前端</h4>
                <p>Vue 3 + TypeScript</p>
              </div>
            </el-col>
            <el-col :xs="12" :sm="6">
              <div class="tech-item">
                <el-icon class="tech-icon"><DataBoard /></el-icon>
                <h4>后端</h4>
                <p>FastAPI + SQLite</p>
              </div>
            </el-col>
            <el-col :xs="12" :sm="6">
              <div class="tech-item">
                <el-icon class="tech-icon"><ChatDotRound /></el-icon>
                <h4>AI服务</h4>
                <p>阿里云通义千问</p>
              </div>
            </el-col>
            <el-col :xs="12" :sm="6">
              <div class="tech-item">
                <el-icon class="tech-icon"><MapLocation /></el-icon>
                <h4>地图</h4>
                <p>高德地图API</p>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </div>

      <!-- 联系信息 -->
      <div class="contact-section">
        <el-card class="contact-card" shadow="hover">
          <div class="contact-content">
            <el-icon class="contact-icon"><Link /></el-icon>
            <h3>开源项目</h3>
            <p>欢迎访问我们的 GitHub 仓库了解更多信息</p>
            <el-button type="success" size="large" @click="openGithub">
              <el-icon><Link /></el-icon>
              访问 GitHub
            </el-button>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const openGithub = () => {
  window.open('https://github.com/tingPetty/AI-Travel-Planner', '_blank')
}
</script>

<style scoped>
.about {
  min-height: calc(100vh - 60px);
  background: linear-gradient(135deg, #f0f9f0 0%, #e8f5e8 100%);
  padding: 40px 20px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

/* 标题区域 */
.header-section {
  margin-bottom: 40px;
}

.title-card {
  background: linear-gradient(135deg, #8fbc8f 0%, #7a9d7a 100%);
  border: none;
  border-radius: 20px;
}

.title-card :deep(.el-card__body) {
  padding: 60px 40px;
}

.title-content {
  text-align: center;
  color: white;
}

.title-icon {
  color: #ffd700;
  margin-bottom: 20px;
}

.title-content h1 {
  font-size: 2.5rem;
  font-weight: 600;
  margin: 0 0 16px 0;
}

.subtitle {
  font-size: 1.2rem;
  opacity: 0.9;
  margin: 0;
}

/* 介绍区域 */
.intro-section {
  margin-bottom: 40px;
}

.info-card {
  height: 100%;
  border-radius: 16px;
  border: 2px solid #e8f5e8;
  transition: all 0.3s ease;
}

.info-card:hover {
  border-color: #8fbc8f;
  transform: translateY(-5px);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #4f7942;
}

.info-card p {
  line-height: 1.8;
  color: #606266;
  margin: 0;
}

/* 功能标签网格布局 */
.tags-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.feature-tag {
  width: 100%;
  text-align: center;
  justify-content: center;
  padding: 8px 12px;
}

/* 技术栈区域 */
.tech-section {
  margin-bottom: 40px;
}

.tech-card {
  border-radius: 16px;
  border: 2px solid #e8f5e8;
}

.tech-item {
  text-align: center;
  padding: 20px 10px;
  border-radius: 12px;
  background: #f8f9fa;
  transition: all 0.3s ease;
}

.tech-item:hover {
  background: #e8f5e8;
  transform: translateY(-3px);
}

.tech-icon {
  font-size: 32px;
  color: #8fbc8f;
  margin-bottom: 12px;
}

.tech-item h4 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.tech-item p {
  font-size: 0.9rem;
  color: #606266;
  margin: 0;
}

/* 联系区域 */
.contact-section {
  margin-bottom: 20px;
}

.contact-card {
  border-radius: 16px;
  border: 2px solid #e8f5e8;
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
}

.contact-content {
  text-align: center;
  padding: 20px;
}

.contact-icon {
  font-size: 48px;
  color: #8fbc8f;
  margin-bottom: 16px;
}

.contact-content h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #303133;
  margin: 0 0 12px 0;
}

.contact-content p {
  color: #606266;
  margin: 0 0 24px 0;
  line-height: 1.6;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .about {
    padding: 20px 15px;
  }
  
  .title-content h1 {
    font-size: 2rem;
  }
  
  .subtitle {
    font-size: 1rem;
  }
  
  .title-card :deep(.el-card__body) {
    padding: 40px 20px;
  }
  
  .intro-section .el-col {
    margin-bottom: 20px;
  }
  
  .tags-grid {
    grid-template-columns: 1fr;
    gap: 8px;
  }
}

@media (max-width: 480px) {
  .title-content h1 {
    font-size: 1.8rem;
  }
  
  .tech-item {
    padding: 15px 8px;
  }
  
  .tech-icon {
    font-size: 24px;
  }
}
</style>
