/**
 * 运行时配置工具
 * 优先使用运行时配置（从 window.__APP_CONFIG__），如果不存在则使用构建时配置
 */

interface AppConfig {
  VITE_AMAP_KEY?: string
  VITE_API_BASE_URL?: string
}

declare global {
  interface Window {
    __APP_CONFIG__?: AppConfig
  }
}

/**
 * 获取高德地图 API Key
 * 优先级：运行时配置 > 构建时配置
 */
export function getAmapKey(): string {
  // 优先使用运行时配置
  const runtimeKey = window.__APP_CONFIG__?.VITE_AMAP_KEY
  if (runtimeKey && runtimeKey !== 'PLACEHOLDER_VITE_AMAP_KEY') {
    return runtimeKey
  }
  
  // 回退到构建时配置
  return import.meta.env.VITE_AMAP_KEY || ''
}

/**
 * 获取 API 基础 URL
 * 优先级：运行时配置 > 构建时配置
 */
export function getApiBaseUrl(): string {
  // 优先使用运行时配置
  const runtimeUrl = window.__APP_CONFIG__?.VITE_API_BASE_URL
  if (runtimeUrl && runtimeUrl !== 'PLACEHOLDER_VITE_API_BASE_URL') {
    return runtimeUrl
  }
  
  // 回退到构建时配置
  return import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
}
