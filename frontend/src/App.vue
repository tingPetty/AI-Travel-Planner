<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

const message = ref('Hello World! AI旅行规划助手前端测试成功！')
const currentTime = ref(new Date().toLocaleString())
const apiStatus = ref('检测中...')
const apiData = ref<any>(null)
const testMessage = ref('')
const echoResult = ref('')

// API基础地址
const API_BASE_URL = 'http://localhost:8000'

// 测试后端连接
const testBackendConnection = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/`)
    apiStatus.value = '✅ 连接成功'
    apiData.value = response.data
  } catch (error) {
    apiStatus.value = '❌ 连接失败'
    console.error('Backend connection failed:', error)
  }
}

// 测试API接口
const testAPI = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/test`)
    console.log('API Test Response:', response.data)
  } catch (error) {
    console.error('API test failed:', error)
  }
}

// 测试回声接口
const testEcho = async () => {
  if (!testMessage.value.trim()) {
    echoResult.value = '请输入测试消息'
    return
  }
  
  try {
    const response = await axios.get(`${API_BASE_URL}/api/test/echo/${encodeURIComponent(testMessage.value)}`)
    echoResult.value = response.data.echo
  } catch (error) {
    echoResult.value = '回声测试失败'
    console.error('Echo test failed:', error)
  }
}

onMounted(() => {
  testBackendConnection()
})
</script>

<template>
  <div class="app">
    <header class="header">
      <h1>🌍 AI旅行规划助手</h1>
      <p class="subtitle">前端 Hello World 测试</p>
    </header>
    
    <main class="main">
      <div class="card">
        <h2>{{ message }}</h2>
        <p>当前时间: {{ currentTime }}</p>
        <div class="status">
          <span class="status-item">✅ Vue 3</span>
          <span class="status-item">✅ TypeScript</span>
          <span class="status-item">✅ Vite</span>
          <span class="status-item">✅ 开发服务器</span>
        </div>
      </div>

      <div class="card">
        <h3>🔗 前后端连通性测试</h3>
        <div class="api-test">
          <p><strong>后端状态:</strong> {{ apiStatus }}</p>
          <div v-if="apiData" class="api-info">
            <p><strong>API信息:</strong> {{ apiData.message }}</p>
            <p><strong>版本:</strong> {{ apiData.version }}</p>
            <p><strong>描述:</strong> {{ apiData.description }}</p>
          </div>
          
          <div class="test-section">
            <h4>回声测试</h4>
            <div class="input-group">
              <input 
                v-model="testMessage" 
                type="text" 
                placeholder="输入测试消息"
                @keyup.enter="testEcho"
              />
              <button @click="testEcho" class="test-btn">发送</button>
            </div>
            <p v-if="echoResult" class="echo-result">{{ echoResult }}</p>
          </div>
          
          <button @click="testAPI" class="test-btn">测试API接口</button>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.header {
  text-align: center;
  color: white;
  margin-bottom: 2rem;
}

.header h1 {
  font-size: 3rem;
  margin: 0;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.subtitle {
  font-size: 1.2rem;
  margin: 0.5rem 0 0 0;
  opacity: 0.9;
}

.main {
  width: 100%;
  max-width: 600px;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.card {
  background: white;
  border-radius: 15px;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
  text-align: center;
}

.card h2 {
  color: #333;
  margin: 0 0 1rem 0;
  font-size: 1.5rem;
}

.card h3 {
  color: #333;
  margin: 0 0 1rem 0;
  font-size: 1.3rem;
}

.card h4 {
  color: #555;
  margin: 1rem 0 0.5rem 0;
  font-size: 1.1rem;
}

.card p {
  color: #666;
  margin: 1rem 0;
  font-size: 1.1rem;
}

.status {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
  margin-top: 1.5rem;
}

.status-item {
  background: #4CAF50;
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
}

.api-test {
  text-align: left;
}

.api-info {
  background: #f5f5f5;
  padding: 1rem;
  border-radius: 8px;
  margin: 1rem 0;
}

.test-section {
  margin: 1.5rem 0;
}

.input-group {
  display: flex;
  gap: 10px;
  margin: 0.5rem 0;
}

.input-group input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1rem;
}

.test-btn {
  background: #2196F3;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s;
}

.test-btn:hover {
  background: #1976D2;
}

.echo-result {
  background: #e8f5e8;
  padding: 10px;
  border-radius: 5px;
  margin-top: 10px;
  color: #2e7d32;
  font-weight: 500;
}

@media (max-width: 768px) {
  .header h1 {
    font-size: 2rem;
  }
  
  .card {
    padding: 1.5rem;
  }
  
  .status {
    flex-direction: column;
    align-items: center;
  }
}
</style>
