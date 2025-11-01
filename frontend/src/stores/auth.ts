import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

// 用户信息接口
export interface User {
  id: number
  username: string
  email: string
  preferences?: Record<string, any>
  created_at: string
}

// 注册数据接口
export interface RegisterData {
  username: string
  email: string
  password: string
  preferences?: Record<string, any>
}

// API响应接口
interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

// API基础URL
const API_BASE_URL = 'http://localhost:8000/api'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const isLoading = ref(false)

  // 计算属性
  const isAuthenticated = computed(() => !!token.value && !!user.value)

  // 设置认证头
  const setAuthHeader = (authToken: string) => {
    axios.defaults.headers.common['Authorization'] = `Bearer ${authToken}`
  }

  // 清除认证头
  const clearAuthHeader = () => {
    delete axios.defaults.headers.common['Authorization']
  }

  // 保存认证信息
  const saveAuthData = (authData: AuthResponse) => {
    token.value = authData.access_token
    user.value = authData.user
    localStorage.setItem('token', authData.access_token)
    localStorage.setItem('user', JSON.stringify(authData.user))
    setAuthHeader(authData.access_token)
  }

  // 清除认证信息
  const clearAuthData = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    clearAuthHeader()
  }

  // 初始化认证状态
  const initAuth = () => {
    const savedToken = localStorage.getItem('token')
    const savedUser = localStorage.getItem('user')
    
    if (savedToken && savedUser) {
      try {
        token.value = savedToken
        user.value = JSON.parse(savedUser)
        setAuthHeader(savedToken)
      } catch (error) {
        console.error('Failed to parse saved user data:', error)
        clearAuthData()
      }
    }
  }

  // 用户注册
  const register = async (registerData: RegisterData): Promise<void> => {
    isLoading.value = true
    try {
      const response = await axios.post<AuthResponse>(
        `${API_BASE_URL}/auth/register`,
        registerData
      )
      saveAuthData(response.data)
    } catch (error: any) {
      const message = error.response?.data?.detail || '注册失败'
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  // 用户登录
  const login = async (email: string, password: string): Promise<void> => {
    isLoading.value = true
    try {
      const response = await axios.post<AuthResponse>(
        `${API_BASE_URL}/auth/login`,
        { email, password }
      )
      saveAuthData(response.data)
    } catch (error: any) {
      const message = error.response?.data?.detail || '登录失败'
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  // 用户登出
  const logout = async (): Promise<void> => {
    try {
      // 调用后端登出接口（可选）
      await axios.post(`${API_BASE_URL}/auth/logout`)
    } catch (error) {
      console.error('Logout API call failed:', error)
    } finally {
      clearAuthData()
    }
  }

  // 获取当前用户信息
  const getCurrentUser = async (): Promise<void> => {
    if (!token.value) return
    
    try {
      const response = await axios.get<User>(`${API_BASE_URL}/auth/me`)
      user.value = response.data
      localStorage.setItem('user', JSON.stringify(response.data))
    } catch (error) {
      console.error('Failed to get current user:', error)
      clearAuthData()
    }
  }

  // 检查token有效性
  const checkTokenValidity = async (): Promise<boolean> => {
    if (!token.value) return false
    
    try {
      await getCurrentUser()
      return true
    } catch (error) {
      clearAuthData()
      return false
    }
  }

  return {
    // 状态
    user,
    token,
    isLoading,
    
    // 计算属性
    isAuthenticated,
    
    // 方法
    initAuth,
    register,
    login,
    logout,
    getCurrentUser,
    checkTokenValidity
  }
})