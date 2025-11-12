<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Calendar, Money, Edit, Delete, MapLocation } from '@element-plus/icons-vue'
import { 
  getItineraryList, 
  deleteItinerary as deleteItineraryAPI,
  type ItineraryListResponse,
} from '@/api/itinerary'
import { getExpenses, getBudgetSummary, getAIBudgetAnalysis, type ExpenseResponse, type BudgetSummaryResponse, type AIBudgetAnalysisResponse } from '@/api/budget'
import BudgetSummary from '@/components/budget/BudgetSummary.vue'
import ExpenseDialog from '@/components/budget/ExpenseDialog.vue'

// 路由
const router = useRouter()

// 响应式数据
const activeMenu = ref('itinerary')
const loading = ref(false)
const trips = ref<ItineraryListResponse[]>([])
// 预算管理相关
const selectedTripId = ref<number | null>(null)
const expenses = ref<ExpenseResponse[]>([])
const summary = ref<BudgetSummaryResponse | null>(null)
const budgetLoading = ref(false)
const showExpenseDialog = ref(false)
// AI预算分析相关
const aiAnalysisLoading = ref(false)
const aiAnalysisResult = ref<AIBudgetAnalysisResponse | null>(null)
// 费用列表等宽列宽计算
const expensesTableRef = ref<any | null>(null)
const colWidth = ref(240)
const updateColWidth = () => {
  try {
    const el = expensesTableRef.value?.$el ?? expensesTableRef.value
    const width = el?.clientWidth || 960
    colWidth.value = Math.max(200, Math.floor(width / 4))
  } catch {
    // 回退列宽
    colWidth.value = 240
  }
}

// 旅行偏好选项
// const preferenceOptions = [
//   { label: '美食', value: 'food' },
//   { label: '文化', value: 'culture' },
//   { label: '自然风光', value: 'nature' },
//   { label: '购物', value: 'shopping' },
//   { label: '历史古迹', value: 'history' },
//   { label: '冒险运动', value: 'adventure' },
//   { label: '放松度假', value: 'relaxation' },
//   { label: '摄影', value: 'photography' }
// ]

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
  // 初始化并监听窗口尺寸变化，保证四列等宽
  nextTick(updateColWidth)
  window.addEventListener('resize', updateColWidth)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateColWidth)
})

// 方法
const handleMenuSelect = (key: string) => {
  activeMenu.value = key
}

const openNewTripDialog = () => {
  router.push('/new-trip')
}

// 新建行程提交逻辑已迁移到新页面

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

// 类别中文映射，后端保存英文枚举，前端统一中文展示
const categoryLabels: Record<string, string> = {
  transport: '交通',
  accommodation: '住宿',
  food: '食物',
  entertainment: '娱乐',
  shopping: '购物',
  other: '其他'
}
const formatCategory = (val: string) => categoryLabels[val] ?? val

// 格式化日期显示
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 格式化日期工具仅用于展示
// 预算管理：加载指定行程的费用与汇总
const loadBudgetData = async (tripId: number) => {
  try {
    budgetLoading.value = true
    const [list, sum] = await Promise.all([
      getExpenses(tripId),
      getBudgetSummary(tripId)
    ])
    expenses.value = list
    summary.value = sum
    await nextTick()
    updateColWidth()
  } catch (e) {
    console.error('加载费用/汇总失败:', e)
    ElMessage.error('加载费用数据失败')
  } finally {
    budgetLoading.value = false
  }
}

// 当行程数据加载完成后默认选中第一个并加载预算数据
watch(trips, (val) => {
  if (activeMenu.value === 'budget' && val.length > 0 && selectedTripId.value == null) {
    selectedTripId.value = val[0]?.id
    if (selectedTripId.value) {
      loadBudgetData(selectedTripId.value)
    }
  }
})

watch(activeMenu, (menu) => {
  if (menu === 'budget' && trips.value.length > 0) {
    if (selectedTripId.value == null) {
      selectedTripId.value = trips.value[0]?.id
    }
    if (selectedTripId.value) {
      loadBudgetData(selectedTripId.value)
    }
  }
})

const onTripChange = (val: number) => {
  selectedTripId.value = val
  aiAnalysisResult.value = null // 清空AI分析结果
  loadBudgetData(val)
}

const onExpenseCreated = () => {
  if (selectedTripId.value) {
    loadBudgetData(selectedTripId.value)
  }
}

// AI预算分析
const handleAIAnalysis = async () => {
  if (!selectedTripId.value) {
    ElMessage.warning('请先选择行程')
    return
  }
  
  try {
    aiAnalysisLoading.value = true
    const result = await getAIBudgetAnalysis(selectedTripId.value) as AIBudgetAnalysisResponse
    aiAnalysisResult.value = result
    ElMessage.success('AI分析完成')
  } catch (error: any) {
    console.error('AI预算分析失败:', error)
    // 错误消息已由axios拦截器显示，这里不再重复显示
  } finally {
    aiAnalysisLoading.value = false
  }
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
              
              <!-- <p class="trip-description">{{ trip.description || '暂无描述' }}</p> -->
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
      <div v-else-if="activeMenu === 'budget'" class="content-section budget-section">
        <div class="section-header">
          <h2>费用管理</h2>
          <el-button type="primary" :icon="Plus" color="#4f7942" @click="showExpenseDialog = true" :disabled="!selectedTripId">
            新建费用记录
          </el-button>
        </div>

        <!-- 选择行程 -->
        <div class="filter-bar">
          <el-select v-model="selectedTripId" placeholder="选择行程" @change="onTripChange" style="width: 320px">
            <!-- <el-option v-for="trip in trips" :key="trip.id" :label="`#${trip.id} - ${trip.title}`" :value="trip.id" /> -->
             <el-option v-for="trip in trips" :key="trip.id" :label="`# ${trip.title}`" :value="trip.id" />
          </el-select>
        </div>

        <!-- AI预算分析卡片 -->
        <el-card class="ai-analysis-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>🌟 AI 预算分析</span>
              <el-button 
                type="primary" 
                @click="handleAIAnalysis" 
                :loading="aiAnalysisLoading"
                :disabled="!selectedTripId"
                size="default"
                color="#4f7942"
              >
                {{ aiAnalysisResult ? '重新分析' : 'AI 预算分析' }}
              </el-button>
            </div>
          </template>
          
          <div v-if="aiAnalysisResult" class="analysis-content">
            <div class="analysis-section">
              <h4>开销分析</h4>
              <p class="analysis-text">{{ aiAnalysisResult.analysis }}</p>
            </div>
            
            <div class="suggestions-section">
              <h4>旅游建议</h4>
              <ul class="suggestions-list">
                <li v-for="(suggestion, index) in aiAnalysisResult.suggestions" :key="index">
                  {{ suggestion }}
                </li>
              </ul>
            </div>
          </div>
          
          <div v-else class="empty-analysis">
            <el-empty description="点击按钮开始AI预算分析" :image-size="80" />
          </div>
        </el-card>

        <!-- 汇总卡片 -->
        <BudgetSummary :summary="summary" />

        <!-- 费用列表 -->
        <el-card class="expenses-card" v-loading="budgetLoading">
          <template #header>
            <div class="card-header">
              <span>当前行程开销</span>
            </div>
          </template>
          <el-table ref="expensesTableRef" :data="expenses" stripe class="expenses-table">
            <el-table-column prop="expense_date" label="日期" :width="colWidth" align="center">
              <template #default="scope">
                {{ formatDate(scope.row.expense_date) }}
              </template>
            </el-table-column>
            <el-table-column prop="amount" label="金额" :width="colWidth" align="center">
              <template #default="scope">
                ¥{{ Number(scope.row.amount).toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="category" label="类别" :width="colWidth" align="center">
              <template #default="scope">
                {{ formatCategory(scope.row.category) }}
              </template>
            </el-table-column>
            <el-table-column prop="description" label="描述" :width="colWidth" show-overflow-tooltip align="center" />
          </el-table>
        </el-card>

        <!-- 新建费用弹窗 -->
        <ExpenseDialog v-model:visible="showExpenseDialog" :trip-id="selectedTripId" @created="onExpenseCreated" />
      </div>
    </div>

    
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

/* 费用管理样式 */
.budget-section .filter-bar {
  margin-bottom: 16px;
}

/* AI预算分析卡片样式 */
.ai-analysis-card {
  margin-bottom: 16px;
  border-radius: 12px;
  border: 1px solid #edf2ed;
  box-shadow: 0 2px 12px rgba(143, 188, 143, 0.08);
}

.ai-analysis-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ai-analysis-card .card-header span {
  color: #6b8e6b;
  font-weight: 600;
  font-size: 16px;
}

.analysis-content {
  padding: 8px 0;
}

.analysis-section,
.suggestions-section {
  margin-bottom: 20px;
}

.analysis-section:last-child,
.suggestions-section:last-child {
  margin-bottom: 0;
}

.analysis-section h4,
.suggestions-section h4 {
  margin: 0 0 12px 0;
  color: #4f7942;
  font-size: 15px;
  font-weight: 600;
}

.analysis-text {
  margin: 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.8;
  padding: 12px;
  background-color: #f8faf8;
  border-radius: 8px;
  border-left: 3px solid #8fbc8f;
}

.suggestions-list {
  margin: 0;
  padding-left: 24px;
  color: #606266;
  font-size: 14px;
  line-height: 2;
}

.suggestions-list li {
  margin-bottom: 8px;
  position: relative;
}

.suggestions-list li::marker {
  color: #8fbc8f;
  font-weight: bold;
}

.empty-analysis {
  padding: 20px 0;
  text-align: center;
}

.expenses-card {
  border-radius: 12px;
  border: 1px solid #edf2ed;
  box-shadow: 0 2px 12px rgba(143, 188, 143, 0.08);
}

.expenses-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.expenses-card .card-header span {
  color: #6b8e6b;
  font-weight: 600;
}

/* 让费用表格四列等宽且更易读 */
.expenses-table :deep(.el-table__header),
.expenses-table :deep(.el-table__body) {
  table-layout: fixed;
}
.expenses-table :deep(.el-table__cell) {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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