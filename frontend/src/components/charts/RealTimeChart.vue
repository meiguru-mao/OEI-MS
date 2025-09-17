<template>
  <div class="real-time-chart">
    <div class="chart-header">
      <h3>{{ title }}</h3>
      <div class="chart-controls">
        <el-select v-model="selectedSensor" placeholder="选择传感器" @change="onSensorChange">
          <el-option
            v-for="sensor in sensors"
            :key="sensor.id"
            :label="sensor.name"
            :value="sensor.id"
          />
        </el-select>
        <el-button-group>
          <el-button :type="isRealTime ? 'primary' : 'default'" @click="toggleRealTime">
            {{ isRealTime ? '实时' : '暂停' }}
          </el-button>
          <el-button @click="clearChart">清空</el-button>
        </el-button-group>
      </div>
    </div>
    
    <div ref="chartContainer" class="chart-container" :style="{ height: height + 'px' }"></div>
    
    <div class="chart-info">
      <div class="info-item">
        <span class="label">当前值:</span>
        <span class="value" :class="getValueClass(currentValue)">{{ formatValue(currentValue) }}</span>
      </div>
      <div class="info-item">
        <span class="label">更新时间:</span>
        <span class="value">{{ lastUpdateTime }}</span>
      </div>
      <div class="info-item">
        <span class="label">数据点数:</span>
        <span class="value">{{ dataPoints.length }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { ApiService, WebSocketService } from '@/services/api'
import { formatDateTime } from '@/utils/date'

interface Props {
  title?: string
  height?: number
  maxDataPoints?: number
  sensorId?: number
  chartType?: 'line' | 'area' | 'bar'
  theme?: 'light' | 'dark'
}

const props = withDefaults(defineProps<Props>(), {
  title: '实时数据监控',
  height: 400,
  maxDataPoints: 100,
  chartType: 'line',
  theme: 'light'
})

const emit = defineEmits<{
  sensorChange: [sensorId: number]
  dataUpdate: [data: any]
}>()

// 响应式数据
const chartContainer = ref<HTMLDivElement>()
const chart = ref<echarts.ECharts>()
const sensors = ref<any[]>([])
const selectedSensor = ref<number>(props.sensorId || 0)
const isRealTime = ref(true)
const dataPoints = ref<any[]>([])
const currentValue = ref<number | null>(null)
const lastUpdateTime = ref<string>('')

// WebSocket服务
const wsService = new WebSocketService()

// 图表配置
const chartOption = ref({
  title: {
    show: false
  },
  tooltip: {
    trigger: 'axis',
    formatter: (params: any) => {
      const data = params[0]
      return `
        <div>
          <div>时间: ${data.axisValue}</div>
          <div>数值: ${data.value[1]}</div>
        </div>
      `
    }
  },
  legend: {
    show: false
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'time',
    splitLine: {
      show: false
    },
    axisLabel: {
      formatter: (value: number) => {
        const date = new Date(value)
        return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}:${date.getSeconds().toString().padStart(2, '0')}`
      }
    }
  },
  yAxis: {
    type: 'value',
    splitLine: {
      lineStyle: {
        color: '#f0f0f0'
      }
    }
  },
  series: [
    {
      name: '传感器数据',
      type: props.chartType,
      smooth: true,
      symbol: 'none',
      sampling: 'lttb',
      itemStyle: {
        color: '#409EFF'
      },
      areaStyle: props.chartType === 'area' ? {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
          { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
        ])
      } : undefined,
      data: []
    }
  ],
  animation: false
})

// 生命周期
onMounted(async () => {
  await initChart()
  await loadSensors()
  await connectWebSocket()
  
  if (selectedSensor.value) {
    await loadInitialData()
  }
})

onUnmounted(() => {
  if (chart.value) {
    chart.value.dispose()
  }
  wsService.disconnect()
})

// 监听器
watch(() => props.theme, () => {
  if (chart.value) {
    chart.value.dispose()
    initChart()
  }
})

watch(selectedSensor, (newSensorId) => {
  if (newSensorId) {
    clearChart()
    loadInitialData()
    emit('sensorChange', newSensorId)
  }
})

// 方法
const initChart = async () => {
  await nextTick()
  if (chartContainer.value) {
    chart.value = echarts.init(chartContainer.value, props.theme)
    chart.value.setOption(chartOption.value)
    
    // 监听窗口大小变化
    window.addEventListener('resize', handleResize)
  }
}

const handleResize = () => {
  if (chart.value) {
    chart.value.resize()
  }
}

const loadSensors = async () => {
  try {
    const response = await ApiService.getSensors()
    sensors.value = response.data || []
    
    if (!selectedSensor.value && sensors.value.length > 0) {
      selectedSensor.value = sensors.value[0].id
    }
  } catch (error) {
    console.error('加载传感器列表失败:', error)
    ElMessage.error('加载传感器列表失败')
  }
}

const loadInitialData = async () => {
  if (!selectedSensor.value) return
  
  try {
    const endTime = new Date()
    const startTime = new Date(endTime.getTime() - 30 * 60 * 1000) // 最近30分钟
    
    const response = await ApiService.getSensorHistoryData(selectedSensor.value, {
      start_time: startTime.toISOString(),
      end_time: endTime.toISOString(),
      interval: '1m'
    })
    
    const historyData = response.data || []
    dataPoints.value = historyData.map((item: any) => [
      new Date(item.timestamp).getTime(),
      item.value
    ])
    
    updateChart()
    
    if (historyData.length > 0) {
      const latest = historyData[historyData.length - 1]
      currentValue.value = latest.value
      lastUpdateTime.value = formatDateTime(new Date(latest.timestamp))
    }
  } catch (error) {
    console.error('加载历史数据失败:', error)
    ElMessage.error('加载历史数据失败')
  }
}

const connectWebSocket = async () => {
  try {
    await wsService.connect()
    
    // 监听传感器数据更新
    wsService.on('sensor_data', (message: any) => {
      if (isRealTime.value && message.sensor_id === selectedSensor.value) {
        addDataPoint(message.data)
      }
    })
    
    // 监听连接状态
    wsService.on('connected', () => {
      console.log('WebSocket已连接')
    })
    
    wsService.on('disconnected', () => {
      console.log('WebSocket已断开')
    })
    
  } catch (error) {
    console.error('WebSocket连接失败:', error)
    ElMessage.warning('实时数据连接失败，将使用轮询模式')
    startPolling()
  }
}

const startPolling = () => {
  const pollInterval = setInterval(async () => {
    if (!isRealTime.value || !selectedSensor.value) return
    
    try {
      const response = await ApiService.getSensorLatestData(selectedSensor.value)
      if (response.data) {
        addDataPoint(response.data)
      }
    } catch (error) {
      console.error('轮询数据失败:', error)
    }
  }, 5000) // 每5秒轮询一次
  
  onUnmounted(() => {
    clearInterval(pollInterval)
  })
}

const addDataPoint = (data: any) => {
  const timestamp = new Date(data.timestamp).getTime()
  const value = data.value
  
  dataPoints.value.push([timestamp, value])
  
  // 限制数据点数量
  if (dataPoints.value.length > props.maxDataPoints) {
    dataPoints.value.shift()
  }
  
  currentValue.value = value
  lastUpdateTime.value = formatDateTime(new Date(timestamp))
  
  updateChart()
  emit('dataUpdate', data)
}

const updateChart = () => {
  if (chart.value) {
    chart.value.setOption({
      series: [{
        data: dataPoints.value
      }]
    })
  }
}

const onSensorChange = () => {
  if (selectedSensor.value) {
    clearChart()
    loadInitialData()
  }
}

const toggleRealTime = () => {
  isRealTime.value = !isRealTime.value
  
  if (isRealTime.value) {
    ElMessage.success('已开启实时监控')
  } else {
    ElMessage.info('已暂停实时监控')
  }
}

const clearChart = () => {
  dataPoints.value = []
  currentValue.value = null
  lastUpdateTime.value = ''
  updateChart()
}

const formatValue = (value: number | null): string => {
  if (value === null) return '--'
  return value.toFixed(2)
}

const getValueClass = (value: number | null): string => {
  if (value === null) return ''
  
  // 这里可以根据传感器类型和阈值来判断状态
  if (value > 80) return 'danger'
  if (value > 60) return 'warning'
  return 'normal'
}
</script>

<style scoped>
.real-time-chart {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
}

.chart-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.chart-container {
  width: 100%;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
}

.chart-info {
  display: flex;
  justify-content: space-around;
  margin-top: 16px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 4px;
}

.info-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.info-item .label {
  font-size: 12px;
  color: #666;
}

.info-item .value {
  font-size: 16px;
  font-weight: 600;
}

.value.normal {
  color: #67c23a;
}

.value.warning {
  color: #e6a23c;
}

.value.danger {
  color: #f56c6c;
}

@media (max-width: 768px) {
  .chart-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .chart-controls {
    justify-content: center;
  }
  
  .chart-info {
    flex-direction: column;
    gap: 8px;
  }
  
  .info-item {
    flex-direction: row;
    justify-content: space-between;
  }
}
</style>