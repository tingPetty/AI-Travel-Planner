<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { generateItinerary, type ItineraryGenerateRequest } from '@/api/itinerary'
import { request } from '@/api/request'

const router = useRouter()
const loading = ref(false)

// 语音识别与智能填充
const isRecording = ref(false)
const recordingHint = ref('👆 点击开始录音，最长1分钟。请清晰描述目的地、日期、天数、预算与偏好。')
const recordSeconds = ref(0)
let recordTimer: number | null = null
let audioContext: AudioContext | null = null
let mediaStream: MediaStream | null = null
let sourceNode: MediaStreamAudioSourceNode | null = null
let processorNode: ScriptProcessorNode | null = null
let recordedChunks: Float32Array[] = []

const recognizedText = ref('')
const recognizing = ref(false)
const parsing = ref(false)
const waitingTips = ref('')

// 新建行程表单（原弹窗内容迁移为页面表单）
const newTripForm = reactive({
  title: '',
  destination: '',
  startDate: '',
  endDate: '',
  budget: null as number | null,
  travelers: 1,
  preferences: ''
})

const formatDateForAPI = (date: Date | string | null): string => {
  if (!date) return ''
  const dateObj = typeof date === 'string' ? new Date(date) : date
  if (isNaN(dateObj.getTime())) return ''
  const year = dateObj.getFullYear()
  const month = String(dateObj.getMonth() + 1).padStart(2, '0')
  const day = String(dateObj.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const resetForm = () => {
  Object.assign(newTripForm, {
    title: '',
    destination: '',
    startDate: '',
    endDate: '',
    budget: null,
    travelers: 1,
    preferences: ''
  })
}

const cancel = () => {
  router.push('/dashboard')
}

const submitTrip = async () => {
  try {
    if (!newTripForm.title || !newTripForm.destination || !newTripForm.startDate || !newTripForm.endDate) {
      ElMessage.warning('请填写必要信息')
      return
    }

    loading.value = true

    const requestData: ItineraryGenerateRequest = {
      title: newTripForm.title,
      destination: newTripForm.destination,
      start_date: formatDateForAPI(newTripForm.startDate),
      end_date: formatDateForAPI(newTripForm.endDate),
      budget: newTripForm.budget || undefined,
      preferences: newTripForm.preferences,
      travelers: newTripForm.travelers
    }

    ElMessage.info('正在调用AI生成行程，请稍候...')
    const response = await generateItinerary(requestData)

    if (response.success && response.data) {
      ElMessage.success('AI行程生成成功！')
      // 跳回仪表盘，仪表盘会在挂载时加载列表
      router.push('/dashboard')
    } else {
      ElMessage.error(response.message || 'AI行程生成失败')
    }
  } catch (error: any) {
    if (error.response?.status === 422) {
      let errorMessage = '请求数据格式错误，请检查输入信息'
      if (error.response.data?.detail) {
        if (Array.isArray(error.response.data.detail)) {
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
  } finally {
    loading.value = false
  }
}

// ---- 录音与编码为16k WAV ----
const startRecording = async () => {
  try {
    if (isRecording.value) return
    // 请求麦克风权限
    mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true })
    // 创建音频上下文（部分浏览器无法强制设置采样率，这里按设备采样率采集，稍后下采样到16k）
    audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
    sourceNode = audioContext.createMediaStreamSource(mediaStream)
    processorNode = audioContext.createScriptProcessor(4096, 1, 1)
    recordedChunks = []

    processorNode.onaudioprocess = (e: AudioProcessingEvent) => {
      const input = e.inputBuffer.getChannelData(0)
      // 拷贝一份数据，避免引用问题
      recordedChunks.push(new Float32Array(input))
    }
    sourceNode.connect(processorNode)
    processorNode.connect(audioContext.destination)

    isRecording.value = true
    recordingHint.value = '录音中…请自然描述（目的地、日期、天数、预算、偏好）'
    recordSeconds.value = 0
    if (recordTimer) {
      clearInterval(recordTimer)
    }
    recordTimer = window.setInterval(() => {
      recordSeconds.value += 1
      if (recordSeconds.value >= 60) {
        stopRecording()
      }
    }, 1000) as unknown as number
  } catch (err: any) {
    ElMessage.error('无法开始录音，请检查麦克风权限')
  }
}

const stopRecording = async () => {
  try {
    if (!isRecording.value) return
    isRecording.value = false
    recordingHint.value = '录音结束，正在处理音频并进行识别…'
    if (recordTimer) {
      clearInterval(recordTimer)
      recordTimer = null
    }
    // 断开音频节点
    try {
      processorNode && processorNode.disconnect()
      sourceNode && sourceNode.disconnect()
    } catch {}
    // 停止媒体轨道
    if (mediaStream) {
      mediaStream.getTracks().forEach(t => t.stop())
    }
    // 关闭音频上下文
    try { await audioContext?.close() } catch {}

    // 合并与下采样为16k
    const inputSampleRate = audioContext?.sampleRate || 44100
    const merged = mergeFloat32Arrays(recordedChunks)
    const downsampled = downsampleBuffer(merged, inputSampleRate, 16000)
    const wavBlob = encodeWAV(downsampled, 16000)

    // 上传并识别
    await uploadAndRecognize(wavBlob)
  } catch (err: any) {
    ElMessage.error('处理音频失败，请重试')
  } finally {
    recordingHint.value = '点击开始录音，最长1分钟。请清晰描述目的地、日期、天数、预算与偏好。'
  }
}

function mergeFloat32Arrays(chunks: Float32Array[]) {
  const length = chunks.reduce((sum, arr) => sum + arr.length, 0)
  const result = new Float32Array(length)
  let offset = 0
  for (const arr of chunks) {
    result.set(arr, offset)
    offset += arr.length
  }
  return result
}

function downsampleBuffer(buffer: Float32Array, sampleRate: number, outSampleRate: number) {
  if (outSampleRate === sampleRate) {
    return buffer
  }
  if (outSampleRate > sampleRate) {
    // 不支持上采样
    return buffer
  }
  const ratio = sampleRate / outSampleRate
  const newLength = Math.round(buffer.length / ratio)
  const result = new Float32Array(newLength)
  let offsetResult = 0
  let offsetBuffer = 0
  while (offsetResult < result.length) {
    // 简单取样本点（可改为均值以更平滑）
    result[offsetResult] = buffer[Math.floor(offsetBuffer)]
    offsetResult++
    offsetBuffer += ratio
  }
  return result
}

function encodeWAV(samples: Float32Array, sampleRate: number) {
  // 转为16位PCM
  const buffer = new ArrayBuffer(44 + samples.length * 2)
  const view = new DataView(buffer)

  // 写入WAV头
  writeString(view, 0, 'RIFF')
  view.setUint32(4, 36 + samples.length * 2, true)
  writeString(view, 8, 'WAVE')
  writeString(view, 12, 'fmt ')
  view.setUint32(16, 16, true) // PCM chunk size
  view.setUint16(20, 1, true) // 格式：PCM
  view.setUint16(22, 1, true) // 声道数：单声道
  view.setUint32(24, sampleRate, true)
  view.setUint32(28, sampleRate * 2, true) // 字节率 = 采样率 * 声道 * 位深/8
  view.setUint16(32, 2, true) // Block align = 声道 * 位深/8
  view.setUint16(34, 16, true) // 位深：16位
  writeString(view, 36, 'data')
  view.setUint32(40, samples.length * 2, true)

  // PCM数据
  floatTo16BitPCM(view, 44, samples)
  return new Blob([view], { type: 'audio/wav' })
}

function writeString(view: DataView, offset: number, str: string) {
  for (let i = 0; i < str.length; i++) {
    view.setUint8(offset + i, str.charCodeAt(i))
  }
}

function floatTo16BitPCM(view: DataView, offset: number, input: Float32Array) {
  for (let i = 0; i < input.length; i++, offset += 2) {
    const s = Math.max(-1, Math.min(1, input[i]))
    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true)
  }
}

// ---- 上传至后端进行语音识别 ----
const uploadAndRecognize = async (blob: Blob) => {
  try {
    recognizing.value = true
    waitingTips.value = '正在上传音频并进行语音识别，请稍候…'
    const form = new FormData()
    form.append('file', blob, 'recording.wav')
    const res = await request.post('/api/speech/recognize?format=wav&sample_rate=16000', form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    // 在浏览器控制台打印识别结果详情
    console.log('🎙️ ASR识别结果详情:', res)
    
    if (res?.success) {
      console.log('✅ 识别成功，文本:', res.recognized_text)
      recognizedText.value = res.recognized_text
      ElMessage.success('语音识别成功')
      // 自动调用解析并填充
      await parseTextAndFill()
    } else {
      console.error('❌ ASR识别失败:', {
        success: res?.success,
        error: res?.error,
        status_code: res?.status_code,
        raw: res?.raw
      })
      ElMessage.error('语音识别失败')
    }
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '语音识别接口调用失败')
  } finally {
    recognizing.value = false
    waitingTips.value = ''
  }
}

// ---- 调用文本解析接口并填充表单 ----
const parseTextAndFill = async () => {
  if (!recognizedText.value || !recognizedText.value.trim()) {
    ElMessage.warning('识别文本为空，无法解析')
    return
  }
  try {
    parsing.value = true
    waitingTips.value = '正在解析文本并自动填充，请稍候 5-10 秒…'
    const parsed = await request.post('/api/text/parse', { text: recognizedText.value })
    // 根据返回字段填充
    if (parsed) {
      newTripForm.title = parsed.title || newTripForm.title
      newTripForm.destination = parsed.destination || newTripForm.destination
      // 日期填充：优先解析出的值
      if (parsed.start_date) {
        newTripForm.startDate = parsed.start_date
      }
      if (parsed.end_date) {
        newTripForm.endDate = parsed.end_date
      }
      if (parsed.budget !== null && parsed.budget !== undefined) {
        newTripForm.budget = Number(parsed.budget)
      }
      if (parsed.travelers !== null && parsed.travelers !== undefined) {
        newTripForm.travelers = Number(parsed.travelers)
      }
      if (parsed.preferences) {
        newTripForm.preferences = parsed.preferences
      }
      ElMessage.success('已根据识别文本自动填充，您可继续手动修改')
    }
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '文本解析失败，请稍后重试')
  } finally {
    parsing.value = false
    waitingTips.value = ''
  }
}
</script>

<template>
  <div class="new-trip-page">
    <div class="page-header">
      <h2>新建旅行计划</h2>
    </div>

    <!-- 语音识别与智能填充模块（绿色ins风格） -->
    <div class="speech-section" :class="{ 'is-loading': recognizing || parsing }" v-loading="recognizing || parsing">
      <div class="speech-header">
        <h3>🎙️ 语音识别与智能填充</h3>
        <p class="subtitle">支持语音一键填写表单，仍可手动修改</p>
      </div>
      <div class="speech-actions">
        <el-button
          :type="isRecording ? 'danger' : 'primary'"
          :color="isRecording ? '#d9534f' : '#4f7942'"
          @click="isRecording ? stopRecording() : startRecording()"
        >
          {{ isRecording ? '结束录音' : '开始进行语音识别' }}
        </el-button>
        <span class="record-timer" v-if="isRecording">录音中：{{ Math.floor(recordSeconds/60) }}分{{ recordSeconds%60 }}秒</span>
      </div>
      <p class="hint">{{ recordingHint }}</p>

      <div class="template-box">
        <div class="template-title">语音模板：</div>
        <div class="template-content">我想去[目的地]旅游，出行日期是[日期]，计划玩[天数]天，出行人数是[人数]，预算是[钱数]，我喜欢[旅游偏好]</div>
        <div class="template-title" style="margin-top:8px">示例：</div>
        <div class="template-content">我想去日本，出行日期是10.1，计划玩 5 天，出行人数 2 人，预算 1 万元，喜欢美食和动漫，带孩子。</div>
      </div>

      <div class="recognized-box" v-if="recognizedText || recognizing">
        <div class="recognized-title">识别文本：</div>
        <el-input type="textarea" v-model="recognizedText" :rows="4" placeholder="语音识别结果会显示在这里，可修改后重新解析" />
        <div class="recognized-actions">
          <el-button :disabled="parsing" @click="parseTextAndFill" color="#4f7942">重新解析并填充</el-button>
          <span class="waiting-tips" v-if="waitingTips">{{ waitingTips }}</span>
        </div>
      </div>
    </div>

    <el-form :model="newTripForm" label-width="100px" class="new-trip-form">
      <el-form-item label="行程标题" required>
        <el-input v-model="newTripForm.title" placeholder="给您的旅行起个名字" />
      </el-form-item>

      <el-form-item label="目的地" required>
        <el-input v-model="newTripForm.destination" placeholder="您想去哪里？" />
      </el-form-item>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="开始日期" required>
            <el-date-picker v-model="newTripForm.startDate" type="date" placeholder="选择开始日期" style="width: 100%" value-format="YYYY-MM-DD" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="结束日期" required>
            <el-date-picker v-model="newTripForm.endDate" type="date" placeholder="选择结束日期" style="width: 100%" value-format="YYYY-MM-DD" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="预算">
            <el-input-number v-model="newTripForm.budget" :min="0" :step="100" placeholder="预算金额" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="人数">
            <el-input-number v-model="newTripForm.travelers" :min="1" :max="20" style="width: 100%" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="旅行偏好" prop="travel_style">
        <el-input type="textarea" v-model="newTripForm.preferences" placeholder="请输入您的旅行风格或特殊需求，如：喜欢自由行、希望深度体验当地文化等" :rows="3" />
      </el-form-item>

      <div class="form-actions">
        <el-button @click="cancel" :disabled="loading">取消</el-button>
        <el-button type="primary" @click="submitTrip" color="#4f7942" :loading="loading" :disabled="loading">
          {{ loading ? '正在生成行程...' : '创建并生成行程' }}
        </el-button>
      </div>
    </el-form>
  </div>
  
</template>

<style scoped>
.new-trip-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
}
.page-header {
  margin-bottom: 24px;
}
.page-header h2 {
  margin: 0;
  color: #2c3e50;
  font-size: 24px;
  font-weight: 600;
}

.speech-section {
  background: #f6fbf5;
  border: 1px solid #e4f0e8;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
}
.speech-header h3 {
  margin: 0 0 4px 0;
  color: #4f7942;
}
.speech-header .subtitle {
  margin: 0;
  color: #6b8f6a;
  font-size: 13px;
  font-weight: 700;
}
.speech-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 12px;
}
.record-timer {
  color: #4f7942;
}
.hint {
  margin-top: 8px;
  color: #6b8f6a;
}
.template-box {
  margin-top: 12px;
  background: #ffffff;
  border: 1px dashed #cfe3cf;
  border-radius: 8px;
  padding: 12px;
}
.template-title {
  color: #4f7942;
  font-weight: 600;
}
.template-content {
  color: #2c3e50;
}
.recognized-box {
  margin-top: 12px;
}
.recognized-title {
  color: #4f7942;
  margin-bottom: 6px;
}
.recognized-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
}
.waiting-tips {
  color: #6b8f6a;
}
.new-trip-form {
  background: #fff;
  padding: 20px;
  border: 1px solid #edf2ed;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(143, 188, 143, 0.08);
}
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>