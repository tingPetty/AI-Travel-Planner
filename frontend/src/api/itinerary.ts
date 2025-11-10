/**
 * 行程相关API服务
 */

import { request } from './request'

// 行程生成请求接口
export interface ItineraryGenerateRequest {
  destination: string
  start_date: string
  end_date: string
  budget?: number
  preferences?: string
  travelers?: number
  travel_style?: string
  title?: string
}

// 活动模型
export interface Activity {
  time: string
  activity: string
  location: string
  duration: string
  cost: number
  type?: string
  description?: string
}

// 单日行程模型
export interface DayItinerary {
  date: string
  activities: Activity[]
}

// 行程响应接口
export interface ItineraryResponse {
  id: number
  user_id: number
  title: string
  destination: string
  start_date: string
  end_date: string
  budget?: number
  travelers?: number
  status: string
  itinerary?: Record<string, DayItinerary>
  created_at: string
  updated_at: string
}

// 行程列表响应接口
export interface ItineraryListResponse {
  id: number
  title: string
  destination: string
  start_date: string
  end_date: string
  travelers?: number
  status: string
  created_at: string
  budget: number
  
}

// 生成行程响应接口
export interface GenerateItineraryResponse {
  success: boolean
  message: string
  data?: ItineraryResponse
}

// API响应接口
export interface APIResponse {
  success: boolean
  message: string
  data?: any
}

/**
 * 生成行程规划
 */
export const generateItinerary = async (data: ItineraryGenerateRequest): Promise<GenerateItineraryResponse> => {
  return request.post('/api/itinerary/generate', data)
}

/**
 * 获取行程列表
 */
export const getItineraryList = async (): Promise<ItineraryListResponse[]> => {
  return request.get('/api/itinerary/list')
}

/**
 * 获取单个行程详情
 */
export const getItinerary = async (id: number): Promise<ItineraryResponse> => {
  return request.get(`/api/itinerary/${id}`)
}

/**
 * 更新行程
 */
export const updateItinerary = async (id: number, data: ItineraryGenerateRequest): Promise<APIResponse> => {
  return request.put(`/api/itinerary/${id}`, data)
}

/**
 * 删除行程
 */
export const deleteItinerary = async (id: number): Promise<APIResponse> => {
  return request.delete(`/api/itinerary/${id}`)
}

/**
 * 根据ID获取行程详情（用于编辑页面）
 */
export const getTripById = async (id: string): Promise<any> => {
  return request.get(`/api/itinerary/${id}`)
}

/**
 * 更新行程信息（用于编辑页面）
 */
export const updateTrip = async (id: string, data: any): Promise<APIResponse> => {
  return request.put(`/api/itinerary/${id}`, data)
}