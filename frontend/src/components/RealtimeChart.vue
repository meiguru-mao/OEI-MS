<template>
  <div class="realtime-chart">
    <div class="chart-header">
      <div class="chart-title">
        <h3>{{ title }}</h3>
        <p class="chart-subtitle" v-if="subtitle">{{ subtitle }}</p>
      </div>
      <div class="chart-controls">
        <select v-model="timeRange" @change="onTimeRangeChange" class="time-range-select">
          <option value="1h">最近1小时</option>
          <option value="6h">最近6小时</option>
          <option value="24h">最近24小时</option>
          <option value="7d">最近7天</option>
          <option value="30d">最近30天</option>
        </select>
        <button @click="toggleAutoRefresh" class="refresh-btn" :class="{ active: autoRefresh }">
          <span class="refresh-icon">🔄</span>
          {{ autoRefresh ? '停止刷新' : '自动刷新' }}
        </button>
        <button @click="refreshData" class="refresh-btn">
          <span class="refresh-icon">↻</span>
          刷新
        </button>
      </div>
    </div>
    
    <div class="chart-container" ref="chartContainer">
      <div v-if="loading" class="chart-loading">
        <div class="loading-spinner"></div>
        <p>加载数据中...</p>
      </div>
      <div v-else-if="error" class="chart-error">
        <p>{{ error }}</p>
        <button @click="refreshData" class="retry-btn">重试</button>
      </div>
      <div v-else-if="!hasData" class="chart-no-data">
        <p>暂无数据</p>
      </div>
    </div>
    
    <div class="chart-stats" v-if="hasData && stats">
      <div class="stat-item">
        <span class="stat-label">当前值:</span>
        <span class="stat-value">{{ formatValue(stats.current) }} {{ unit }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">平均值:</span>
        <span class="stat-value">{{ formatValue(stats.average) }} {{ unit }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">最大值:</span>
        <span class="stat-value">{{ formatValue(stats.max) }} {{ unit }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">最小值:</span>
        <span class="stat-value">{{ formatValue(stats.min) }} {{ unit }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed, nextTick } from 'vue'
import * as echarts from 'echarts'
import type { ECharts } from 'echarts'
import type { SensorData } from '@/services/api'

interface Props {
  title: string
  subtitle?: string
  sensorIds: string[]
  unit?: string
  height?: string
  showLegend?: boolean
  showGrid?: boolean
  lineSmooth?: boolean
  colors?: string[]
}

interface Emits {
  'data-request': [params: {
    sensor_ids: string[]
    start_time: string
    end_time: string
    limit?: number
    aggregation?: string
    interval?: string
  }]
  'time-range-change': [range: string]
}

const props = withDefaults(defineProps<Props>(), {
  height: '400px',
  showLegend: true,
  showGrid: true,
  lineSmooth: false,
  colors: () => ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#06b6d4']
})

const emit = defineEmits<Emits>()

// 响应式数据
const chartContainer = ref<HTMLDivElement>()
const chart = ref<ECharts>()
const timeRange = ref('1h')
const autoRefresh = ref(false)
const loading = ref(false)
const error = ref<string | null>(null)
const chartData = ref<SensorData[]>([])
const refreshTimer = ref<number>()

// 计算属性
const hasData = computed(() => chartData.value.length > 0)

const stats = computed(() => {
  if (!hasData.value) return null
  
  const values = chartData.value.map(d => d.value).filter(v => typeof v === 'number')
  if (values.length === 0) return null
  
  const current = values[values.length - 1]
  const sum = values.reduce((a, b) => a + b, 0)
  const average = sum / values.length
  const max = Math.max(...values)
  const min = Math.min(...values)
  
  return { current, average, max, min }
})

// 方法
const initChart = () => {
  if (!chartContainer.value) return
  
  chart.value = echarts.init(chartContainer.value)
  
  const option = {
    title: {
      show: false
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985'
        }
      },
      formatter: (params: any) => {
        if (!params || params.length === 0) return ''
        
        const time = new Date(params[0].axisValue).toLocaleString('zh-CN')
        let content = `<div style="margin-bottom: 4px;">${time}</div>`
        
        params.forEach((param: any) => {
          const color = param.color
          const name = param.seriesName
          const value = formatValue(param.value[1])
          content += `
            <div style="display: flex; align-items: center; margin-bottom: 2px;">
              <span style="display: inline-block; width: 10px; height: 10px; background-color: ${color}; border-radius: 50%; margin-right: 8px;"></span>
              <span style="margin-right: 8px;">${name}:</span>
              <span style="font-weight: bold;">${value} ${props.unit || ''}</span>
            </div>
          `
        })
        
        return content
      }
    },
    legend: {
      show: props.showLegend,
      top: 10,
      textStyle: {
        fontSize: 12
      }
    },
    grid: {
      show: props.showGrid,
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: props.showLegend ? '15%' : '5%',
      containLabel: true
    },
    xAxis: {
      type: 'time',
      boundaryGap: false,
      axisLine: {
        lineStyle: {
          color: '#e5e7eb'
        }
      },
      axisLabel: {
        color: '#6b7280',
        fontSize: 11,
        formatter: (value: number) => {
          const date = new Date(value)
          const now = new Date()
          const diffHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60)
          
          if (diffHours < 24) {
            return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
          } else {
            return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
          }
        }
      },
      splitLine: {
        show: true,
        lineStyle: {
          color: '#f3f4f6',
          type: 'dashed'
        }
      }
    },
    yAxis: {
      type: 'value',
      axisLine: {
        lineStyle: {
          color: '#e5e7eb'
        }
      },
      axisLabel: {
        color: '#6b7280',
        fontSize: 11,
        formatter: (value: number) => formatValue(value)
      },
      splitLine: {
        show: true,
        lineStyle: {
          color: '#f3f4f6',
          type: 'dashed'
        }
      }
    },
    series: []
  }
  
  chart.value.setOption(option)
  
  // 监听窗口大小变化
  const resizeObserver = new ResizeObserver(() => {
    chart.value?.resize()
  })
  resizeObserver.observe(chartContainer.value)
}

const updateChart = () => {
  if (!chart.value || !hasData.value) return
  
  // 按传感器ID分组数据
  const groupedData = new Map<string, SensorData[]>()
  chartData.value.forEach(item => {
    if (!groupedData.has(item.sensor_id)) {
      groupedData.set(item.sensor_id, [])
    }
    groupedData.get(item.sensor_id)!.push(item)
  })
  
  // 生成系列数据
  const series: any[] = []
  let colorIndex = 0
  
  groupedData.forEach((data, sensorId) => {
    const sortedData = data.sort((a, b) => 
      new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    )
    
    series.push({
      name: sensorId,
      type: 'line',
      smooth: props.lineSmooth,
      symbol: 'circle',
      symbolSize: 4,
      lineStyle: {
        width: 2,
        color: props.colors[colorIndex % props.colors.length]
      },
      itemStyle: {
        color: props.colors[colorIndex % props.colors.length]
      },
      areaStyle: {
        opacity: 0.1,
        color: props.colors[colorIndex % props.colors.length]
      },
      data: sortedData.map(item => [
        new Date(item.timestamp).getTime(),
        item.value
      ])
    })
    
    colorIndex++
  })
  
  chart.value.setOption({
    series
  })
}

const getTimeRangeParams = () => {
  const now = new Date()
  let startTime: Date
  
  switch (timeRange.value) {
    case '1h':
      startTime = new Date(now.getTime() - 60 * 60 * 1000)
      break
    case '6h':
      startTime = new Date(now.getTime() - 6 * 60 * 60 * 1000)
      break
    case '24h':
      startTime = new Date(now.getTime() - 24 * 60 * 60 * 1000)
      break
    case '7d':
      startTime = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
      break
    case '30d':
      startTime = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
      break
    default:
      startTime = new Date(now.getTime() - 60 * 60 * 1000)
  }
  
  return {
    start_time: startTime.toISOString(),
    end_time: now.toISOString()
  }
}

const refreshData = async () => {
  if (props.sensorIds.length === 0) return
  
  try {
    loading.value = true
    error.value = null
    
    const timeParams = getTimeRangeParams()
    const params = {
      sensor_ids: props.sensorIds,
      ...timeParams,
      limit: 1000
    }
    
    emit('data-request', params)
  } catch (err) {
    error.value = '获取数据失败'
    console.error('获取图表数据失败:', err)
  } finally {
    loading.value = false
  }
}

const onTimeRangeChange = () => {
  emit('time-range-change', timeRange.value)
  refreshData()
}

const toggleAutoRefresh = () => {
  autoRefresh.value = !autoRefresh.value
  
  if (autoRefresh.value) {
    refreshTimer.value = window.setInterval(() => {
      refreshData()
    }, 30000) // 30秒刷新一次
  } else {
    if (refreshTimer.value) {
      clearInterval(refreshTimer.value)
      refreshTimer.value = undefined
    }
  }
}

const formatValue = (value: number): string => {
  if (typeof value !== 'number') return '--'
  
  if (Math.abs(value) >= 1000) {
    return value.toLocaleString('zh-CN', { maximumFractionDigits: 1 })
  } else if (Math.abs(value) >= 1) {
    return value.toFixed(2)
  } else {
    return value.toFixed(4)
  }
}

// 暴露方法给父组件
const updateData = (data: SensorData[]) => {
  chartData.value = data
  loading.value = false
  error.value = null
  nextTick(() => {
    updateChart()
  })
}

const setError = (errorMessage: string) => {
  error.value = errorMessage
  loading.value = false
}

defineExpose({
  updateData,
  setError,
  refreshData
})

// 生命周期
onMounted(() => {
  nextTick(() => {
    initChart()
    refreshData()
  })
})

onUnmounted(() => {
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value)
  }
  if (chart.value) {
    chart.value.dispose()
  }
})

// 监听器
watch(() => props.sensorIds, () => {
  refreshData()
}, { deep: true })

watch(hasData, (newVal) => {
  if (newVal) {
    nextTick(() => {
      updateChart()
    })
  }
})
</script>

<style scoped>
.realtime-chart {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px 20px 0;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 0;
}

.chart-title h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 4px 0;
}

.chart-subtitle {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

.chart-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.time-range-select {
  padding: 6px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 12px;
  background: white;
  color: #374151;
  cursor: pointer;
}

.time-range-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.refresh-btn {
  padding: 6px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 12px;
  background: white;
  color: #374151;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.2s ease;
}

.refresh-btn:hover {
  background-color: #f9fafb;
  border-color: #9ca3af;
}

.refresh-btn.active {
  background-color: #dbeafe;
  color: #1d4ed8;
  border-color: #3b82f6;
}

.refresh-icon {
  font-size: 12px;
}

.chart-container {
  position: relative;
  height: v-bind(height);
  padding: 20px;
}

.chart-loading,
.chart-error,
.chart-no-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #6b7280;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e5e7eb;
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.retry-btn {
  margin-top: 12px;
  padding: 8px 16px;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
}

.retry-btn:hover {
  background-color: #2563eb;
}

.chart-stats {
  display: flex;
  justify-content: space-around;
  padding: 16px 20px;
  background-color: #f9fafb;
  border-top: 1px solid #e5e7eb;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-label {
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
}

.stat-value {
  font-size: 14px;
  color: #1f2937;
  font-weight: 600;
  font-family: monospace;
}

@media (max-width: 768px) {
  .chart-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .chart-controls {
    justify-content: flex-start;
  }
  
  .chart-stats {
    flex-wrap: wrap;
    gap: 12px;
  }
  
  .stat-item {
    flex: 1;
    min-width: calc(50% - 6px);
  }
}
</style>