<template>
  <div class="map-container">
    <div id="amap-container" class="amap-container"></div>
    <div v-if="loading" class="map-loading">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>地图加载中...</span>
    </div>
    <div v-if="apiError" class="map-error">
      <el-alert
        :title="apiError.title"
        :description="apiError.description"
        type="error"
        :closable="false"
        show-icon
      />
    </div>
    <div v-if="parsingLocations" class="map-parsing">
      <el-alert
        :title="parsingStatus.title"
        :description="parsingStatus.description"
        type="info"
        :closable="false"
        show-icon
      >
        <template #default>
          <div class="parsing-content">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>{{ parsingStatus.description }}</span>
          </div>
        </template>
      </el-alert>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import AMapLoader from '@amap/amap-jsapi-loader'
import { Loading } from '@element-plus/icons-vue'

interface Activity {
  time?: string
  activity?: string
  location?: string
  duration?: string
  type?: string
  cost?: number
  description?: string
}

interface Props {
  activities: Activity[]
}

const props = defineProps<Props>()

const loading = ref(true)
const apiError = ref<{ title: string; description: string } | null>(null)
const parsingLocations = ref(false)
const parsingStatus = ref<{ title: string; description: string }>({
  title: '正在解析地点',
  description: '请稍候...',
})
let map: any = null
let markers: any[] = []
let AMapInstance: any = null

// 地点缓存，避免重复搜索相同地点
const locationCache = new Map<
  string,
  {
    location: { lng: number; lat: number }
    address: string
    name: string
    type: string
    tel: string
  }
>()

// 初始化地图
const initMap = async () => {
  try {
    console.log('[地图] 开始初始化高德地图...')
    console.log('[地图] 使用 Key:', import.meta.env.VITE_AMAP_KEY ? '已配置' : '未配置')

    AMapInstance = await AMapLoader.load({
      key: import.meta.env.VITE_AMAP_KEY,
      version: '2.0',
      plugins: [], // 不再需要 Geocoder 和 PlaceSearch 插件，改用 Web 服务 API
    })

    console.log('[地图] 高德地图 API 加载成功')

    // 创建地图实例
    map = new AMapInstance.Map('amap-container', {
      zoom: 13,
      center: [116.397428, 39.90923], // 默认中心点（北京）
      viewMode: '3D',
    })

    console.log('[地图] 地图实例创建成功')

    // 注意：不再使用 JS API 的 Geocoder，改用 Web 服务 HTTP API

    loading.value = false

    // 地图加载完成后标记地点
    map.on('complete', () => {
      console.log('[地图] 地图加载完成')
      markLocations()
    })
  } catch (error: any) {
    console.error('[地图] 初始化失败:', error)
    loading.value = false
  }
}

// 延迟函数，用于控制请求频率
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

// 使用高德地图 Web 服务 API 搜索地点（使用 JSONP 避免 CORS 问题）
const searchLocation = async (locationName: string): Promise<any> => {
  // 检查缓存
  if (locationCache.has(locationName)) {
    const cached = locationCache.get(locationName)
    console.log(`[地点搜索] ✓ 使用缓存: "${locationName}"`)
    return cached
  }

  console.log(`[地点搜索] 开始搜索地点: "${locationName}"`)

  // 添加延迟，避免触发频率限制（每个请求间隔 200ms）
  await delay(200)

  const apiKey = import.meta.env.VITE_AMAP_KEY

  return new Promise((resolve, reject) => {
    // 使用 JSONP 方式调用 API，避免 CORS 问题
    const callbackName = `amap_callback_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`

    // 创建 script 标签
    const script = document.createElement('script')
    const url = new URL('https://restapi.amap.com/v3/place/text')
    url.searchParams.set('key', apiKey)
    url.searchParams.set('keywords', locationName)
    url.searchParams.set('city', '全国')
    url.searchParams.set('offset', '1')
    url.searchParams.set('page', '1')
    url.searchParams.set('extensions', 'base')
    url.searchParams.set('callback', callbackName)

    script.src = url.toString()

    // 超时处理
    let timeoutId: ReturnType<typeof setTimeout> | null = null
    let isResolved = false

    const cleanup = () => {
      if (timeoutId) {
        clearTimeout(timeoutId)
        timeoutId = null
      }
      delete (window as any)[callbackName]
      if (document.body.contains(script)) {
        document.body.removeChild(script)
      }
    }

    // 设置全局回调函数
    ;(window as any)[callbackName] = (data: any) => {
      if (isResolved) return
      isResolved = true

      cleanup()

      console.log(`[地点搜索] API 响应:`, data)

      if (data.status === '1' && data.pois && data.pois.length > 0) {
        const poi = data.pois[0]
        const location = poi.location.split(',') // 格式: "lng,lat"

        console.log(`[地点搜索] ✓ 找到地点: "${locationName}" -> ${poi.name}`, {
          lng: parseFloat(location[0]),
          lat: parseFloat(location[1]),
        })

        const result = {
          location: {
            lng: parseFloat(location[0]),
            lat: parseFloat(location[1]),
          },
          address: poi.address || poi.name,
          name: poi.name,
          type: poi.type,
          tel: poi.tel || '',
        }

        // 缓存结果
        locationCache.set(locationName, result)
        resolve(result)
      } else {
        console.warn(`[地点搜索] ✗ 未找到地点: "${locationName}"`, data)

        // 检查是否是频率限制错误
        if (data.info?.includes('CUQPS_HAS_EXCEEDED_THE_LIMIT') || data.infocode === '10021') {
          console.error(`[地点搜索] ⚠️ API 调用频率超限，请稍后重试`)
          // 不缓存错误结果，允许重试
          reject(new Error(`API调用频率超限，请稍后重试: ${locationName}`))
          return
        }

        // 检查是否是 API Key 错误
        if (data.info?.includes('USERKEY_PLAT_NOMATCH') || data.info?.includes('平台')) {
          console.error(`[地点搜索] ⚠️ API Key 平台配置错误！`)
          apiError.value = {
            title: 'API Key 配置错误',
            description:
              '您的 API Key 需要开通 "Web服务" 权限。请登录高德开放平台，在 Key 管理中确保已开通相关服务。',
          }
        }

        reject(new Error(`未找到地点: ${locationName}`))
      }
    }

    // 错误处理
    script.onerror = () => {
      if (isResolved) return
      isResolved = true

      cleanup()
      console.error(`[地点搜索] ✗ JSONP 请求失败: "${locationName}"`)
      reject(new Error(`请求失败: ${locationName}`))
    }

    // 设置超时
    timeoutId = setTimeout(() => {
      if (isResolved) return
      isResolved = true

      cleanup()
      console.error(`[地点搜索] ✗ 请求超时: "${locationName}"`)
      reject(new Error(`请求超时: ${locationName}`))
    }, 8000)

    // 添加到页面
    document.body.appendChild(script)
  })
}

// 标记所有地点
const markLocations = async () => {
  if (!map || !props.activities || props.activities.length === 0) {
    console.log('[地点标记] 没有活动数据，跳过标记')
    parsingLocations.value = false
    return
  }

  // 清除之前的标记
  clearMarkers()

  // 显示解析提示
  parsingLocations.value = true
  parsingStatus.value = {
    title: '正在解析地点',
    description: '正在分析行程中的地点信息，请稍候...',
  }

  console.log(`[地点标记] 开始标记 ${props.activities.length} 个活动的地点...`)

  const locations: any[] = []

  // 遍历所有活动，只标记类型不是"交通"的活动
  // 先收集所有需要搜索的地点，去重
  const locationNamesToSearch = new Set<string>()
  const activityLocationMap = new Map<string, Array<{ activity: any; index: number }>>()

  for (let i = 0; i < props.activities.length; i++) {
    const activity = props.activities[i]

    // 检查 activity 是否存在
    if (!activity) {
      continue
    }

    // 检查类型是否为"交通"
    if (activity.type === '交通') {
      console.log(`[地点标记] 跳过交通类型活动: "${activity.activity || '未知'}" (索引: ${i})`)
      continue
    }

    // 检查是否有地点信息
    if (!activity.location || activity.location.trim() === '') {
      console.log(`[地点标记] 活动 "${activity.activity || '未知'}" 没有地点信息，跳过`)
      continue
    }

    const locationName = activity.location.trim()

    // 收集需要搜索的地点（去重）
    if (!locationCache.has(locationName)) {
      locationNamesToSearch.add(locationName)
    }

    // 建立地点到活动的映射
    if (!activityLocationMap.has(locationName)) {
      activityLocationMap.set(locationName, [])
    }
    activityLocationMap.get(locationName)!.push({ activity, index: i })
  }

  console.log(
    `[地点标记] 需要搜索 ${locationNamesToSearch.size} 个唯一地点（共 ${props.activities.length} 个活动）`,
  )

  // 批量搜索地点（带延迟，避免频率限制）
  const searchResults = new Map<string, any>()
  const searchErrors = new Map<string, Error>()
  const totalLocations = locationNamesToSearch.size
  let processedCount = 0

  for (const locationName of locationNamesToSearch) {
    processedCount++
    parsingStatus.value = {
      title: '正在解析地点',
      description: `正在搜索地点 ${processedCount}/${totalLocations}：${locationName}...`,
    }
    try {
      console.log(
        `[地点标记] 处理地点: "${locationName}" (${Array.from(locationNamesToSearch).indexOf(locationName) + 1}/${locationNamesToSearch.size})`,
      )
      const locationData = await searchLocation(locationName)
      searchResults.set(locationName, locationData)
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : '未知错误'
      console.error(`[地点标记] ✗ 搜索地点失败: "${locationName}"`, errorMessage)
      searchErrors.set(locationName, error instanceof Error ? error : new Error(errorMessage))

      // 如果是频率限制错误，增加延迟
      if (errorMessage.includes('频率超限')) {
        console.log(`[地点标记] 检测到频率限制，等待 2 秒后继续...`)
        await delay(2000)
      }
    }
  }

  // 根据搜索结果构建 locations 数组
  for (const [locationName, activities] of activityLocationMap.entries()) {
    const locationData = searchResults.get(locationName) || locationCache.get(locationName)

    if (locationData) {
      // 为每个使用该地点的活动创建标记
      for (const { activity, index } of activities) {
        locations.push({
          ...locationData,
          activity: activity.activity || '',
          description: activity.description || '', // 添加描述字段
          index: index,
        })
      }
      console.log(`[地点标记] ✓ 地点 "${locationName}" 已添加到 ${activities.length} 个活动`)
    } else {
      console.warn(`[地点标记] ⚠️ 地点 "${locationName}" 未找到，跳过 ${activities.length} 个活动`)
    }
  }

  console.log(`[地点标记] 成功找到 ${locations.length} 个地点，开始在地图上标记...`)

  if (locations.length === 0) {
    console.log('[地点标记] 没有可标记的地点')
    parsingLocations.value = false
    return
  }

  // 更新状态：正在标记
  parsingStatus.value = {
    title: '正在标记地点',
    description: `正在在地图上标记 ${locations.length} 个地点...`,
  }

  // 检查 AMap 实例
  if (!AMapInstance) {
    console.error('[地点标记] 高德地图 API 未加载')
    return
  }

  // 为每个地点创建标记（参考提供的代码风格）
  locations.forEach((loc, index) => {
    // 根据活动类型选择图标
    let icon = '📍'
    const activityType = loc.activity?.toLowerCase() || ''
    if (activityType.includes('酒店') || activityType.includes('住宿')) {
      icon = '🏨'
    } else if (
      activityType.includes('餐厅') ||
      activityType.includes('美食') ||
      activityType.includes('午餐') ||
      activityType.includes('晚餐') ||
      activityType.includes('早餐')
    ) {
      icon = '🍽️'
    } else if (
      activityType.includes('景点') ||
      activityType.includes('参观') ||
      activityType.includes('游览')
    ) {
      icon = '🎯'
    }

    // 创建标记
    const marker = new AMapInstance.Marker({
      position: [loc.location.lng, loc.location.lat],
      title: loc.name,
      label: {
        content: `<div style="background: #4f7942; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 500; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">${icon} ${index + 1}. ${loc.name}</div>`,
        direction: 'top',
        offset: new AMapInstance.Pixel(0, -10),
      },
    })

    // 创建信息窗口（更详细的内容）
    const infoWindow = new AMapInstance.InfoWindow({
      content: `
        <div style="padding: 15px; min-width: 250px; max-width: 300px;">
          <div style="font-size: 24px; text-align: center; margin-bottom: 8px;">${icon}</div>
          <h3 style="margin: 0 0 10px 0; font-size: 16px; color: #303133; font-weight: 600; text-align: center;">${loc.activity || '活动'}</h3>
          <div style="border-top: 1px solid #ebeef5; padding-top: 10px; margin-top: 10px;">
            <p style="margin: 6px 0; font-size: 13px; color: #606266;">
              <strong style="color: #303133;">📍 地点:</strong> ${loc.name}
            </p>
            <p style="margin: 6px 0; font-size: 13px; color: #606266;">
              <strong style="color: #303133;">🏠 地址:</strong> ${loc.address || loc.name}
            </p>
            ${loc.description ? `<p style="margin: 6px 0; font-size: 13px; color: #606266;"><strong style="color: #303133;">📝 描述:</strong> ${loc.description}</p>` : ''}
          </div>
        </div>
      `,
      offset: new AMapInstance.Pixel(0, -30),
    })

    // 绑定点击事件
    marker.on('click', () => {
      infoWindow.open(map, marker.getPosition())
    })

    // 添加到地图
    map.add(marker)
    markers.push(marker)

    console.log(
      `[地点标记] ✓ 已标记地点 ${index + 1}: "${loc.name}" (${loc.location.lng}, ${loc.location.lat})`,
    )
  })

  // 设置地图中心点和缩放级别
  if (locations.length > 0) {
    // 先定位到第一个地点
    const firstLocation = locations[0]
    map.setCenter([firstLocation.location.lng, firstLocation.location.lat])

    if (markers.length > 1) {
      // 如果有多个地点，先定位到第一个，然后使用自适应视图显示所有标记
      // 使用 setTimeout 确保地图先移动到第一个地点，再调整视野
      setTimeout(() => {
        map.setFitView(markers, false, [60, 60, 60, 60], 16)
        console.log(`[地点标记] 已调整地图视野，显示所有 ${markers.length} 个标记`)
      }, 300)

      // 先设置一个合适的缩放级别，让第一个地点清晰可见
      map.setZoom(15)
      console.log(
        `[地点标记] 已定位到第一个地点: "${firstLocation.name}" (${firstLocation.location.lng}, ${firstLocation.location.lat})`,
      )
    } else {
      // 单个地点，设置中心点和缩放级别
      map.setZoom(15)
      console.log(
        `[地点标记] 已设置地图中心点: (${firstLocation.location.lng}, ${firstLocation.location.lat})`,
      )
    }
  }

  console.log(`[地点标记] 完成！共标记 ${markers.length} 个地点`)

  // 标记完成，隐藏解析提示
  parsingLocations.value = false
}

// 清除所有标记
const clearMarkers = () => {
  if (map && markers.length > 0) {
    console.log(`[地点标记] 清除 ${markers.length} 个旧标记`)
    map.remove(markers)
    markers = []
  }
}

// 监听活动数据变化
watch(
  () => props.activities,
  () => {
    console.log('[地图] 活动数据发生变化，重新标记地点')
    if (map && !loading.value) {
      markLocations()
    }
  },
  { deep: true },
)

onMounted(() => {
  initMap()
})

onUnmounted(() => {
  clearMarkers()
  if (map) {
    map.destroy()
    map = null
  }
})
</script>

<style scoped>
.map-container {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 600px;
}

.amap-container {
  width: 100%;
  height: 100%;
}

.map-loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  color: #606266;
  z-index: 1000;
  background: rgba(255, 255, 255, 0.9);
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.map-loading .el-icon {
  font-size: 24px;
}

.map-error {
  position: absolute;
  top: 20px;
  left: 20px;
  right: 20px;
  z-index: 1000;
  max-width: 500px;
}

.map-parsing {
  position: absolute;
  top: 20px;
  left: 20px;
  right: 20px;
  z-index: 1000;
  max-width: 500px;
}

.parsing-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.parsing-content .el-icon {
  font-size: 16px;
}
</style>
