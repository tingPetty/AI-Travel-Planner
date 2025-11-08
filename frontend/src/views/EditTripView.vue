<template>
  <div class="edit-trip-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">编辑行程</h1>
      <el-button @click="goBack" type="default" icon="ArrowLeft">返回</el-button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="8" animated />
    </div>

    <!-- 编辑表单 -->
    <div v-else-if="tripData" class="edit-form">
      <el-form :model="formData" :rules="rules" ref="formRef" label-width="120px">
        <!-- 基本信息 -->
        <el-card class="form-section" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>基本信息</span>
            </div>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="行程标题" prop="title">
                <el-input v-model="formData.title" placeholder="请输入行程标题" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="目的地" prop="destination">
                <el-input v-model="formData.destination" placeholder="请输入目的地" />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="开始日期" prop="start_date">
                <el-date-picker
                  v-model="formData.start_date"
                  type="date"
                  placeholder="选择开始日期"
                  style="width: 100%"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="结束日期" prop="end_date">
                <el-date-picker
                  v-model="formData.end_date"
                  type="date"
                  placeholder="选择结束日期"
                  style="width: 100%"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="预算" prop="budget">
                <el-input-number
                  v-model="formData.budget"
                  :min="0"
                  :precision="2"
                  placeholder="请输入预算"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="状态" prop="status">
                <el-select v-model="formData.status" placeholder="选择状态" style="width: 100%">
                  <el-option label="规划中" value="planning" />
                  <el-option label="进行中" value="ongoing" />
                  <el-option label="已完成" value="completed" />
                  <el-option label="已取消" value="cancelled" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </el-card>

        <!-- 详细行程 -->
        <el-card class="form-section" shadow="hover" v-if="formData.itinerary">
          <template #header>
            <div class="card-header">
              <span>详细行程</span>
            </div>
          </template>
          
          <div v-for="(day, dayKey) in formData.itinerary" :key="dayKey" class="day-section">
            <h3 class="day-title">{{ dayKey.toUpperCase() }} - {{ day.date }}</h3>
            
            <div v-for="(activity, actIndex) in day.activities" :key="actIndex" class="activity-item">
              <el-row :gutter="20">
                <el-col :span="5">
                  <el-form-item :label="`时间`">
                    <el-input v-model="activity.time" placeholder="时间" />
                  </el-form-item>
                </el-col>
                <el-col :span="10">
                  <el-form-item :label="`活动`">
                    <el-input v-model="activity.activity" placeholder="活动名称" />
                  </el-form-item>
                </el-col>
                <el-col :span="9">
                  <el-form-item :label="`地点`">
                    <el-input v-model="activity.location" placeholder="地点" />
                  </el-form-item>
                </el-col>
              </el-row>
              
              <el-row :gutter="20">
                <el-col :span="6">
                  <el-form-item :label="`持续时间`">
                    <el-input v-model="activity.duration" placeholder="持续时间" />
                  </el-form-item>
                </el-col>
                <el-col :span="6">
                  <el-form-item :label="`类型`">
                    <el-input v-model="activity.type" placeholder="活动类型" />
                  </el-form-item>
                </el-col>
                <el-col :span="6">
                  <el-form-item :label="`费用`">
                    <el-input-number v-model="activity.cost" :min="0" placeholder="费用" style="width: 100%" />
                  </el-form-item>
                </el-col>
                <el-col :span="6" style="padding-left: 40px;">
                  <el-button @click="removeActivity(dayKey, actIndex)" type="danger" size="small" icon="Delete">删除该活动</el-button>
                </el-col>
              </el-row>
              
              <el-row :gutter="20">
                <el-col :span="24">
                  <el-form-item :label="`描述`">
                    <el-input 
                      v-model="activity.description" 
                      placeholder="活动描述" 
                      type="textarea" 
                      :rows="2"
                      resize="vertical"
                    />
                  </el-form-item>
                </el-col>
              </el-row>
            </div>
            
            <el-button @click="addActivity(dayKey)" type="primary" size="small" icon="Plus" color="#4f7942">添加活动</el-button>
          </div>
        </el-card>

        <!-- 操作按钮 -->
        <div class="form-actions">
          <el-button @click="goBack" size="large">取消</el-button>
          <el-button type="primary" @click="saveTrip" :loading="saving" size="large" color="#4f7942">保存</el-button>
        </div>
      </el-form>
    </div>

    <!-- 错误状态 -->
    <div v-else class="error-container">
      <el-result icon="error" title="加载失败" sub-title="无法加载行程数据">
        <template #extra>
          <el-button type="primary" @click="loadTripData" color="#4f7942">重试</el-button>
          <el-button @click="goBack">返回</el-button>
        </template>
      </el-result>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getTripById, updateTrip } from '@/api/itinerary'

const route = useRoute()
const router = useRouter()

// 响应式数据
const loading = ref(true)
const saving = ref(false)
const tripData = ref<any>(null)
const formRef = ref()

// 表单数据
const formData = reactive({
  title: '',
  destination: '',
  start_date: '',
  end_date: '',
  budget: 0,
  status: 'planning',
  itinerary: null as any
})

// 表单验证规则
const rules = {
  title: [
    { required: true, message: '请输入行程标题', trigger: 'blur' }
  ],
  destination: [
    { required: true, message: '请输入目的地', trigger: 'blur' }
  ],
  start_date: [
    { required: true, message: '请选择开始日期', trigger: 'change' }
  ],
  end_date: [
    { required: true, message: '请选择结束日期', trigger: 'change' }
  ]
}

// 加载行程数据
const loadTripData = async () => {
  try {
    loading.value = true
    const tripId = route.params.id as string
    const response = await getTripById(tripId)
    
    tripData.value = response
    
    // 填充表单数据
    formData.title = response.title
    formData.destination = response.destination
    formData.start_date = response.start_date.split('T')[0] // 格式化日期
    formData.end_date = response.end_date.split('T')[0]
    formData.budget = response.budget || 0
    formData.status = response.status
    formData.itinerary = response.itinerary
    
  } catch (error: any) {
    console.error('加载行程数据失败:', error)
    ElMessage.error('加载行程数据失败')
  } finally {
    loading.value = false
  }
}

// 保存行程
const saveTrip = async () => {
  try {
    // 表单验证
    await formRef.value.validate()
    
    saving.value = true
    const tripId = route.params.id as string
    
    await updateTrip(tripId, formData)
    
    ElMessage.success('行程保存成功')
    router.push('/dashboard')
    
  } catch (error: any) {
    console.error('保存行程失败:', error)
    if (error.response?.status === 422) {
      ElMessage.error('数据验证失败，请检查输入')
    } else {
      ElMessage.error('保存行程失败，请重试')
    }
  } finally {
    saving.value = false
  }
}

// 添加活动
const addActivity = (dayKey: string) => {
  if (formData.itinerary && formData.itinerary[dayKey]) {
    formData.itinerary[dayKey].activities.push({
      time: '',
      activity: '',
      location: '',
      duration: '',
      cost: 0,
      type: '',
      description: ''
    })
  }
}

// 删除活动
const removeActivity = async (dayKey: string, actIndex: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个活动吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    if (formData.itinerary && formData.itinerary[dayKey]) {
      formData.itinerary[dayKey].activities.splice(actIndex, 1)
    }
  } catch {
    // 用户取消删除
  }
}

// 返回上一页
const goBack = () => {
  router.push('/dashboard')
}

// 组件挂载时加载数据
onMounted(() => {
  loadTripData()
})
</script>

<style scoped>
.edit-trip-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.loading-container {
  padding: 40px;
}

.edit-form {
  background: #fff;
}

.form-section {
  margin-bottom: 20px;
}

.card-header {
  font-weight: 600;
  color: #303133;
}

.day-section {
  margin-bottom: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.day-title {
  font-size: 18px;
  font-weight: 600;
  color: #4f7942;
  margin: 0 0 20px 0;
  padding-bottom: 10px;
  border-bottom: 2px solid #4f7942;
}

.activity-item {
  margin-bottom: 20px;
  padding: 15px;
  background: #fff;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.activity-item .el-input {
  width: 100%;
}

.activity-item .el-form-item {
  margin-bottom: 15px;
}

.activity-item .el-form-item__label {
  font-weight: 500;
  color: #606266;
}
/* 
.delete-button-col {
  display: flex;
  align-items: flex-end;
  padding-top: 20px;
} */

.delete-button-col .el-button {
  margin-bottom: 22px;
}

.form-actions {
  text-align: center;
  padding: 30px 0;
  border-top: 1px solid #ebeef5;
  margin-top: 30px;
}

.form-actions .el-button {
  margin: 0 10px;
  min-width: 120px;
}

.error-container {
  padding: 40px;
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .edit-trip-container {
    padding: 10px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
  
  .day-section {
    padding: 15px;
  }
  
  .activity-item {
    padding: 10px;
  }
}
</style>