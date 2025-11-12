<template>
  <el-dialog v-model="visible" title="新建费用记录" width="600px" :close-on-click-modal="false">
    <!-- 语音识别与智能填充 -->
    <div class="speech-section" :class="{ 'is-loading': recognizing || analyzing }" v-loading="recognizing || analyzing">
      <div class="speech-header">
        <h3>🎙️ 语音识别与智能填充</h3>
        <p class="subtitle">支持语音一键填写，仍可手动修改</p>
      </div>
      <div class="speech-actions">
        <el-button
          :type="isRecording ? 'danger' : 'primary'"
          :color="isRecording ? '#d9534f' : '#4f7942'"
          @click="isRecording ? stopRecording() : startRecording()"
        >
          {{ isRecording ? '结束录音' : '开始语音识别' }}
        </el-button>
        <span class="record-timer" v-if="isRecording">录音中：{{ Math.floor(recordSeconds/60) }}分{{ recordSeconds%60 }}秒</span>
      </div>
      <p class="hint">{{ recordingHint }}</p>

      <div class="examples">
        <span class="ex-title">示例：</span>
        <span class="ex-item">10.1吃肯德基花了50</span>
        <span class="ex-item">滑雪花了100</span>
      </div>

      <div class="recognized-box" v-if="recognizedText || recognizing">
        <div class="recognized-title">识别文本：</div>
        <el-input type="textarea" v-model="recognizedText" :rows="3" placeholder="语音识别结果会显示在这里，可修改后再智能填充" />
        <div class="recognized-actions">
          <el-button :disabled="analyzing" @click="aiExtractAndFill" color="#4f7942">重新解析语音并填充表单</el-button>
          <span class="waiting-tips" v-if="waitingTips">{{ waitingTips }}</span>
        </div>
      </div>
    </div>

    <el-form :model="form" :rules="rules" ref="formRef" label-width="90px">
      <el-form-item label="金额" prop="amount">
        <el-input-number v-model="form.amount" :min="0" :step="1" :precision="2" controls-position="right" />
      </el-form-item>
      <el-form-item label="类别" prop="category">
        <el-select v-model="form.category" placeholder="请选择类别">
          <el-option label="交通" value="transport" />
          <el-option label="住宿" value="accommodation" />
          <el-option label="食物" value="food" />
          <el-option label="娱乐" value="entertainment" />
          <el-option label="购物" value="shopping" />
          <el-option label="其他" value="other" />
        </el-select>
      </el-form-item>
      <el-form-item label="描述" prop="description">
        <el-input v-model="form.description" placeholder="例如：打车到酒店、午餐"/>
      </el-form-item>
      <el-form-item label="日期" prop="expense_date">
        <el-date-picker v-model="form.expense_date" type="date" placeholder="选择日期" format="YYYY-MM-DD" value-format="YYYY-MM-DD"/>
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="onCancel">取消</el-button>
        <el-button type="primary" color="#4f7942" :loading="submitting" @click="onSubmit">保存</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { addExpense } from '@/api/budget'
import { request } from '@/api/request'

const props = defineProps<{ visible: boolean; tripId: number | null }>()
const emits = defineEmits<{ (e: 'update:visible', v: boolean): void; (e: 'created'): void }>()

const visible = ref(props.visible)
watch(() => props.visible, v => (visible.value = v))
watch(visible, v => emits('update:visible', v))

const formRef = ref<FormInstance>()
const submitting = ref(false)

const form = reactive({
  amount: 0,
  category: '' as any,
  description: '',
  expense_date: ''
})

const rules: FormRules = {
  amount: [{ required: true, message: '请输入金额', trigger: 'blur' }],
  category: [{ required: true, message: '请选择类别', trigger: 'change' }],
  expense_date: [{ required: true, message: '请选择日期', trigger: 'change' }]
}

// 语音识别相关状态
const isRecording = ref(false)
const recordingHint = ref('👆 点击开始录音，最长1分钟。直接说支出内容和金额即可。')
const recordSeconds = ref(0)
let recordTimer: number | null = null
let audioContext: AudioContext | null = null
let mediaStream: MediaStream | null = null
let sourceNode: MediaStreamAudioSourceNode | null = null
let processorNode: ScriptProcessorNode | null = null
let recordedChunks: Float32Array[] = []

const recognizedText = ref('')
const recognizing = ref(false)
const analyzing = ref(false)
const waitingTips = ref('')

const startRecording = async () => {
  try {
    if (isRecording.value) return
    mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true })
    audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
    sourceNode = audioContext.createMediaStreamSource(mediaStream)
    processorNode = audioContext.createScriptProcessor(4096, 1, 1)
    recordedChunks = []

    processorNode.onaudioprocess = (e: AudioProcessingEvent) => {
      const input = e.inputBuffer.getChannelData(0)
      recordedChunks.push(new Float32Array(input))
    }
    sourceNode.connect(processorNode)
    processorNode.connect(audioContext.destination)

    isRecording.value = true
    recordingHint.value = '录音中…请自然描述（日期可简写，如10.1；项目与金额）'
    recordSeconds.value = 0
    if (recordTimer) clearInterval(recordTimer)
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
    if (recordTimer) { clearInterval(recordTimer); recordTimer = null }
    try { processorNode && processorNode.disconnect(); sourceNode && sourceNode.disconnect() } catch {}
    if (mediaStream) { mediaStream.getTracks().forEach(t => t.stop()) }
    try { await audioContext?.close() } catch {}

    // 合并与下采样为16k
    const inputSampleRate = audioContext?.sampleRate || 44100
    const merged = mergeFloat32Arrays(recordedChunks)
    const downsampled = downsampleBuffer(merged, inputSampleRate, 16000)
    const wavBlob = encodeWAV(downsampled, 16000)

    await uploadAndRecognize(wavBlob)
  } catch (err: any) {
    ElMessage.error('处理音频失败，请重试')
  } finally {
    recordingHint.value = '点击开始录音，最长1分钟。直接说支出内容和金额即可。'
  }
}

function mergeFloat32Arrays(chunks: Float32Array[]) {
  const length = chunks.reduce((sum, arr) => sum + arr.length, 0)
  const result = new Float32Array(length)
  let offset = 0
  for (const arr of chunks) { result.set(arr, offset); offset += arr.length }
  return result
}

function downsampleBuffer(buffer: Float32Array, sampleRate: number, outSampleRate: number) {
  if (outSampleRate === sampleRate) return buffer
  if (outSampleRate > sampleRate) return buffer
  const ratio = sampleRate / outSampleRate
  const newLength = Math.round(buffer.length / ratio)
  const result = new Float32Array(newLength)
  let offsetResult = 0
  let offsetBuffer = 0
  while (offsetResult < result.length) {
    result[offsetResult] = buffer[Math.floor(offsetBuffer)]
    offsetResult++
    offsetBuffer += ratio
  }
  return result
}

function encodeWAV(samples: Float32Array, sampleRate: number) {
  const buffer = new ArrayBuffer(44 + samples.length * 2)
  const view = new DataView(buffer)
  writeString(view, 0, 'RIFF')
  view.setUint32(4, 36 + samples.length * 2, true)
  writeString(view, 8, 'WAVE')
  writeString(view, 12, 'fmt ')
  view.setUint32(16, 16, true)
  view.setUint16(20, 1, true)
  view.setUint16(22, 1, true)
  view.setUint32(24, sampleRate, true)
  view.setUint32(28, sampleRate * 2, true)
  view.setUint16(32, 2, true)
  view.setUint16(34, 16, true)
  writeString(view, 36, 'data')
  view.setUint32(40, samples.length * 2, true)
  floatTo16BitPCM(view, 44, samples)
  return new Blob([view], { type: 'audio/wav' })
}

function writeString(view: DataView, offset: number, str: string) {
  for (let i = 0; i < str.length; i++) view.setUint8(offset + i, str.charCodeAt(i))
}

function floatTo16BitPCM(view: DataView, offset: number, input: Float32Array) {
  for (let i = 0; i < input.length; i++, offset += 2) {
    const s = Math.max(-1, Math.min(1, input[i]))
    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true)
  }
}

// 上传到后端进行语音识别
const uploadAndRecognize = async (blob: Blob) => {
  try {
    recognizing.value = true
    waitingTips.value = '正在上传音频并进行语音识别，请稍候…'
    const formData = new FormData()
    formData.append('file', blob, 'expense.wav')
    const res = await request.post('/api/speech/recognize?format=wav&sample_rate=16000', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    // 在浏览器控制台打印识别结果详情
    console.log('🎙️ ASR识别结果详情:', res)
    
    if (res?.success) {
      console.log('✅ 识别成功，文本:', res.recognized_text)
      recognizedText.value = res.recognized_text
      ElMessage.success('语音识别成功')
      // 自动调用AI提取并填充
      await aiExtractAndFill()
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

// 中文类别到英文枚举映射（保持后端兼容）
const ZH_TO_EN_CATEGORY: Record<string, string> = {
  '交通': 'transport',
  '住宿': 'accommodation',
  '食物': 'food',
  '餐饮': 'food',
  '娱乐': 'entertainment',
  '购物': 'shopping',
  '其他': 'other'
}

// 调用预算AI提取接口并填充表单
const aiExtractAndFill = async () => {
  if (!recognizedText.value || !recognizedText.value.trim()) {
    ElMessage.warning('识别文本为空，无法智能填充')
    return
  }
  try {
    analyzing.value = true
    waitingTips.value = '正在解析并填充费用信息…'
    const parsed = await request.post('/api/budget/ai-extract', { text: recognizedText.value })
    if (parsed) {
      if (parsed.amount !== null && parsed.amount !== undefined) form.amount = Number(parsed.amount)
      if (parsed.category) form.category = ZH_TO_EN_CATEGORY[parsed.category] || form.category
      if (parsed.description) form.description = parsed.description
      if (parsed.expense_date) form.expense_date = parsed.expense_date
      ElMessage.success('已根据识别文本自动填充，您可继续手动修改')
    }
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '智能填充失败，请稍后重试')
  } finally {
    analyzing.value = false
    waitingTips.value = ''
  }
}

function resetForm() {
  form.amount = 0
  form.category = ''
  form.description = ''
  form.expense_date = ''
}

// 清除语音识别结果
function clearVoiceRecognition() {
  recognizedText.value = ''
  recognizing.value = false
  analyzing.value = false
  waitingTips.value = ''
  recordingHint.value = '👆 点击开始录音，最长1分钟。直接说支出内容和金额即可。'
  
  // 如果正在录音，停止录音
  if (isRecording.value) {
    isRecording.value = false
    if (recordTimer) {
      clearInterval(recordTimer)
      recordTimer = null
    }
    recordSeconds.value = 0
    
    // 清理音频资源
    try {
      processorNode && processorNode.disconnect()
      sourceNode && sourceNode.disconnect()
    } catch {}
    if (mediaStream) {
      mediaStream.getTracks().forEach(t => t.stop())
      mediaStream = null
    }
    try {
      audioContext?.close()
      audioContext = null
    } catch {}
  }
}

// 监听弹窗关闭，清除语音识别结果
watch(() => props.visible, (newVal, oldVal) => {
  if (oldVal && !newVal) {
    // 弹窗从显示变为隐藏时，清除语音识别结果
    clearVoiceRecognition()
  }
})

function onCancel() {
  visible.value = false
  resetForm()
  clearVoiceRecognition()
}

async function onSubmit() {
  if (!props.tripId) {
    ElMessage.error('请先选择行程')
    return
  }
  await formRef.value?.validate()
  submitting.value = true
  try {
    await addExpense({
      trip_id: props.tripId,
      amount: form.amount,
      category: form.category,
      description: form.description || undefined,
      expense_date: form.expense_date
    })
    ElMessage.success('新增费用成功')
    visible.value = false
    emits('created')
    resetForm()
    clearVoiceRecognition()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '新增失败')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
/* 绿色语音识别模块样式 */
.speech-section {
  background: #f6fbf5;
  border: 1px solid #e4f0e8;
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 12px;
}
.speech-header h3 {
  margin: 0 0 4px 0;
  color: #4f7942;
}
.speech-header .subtitle {
  margin: 0;
  color: #6b8f6a;
  font-size: 12px;
  font-weight: 700;
}
.speech-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
}
.record-timer { color: #4f7942; }
.hint { margin-top: 6px; color: #6b8f6a; }
.examples { margin-top: 8px; display: flex; gap: 10px; align-items: center; }
.ex-title { color: #4f7942; font-weight: 600; }
.ex-item { color: #2c3e50; background:#fff; border:1px dashed #cfe3cf; border-radius:6px; padding:2px 6px; }
.recognized-box { margin-top: 10px; }
.recognized-title { color: #4f7942; margin-bottom: 6px; }
.recognized-actions { display: flex; align-items: center; gap: 12px; margin-top: 8px; }
.waiting-tips { color: #6b8f6a; }
</style>