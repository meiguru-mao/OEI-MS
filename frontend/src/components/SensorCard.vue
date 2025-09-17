<template>
  <div class="sensor-card" :class="{ 'offline': !sensor.is_active }">
    <div class="sensor-header">
      <div class="sensor-info">
        <h3 class="sensor-name">{{ sensor.name }}</h3>
        <p class="sensor-id">ID: {{ sensor.sensor_id }}</p>
        <p class="sensor-location" v-if="sensor.location">
          <i class="icon-location"></i>
          {{ sensor.location }}
        </p>
      </div>
      <div class="sensor-status">
        <div class="status-indicator" :class="statusClass"></div>
        <span class="status-text">{{ statusText }}</span>
      </div>
    </div>
    
    <div class="sensor-body">
      <div class="sensor-type">
        <span class="type-label">类型:</span>
        <span class="type-value">{{ sensorType?.name || '未知' }}</span>
      </div>
      
      <div class="sensor-value" v-if="realtimeData">
        <div class="value-display">
          <span class="value-number">{{ formatValue(realtimeData.value) }}</span>
          <span class="value-unit" v-if="sensorType?.unit">{{ sensorType.unit }}</span>
        </div>
        <div class="value-time">
          更新时间: {{ formatTime(realtimeData.timestamp) }}
        </div>
        <div class="value-quality" :class="qualityClass">
          质量: {{ qualityText }}
        </div>
      </div>
      
      <div class="no-data" v-else>
        <span>暂无数据</span>
      </div>
    </div>
    
    <div class="sensor-footer">
      <div class="sensor-actions">
        <button class="btn btn-primary" @click="$emit('view-details', sensor)">
          查看详情
        </button>
        <button class="btn btn-secondary" @click="$emit('view-chart', sensor)">
          查看图表
        </button>
        <button 
          class="btn btn-outline" 
          @click="$emit('toggle-subscription', sensor)"
          :class="{ 'active': isSubscribed }"
        >
          {{ isSubscribed ? '取消订阅' : '订阅数据' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Sensor, SensorType, SensorData } from '@/services/api'

interface Props {
  sensor: Sensor
  sensorType?: SensorType
  realtimeData?: SensorData
  isSubscribed?: boolean
}

interface Emits {
  'view-details': [sensor: Sensor]
  'view-chart': [sensor: Sensor]
  'toggle-subscription': [sensor: Sensor]
}

const props = withDefaults(defineProps<Props>(), {
  isSubscribed: false
})

defineEmits<Emits>()

// 状态计算
const statusClass = computed(() => {
  if (!props.sensor.is_active) return 'offline'
  if (props.realtimeData) {
    const now = new Date().getTime()
    const dataTime = new Date(props.realtimeData.timestamp).getTime()
    const diffMinutes = (now - dataTime) / (1000 * 60)
    
    if (diffMinutes > 10) return 'stale'
    if (props.realtimeData.quality && props.realtimeData.quality < 0.8) return 'warning'
    return 'online'
  }
  return 'unknown'
})

const statusText = computed(() => {
  const status = statusClass.value
  switch (status) {
    case 'online': return '在线'
    case 'offline': return '离线'
    case 'stale': return '数据过期'
    case 'warning': return '数据异常'
    default: return '未知状态'
  }
})

const qualityClass = computed(() => {
  if (!props.realtimeData?.quality) return 'unknown'
  const quality = props.realtimeData.quality
  if (quality >= 0.9) return 'excellent'
  if (quality >= 0.8) return 'good'
  if (quality >= 0.6) return 'fair'
  return 'poor'
})

const qualityText = computed(() => {
  if (!props.realtimeData?.quality) return '未知'
  const quality = props.realtimeData.quality
  if (quality >= 0.9) return '优秀'
  if (quality >= 0.8) return '良好'
  if (quality >= 0.6) return '一般'
  return '较差'
})

// 格式化函数
const formatValue = (value: number): string => {
  if (typeof value !== 'number') return '--'
  
  // 根据数值大小选择合适的精度
  if (Math.abs(value) >= 1000) {
    return value.toLocaleString('zh-CN', { maximumFractionDigits: 1 })
  } else if (Math.abs(value) >= 1) {
    return value.toFixed(2)
  } else {
    return value.toFixed(4)
  }
}

const formatTime = (timestamp: string): string => {
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMinutes = Math.floor(diffMs / (1000 * 60))
  
  if (diffMinutes < 1) return '刚刚'
  if (diffMinutes < 60) return `${diffMinutes}分钟前`
  if (diffMinutes < 1440) return `${Math.floor(diffMinutes / 60)}小时前`
  
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.sensor-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
  transition: all 0.3s ease;
  border: 1px solid #e5e7eb;
}

.sensor-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.sensor-card.offline {
  opacity: 0.7;
  border-color: #d1d5db;
}

.sensor-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.sensor-info {
  flex: 1;
}

.sensor-name {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 4px 0;
}

.sensor-id {
  font-size: 12px;
  color: #6b7280;
  margin: 0 0 4px 0;
  font-family: monospace;
}

.sensor-location {
  font-size: 14px;
  color: #4b5563;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 4px;
}

.icon-location::before {
  content: '📍';
}

.sensor-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  position: relative;
}

.status-indicator.online {
  background-color: #10b981;
  box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
}

.status-indicator.offline {
  background-color: #ef4444;
}

.status-indicator.stale {
  background-color: #f59e0b;
}

.status-indicator.warning {
  background-color: #f97316;
}

.status-indicator.unknown {
  background-color: #6b7280;
}

.status-text {
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
}

.sensor-body {
  margin-bottom: 16px;
}

.sensor-type {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.type-label {
  font-size: 14px;
  color: #6b7280;
}

.type-value {
  font-size: 14px;
  color: #1f2937;
  font-weight: 500;
  background-color: #f3f4f6;
  padding: 2px 8px;
  border-radius: 4px;
}

.sensor-value {
  background-color: #f9fafb;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.value-display {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-bottom: 8px;
}

.value-number {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
  font-family: monospace;
}

.value-unit {
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
}

.value-time {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 4px;
}

.value-quality {
  font-size: 12px;
  font-weight: 500;
}

.value-quality.excellent {
  color: #059669;
}

.value-quality.good {
  color: #0891b2;
}

.value-quality.fair {
  color: #d97706;
}

.value-quality.poor {
  color: #dc2626;
}

.value-quality.unknown {
  color: #6b7280;
}

.no-data {
  text-align: center;
  padding: 20px;
  color: #9ca3af;
  font-style: italic;
}

.sensor-footer {
  border-top: 1px solid #e5e7eb;
  padding-top: 16px;
}

.sensor-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.btn {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn:hover {
  transform: translateY(-1px);
}

.btn-primary {
  background-color: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.btn-primary:hover {
  background-color: #2563eb;
  border-color: #2563eb;
}

.btn-secondary {
  background-color: #6b7280;
  color: white;
  border-color: #6b7280;
}

.btn-secondary:hover {
  background-color: #4b5563;
  border-color: #4b5563;
}

.btn-outline {
  background-color: transparent;
  color: #6b7280;
  border-color: #d1d5db;
}

.btn-outline:hover {
  background-color: #f9fafb;
  color: #374151;
  border-color: #9ca3af;
}

.btn-outline.active {
  background-color: #dbeafe;
  color: #1d4ed8;
  border-color: #3b82f6;
}

@media (max-width: 768px) {
  .sensor-card {
    padding: 16px;
  }
  
  .sensor-header {
    flex-direction: column;
    gap: 12px;
  }
  
  .sensor-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}
</style>