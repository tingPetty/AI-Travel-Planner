<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Calendar, Money, Edit, Delete, MapLocation } from '@element-plus/icons-vue'
import { 
  generateItinerary, 
  getItineraryList, 
  deleteItinerary as deleteItineraryAPI,
  type ItineraryListResponse,
  type ItineraryGenerateRequest 
} from '@/api/itinerary'

// 路由
const router = useRouter()

// 响应式数据
const activeMenu = ref('itinerary')
const dialogVisible = ref(false)
const loading = ref(false)
const trips = ref<ItineraryListResponse[]>([])

// 新建行程表单
const newTripForm = reactive({
  title: '',
  destination: '',
  startDate: '',
  endDate: '',
  budget: null,
  travelers: 1,
  preferences: [],
  description: '',
  travel_style: ''
})

// 旅行偏好选项
const preferenceOptions = [
  { label: '美食', value: 'food' },
  { label: '文化', value: 'culture' },
  { label: '自然风光', value: 'nature' },
  { label: '购物', value: 'shopping' },
  { label: '历史古迹', value: 'history' },
  { label: '冒险运动', value: 'adventure' },
  { label: '放松度假', value: 'relaxation' },
  { label: '摄影', value: 'photography' }
]

// 计算属性
const filteredTrips = computed(() => {
  return trips.value
})

// 加载行程列表
const loadTrips = async () => {
  try {
    loading.value = true
    const response = await getItineraryList()
    
    // 安全处理响应数据，避免Vue渲染错误
    const safeTrips = response.map(trip => {
      // 创建一个安全的副本，避免直接使用可能有问题的数据
      return {
        ...trip,
        // 确保所有字段都是安全的
        id: trip.id,
        title: trip.title || '',
        destination: trip.destination || '',
        start_date: trip.start_date || '',
        end_date: trip.end_date || '',
        status: trip.status || 'planning',
        created_at: trip.created_at || ''
      }
    })
    
    trips.value = safeTrips
    console.log('行程数据加载成功:', safeTrips)
  } catch (error) {
    console.error('加载行程列表失败:', error)
    ElMessage.error('加载行程列表失败')
  } finally {
    loading.value = false
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadTrips()
})

// 方法
const handleMenuSelect = (key: string) => {
  activeMenu.value = key
}

const openNewTripDialog = () => {
  dialogVisible.value = true
}

const closeDialog = () => {
  dialogVisible.value = false
  resetForm()
}

const resetForm = () => {
  Object.assign(newTripForm, {
    title: '',
    destination: '',
    startDate: '',
    endDate: '',
    budget: null,
    travelers: 1,
    preferences: [],
    description: '',
    travel_style: ''
  })
}

const submitTrip = async () => {
  try {
    // 表单验证
    if (!newTripForm.title || !newTripForm.destination || !newTripForm.startDate || !newTripForm.endDate) {
      ElMessage.warning('请填写必要信息')
      return
    }

    loading.value = true
    
    // 构建请求数据
    const requestData: ItineraryGenerateRequest = {
      title: newTripForm.title,
      destination: newTripForm.destination,
      start_date: formatDateForAPI(newTripForm.startDate),
      end_date: formatDateForAPI(newTripForm.endDate),
      budget: newTripForm.budget || undefined,
      preferences: newTripForm.preferences.join(', '),
      travel_style: newTripForm.travel_style || undefined
    }

    console.log('发送请求数据:', requestData)
    ElMessage.info('正在调用AI生成行程，请稍候...')
    
    // 调用AI生成行程API
    const response = await generateItinerary(requestData)
    console.log('API响应:', response)
    
    if (response.success && response.data) {
      ElMessage.success('AI行程生成成功！')
      // 先关闭对话框，再重新加载数据
      closeDialog()
      // 延迟重新加载，避免渲染冲突
      setTimeout(async () => {
        await loadTrips()
      }, 100)
    } else {
      ElMessage.error(response.message || 'AI行程生成失败')
      closeDialog()
    }
    
  } catch (error: any) {
    console.error('API请求错误:', error)
    
    // 检查是否是422验证错误
    if (error.response?.status === 422) {
      console.error('验证错误详情:', error.response.data)
      
      // 安全地处理验证错误信息
      let errorMessage = '请求数据格式错误，请检查输入信息'
      
      if (error.response.data?.detail) {
        if (Array.isArray(error.response.data.detail)) {
          // 如果是数组，提取第一个错误信息
          const firstError = error.response.data.detail[0]
          if (firstError?.msg) {
            errorMessage = `数据验证失败: ${firstError.msg}`
          }
        } else if (typeof error.response.data.detail === 'string') {
          errorMessage = error.response.data.detail
        }
      }
      
      ElMessage.error(errorMessage)
    } else {
      ElMessage.error(error.response?.data?.detail || '生成行程失败，请重试')
    }
    
    closeDialog()
  } finally {
    loading.value = false
  }
}

const editTrip = (trip: any) => {
  router.push(`/edit-trip/${trip.id}`)
}

const deleteTrip = async (trip: ItineraryListResponse) => {
  try {
    await ElMessageBox.confirm('确定要删除这个行程吗？', '确认删除', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await deleteItineraryAPI(trip.id)
    ElMessage.success('行程已删除')
    
    // 重新加载行程列表
    await loadTrips()
    
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除行程失败:', error)
      ElMessage.error('删除行程失败')
    }
  }
}

const getStatusType = (status: string) => {
  const statusMap: { [key: string]: string } = {
    'planning': 'warning',
    'ongoing': 'primary',
    'completed': 'success',
    'cancelled': 'info'
  }
  return statusMap[status] || 'info'
}

// 格式化日期显示
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 格式化日期为YYYY-MM-DD格式
const formatDateForAPI = (date: Date | string | null): string => {
  if (!date) return ''
  
  const dateObj = typeof date === 'string' ? new Date(date) : date
  if (isNaN(dateObj.getTime())) return ''
  
  const year = dateObj.getFullYear()
  const month = String(dateObj.getMonth() + 1).padStart(2, '0')
  const day = String(dateObj.getDate()).padStart(2, '0')
  
  return `${year}-${month}-${day}`
}
</script>

<template>
  <div class="dashboard">
    <!-- 左侧导航栏 -->
    <div class="sidebar">
      <div class="sidebar-header">
        <h3>功能导航</h3>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        @select="handleMenuSelect"
      >
        <el-menu-item index="itinerary">
          <el-icon><Calendar /></el-icon>
          <span>行程规划</span>
        </el-menu-item>
        <el-menu-item index="budget">
          <el-icon><Money /></el-icon>
          <span>费用管理</span>
        </el-menu-item>
      </el-menu>
    </div>

    <!-- 主内容区域 -->
    <div class="main-content">
      <!-- 行程规划页面 -->
      <div v-if="activeMenu === 'itinerary'" class="content-section">
        <div class="section-header">
          <h2>我的行程规划</h2>
          <el-button 
            type="primary" 
            :icon="Plus" 
            @click="openNewTripDialog"
            color="#4f7942"
          >
            新建行程
          </el-button>
        </div>

        <!-- 行程卡片列表 -->
        <div class="trips-grid" v-loading="loading">
          <div 
            v-for="trip in filteredTrips" 
            :key="trip.id" 
            class="trip-card"
          >
            <div class="card-header">
              <h3>{{ trip.title }}</h3>
              <el-tag :type="getStatusType(trip.status)">
                {{ trip.status === 'planning' ? '规划中' : 
                   trip.status === 'ongoing' ? '进行中' : 
                   trip.status === 'completed' ? '已完成' : 
                   trip.status === 'cancelled' ? '已取消' : trip.status }}
              </el-tag>
            </div>
            
            <div class="card-content">
              <div class="trip-info">
                <div class="info-item">
                  <el-icon><MapLocation /></el-icon>
                  <span>{{ trip.destination }}</span>
                </div>
                <div class="info-item">
                  <el-icon><Calendar /></el-icon>
                  <span>{{ formatDate(trip.start_date) }} 至 {{ formatDate(trip.end_date) }}</span>
                </div>
                <div class="info-item" v-if="trip.budget">
                  <el-icon><Money /></el-icon>
                  <span>预算：¥{{ trip.budget }}</span>
                </div>
              </div>
              
              <p class="trip-description">{{ trip.description || '暂无描述' }}</p>
            </div>
            
            <div class="card-actions">
              <el-button 
                type="primary" 
                size="small" 
                :icon="Edit"
                @click="editTrip(trip)"
                plain
              >
                编辑
              </el-button>
              <el-button 
                type="danger" 
                size="small" 
                :icon="Delete"
                @click="deleteTrip(trip)"
                plain
              >
                删除
              </el-button>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-if="trips.length === 0" class="empty-state">
          <el-empty description="还没有创建任何行程">
            <el-button 
              type="primary" 
              @click="openNewTripDialog"
              color="#4f7942"
            >
              创建第一个行程
            </el-button>
          </el-empty>
        </div>
      </div>

      <!-- 费用管理页面 -->
      <div v-else-if="activeMenu === 'budget'" class="content-section">
        <div class="section-header">
          <h2>费用管理</h2>
        </div>
        <div class="coming-soon">
          <el-result
            icon="info"
            title="功能开发中"
            sub-title="费用管理功能正在开发中，敬请期待..."
          />
        </div>
      </div>
    </div>

    <!-- 新建行程对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="新建旅行计划"
      width="600px"
      @close="closeDialog"
    >
      <el-form :model="newTripForm" label-width="100px">
        <el-form-item label="行程标题" required>
          <el-input 
            v-model="newTripForm.title" 
            placeholder="给您的旅行起个名字"
          />
        </el-form-item>
        
        <el-form-item label="目的地" required>
          <el-input 
            v-model="newTripForm.destination" 
            placeholder="您想去哪里？"
          />
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开始日期" required>
              <el-date-picker
                v-model="newTripForm.startDate"
                type="date"
                placeholder="选择开始日期"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束日期" required>
              <el-date-picker
                v-model="newTripForm.endDate"
                type="date"
                placeholder="选择结束日期"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="预算">
              <el-input-number
                v-model="newTripForm.budget"
                :min="0"
                :step="100"
                placeholder="预算金额"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="同行人数">
              <el-input-number
                v-model="newTripForm.travelers"
                :min="1"
                :max="20"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="旅行偏好">
          <el-checkbox-group v-model="newTripForm.preferences">
            <el-checkbox 
              v-for="option in preferenceOptions" 
              :key="option.value"
              :label="option.value"
            >
              {{ option.label }}
            </el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        
        <el-form-item label="旅行风格">
          <el-select 
            v-model="newTripForm.travel_style" 
            placeholder="选择您的旅行风格"
            style="width: 100%"
          >
            <el-option label="休闲度假" value="leisure" />
            <el-option label="深度体验" value="cultural" />
            <el-option label="冒险探索" value="adventure" />
            <el-option label="奢华享受" value="luxury" />
            <el-option label="经济实惠" value="budget" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="备注">
          <el-input
            v-model="newTripForm.description"
            type="textarea"
            :rows="3"
            placeholder="其他需求或特殊说明..."
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="closeDialog" :disabled="loading">取消</el-button>
          <el-button 
            type="primary" 
            @click="submitTrip" 
            color="#4f7942"
            :loading="loading"
            :disabled="loading"
          >
            {{ loading ? '正在生成行程...' : '创建并生成行程' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.dashboard {
  display: flex;
  height: calc(100vh - 60px);
  background-color: #f8faf8;
  margin: 0;
  padding: 0;
}

/* 左侧导航栏 */
.sidebar {
  width: 250px;
  background: white;
  border-right: 1px solid #edf2ed;
  box-shadow: 2px 0 8px rgba(143, 188, 143, 0.08);
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #edf2ed;
}

.sidebar-header h3 {
  margin: 0;
  color: #6b8e6b;
  font-size: 18px;
  font-weight: 600;
}

.sidebar-menu {
  border: none;
}

.sidebar-menu .el-menu-item {
  height: 50px;
  line-height: 50px;
  color: #606266;
  transition: all 0.3s;
}

.sidebar-menu .el-menu-item:hover,
.sidebar-menu .el-menu-item.is-active {
  background-color: #f0f9f0;
  color: #4f7942;
}

.sidebar-menu .el-menu-item .el-icon {
  margin-right: 8px;
  font-size: 16px;
}

/* 主内容区域 */
.main-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.content-section {
  max-width: 1200px;
  margin: 0 auto;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-header h2 {
  margin: 0;
  color: #2c3e50;
  font-size: 24px;
  font-weight: 600;
}

/* 行程卡片网格 */
.trips-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.trip-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(143, 188, 143, 0.08);
  border: 1px solid #edf2ed;
  transition: all 0.3s;
}

.trip-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(143, 188, 143, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 18px;
  font-weight: 600;
}

.card-content {
  margin-bottom: 16px;
}

.trip-info {
  margin-bottom: 12px;
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  color: #606266;
  font-size: 14px;
}

.info-item .el-icon {
  margin-right: 8px;
  color: #8fbc8f;
}

.trip-description {
  color: #909399;
  font-size: 14px;
  line-height: 1.5;
  margin: 0;
}

.card-actions {
  display: flex;
  gap: 8px;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.coming-soon {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
}

/* 对话框样式 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dashboard {
    flex-direction: column;
    height: auto;
  }
  
  .sidebar {
    width: 100%;
    height: auto;
  }
  
  .sidebar-menu {
    display: flex;
    overflow-x: auto;
  }
  
  .sidebar-menu .el-menu-item {
    white-space: nowrap;
    min-width: 120px;
  }
  
  .main-content {
    padding: 16px;
  }
  
  .trips-grid {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
}

@media (max-width: 480px) {
  .trip-card {
    padding: 16px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .card-actions {
    flex-direction: column;
  }
}
</style>