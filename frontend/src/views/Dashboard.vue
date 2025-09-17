<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>传感器监控系统</h1>
      <div class="header-stats">
        <div class="stat-card">
          <div class="stat-number">{{ activeSensors.length }}</div>
          <div class="stat-label">活跃传感器</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ onlineGateways.length }}</div>
          <div class="stat-label">在线网关</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ realtimeDataCount }}</div>
          <div class="stat-label">实时数据</div>
        </div>
        <div class="stat-card" :class="connectionStatusClass">
          <div class="stat-number">{{ connectionStatus }}</div>
          <div class="stat-label">连接状态</div>
        </div>
      </div>
    </div>

    <div class="dashboard-content">
      <!-- 传感器网格 -->
      <div class="sensors-section">
        <div class="section-header">
          <h2>传感器状态</h2>
          <div class="section-controls">
            <button 
              @click="refreshAllData" 
              :disabled="loading" 
              class="refresh-btn"
            >
              <span class="refresh-icon" :class="{ spinning: loading }">🔄</span>
              刷新数据
            </button>
            <button @click="showAddSensorModal = true" class="add-btn">
              <span>➕</span>
              添加传感器
            </button>
          </div>
        </div>
        
        <div class="sensors-grid" v-if="sensors.length > 0">
          <SensorCard
            v-for="sensor in sensors"
            :key="sensor.id"
            :sensor="sensor"
            :sensor-type="sensorTypeById.get(sensor.sensor_type_id)"
            :realtime-data="realtimeData.get(sensor.sensor_id)"
            :is-subscribed="subscribedSensors.has(sensor.sensor_id)"
            @view-details="onViewSensorDetails"
            @view-chart="onViewSensorChart"
            @toggle-subscription="onToggleSubscription"
          />
        </div>
        
        <div class="empty-state" v-else-if="!loading">
          <div class="empty-icon">📊</div>
          <h3>暂无传感器</h3>
          <p>点击"添加传感器"按钮开始监控您的设备</p>
          <button @click="showAddSensorModal = true" class="add-btn primary">
            添加第一个传感器
          </button>
        </div>
        
        <div class="loading-state" v-else>
          <div class="loading-spinner"></div>
          <p>加载传感器数据中...</p>
        </div>
      </div>

      <!-- 实时图表区域 -->
      <div class="charts-section" v-if="selectedSensors.length > 0">
        <div class="section-header">
          <h2>实时数据图表</h2>
          <div class="chart-controls">
            <select v-model="selectedChartType" class="chart-type-select">
              <option value="line">折线图</option>
              <option value="area">面积图</option>
              <option value="bar">柱状图</option>
            </select>
          </div>
        </div>
        
        <div class="charts-grid">
          <RealtimeChart
            ref="mainChart"
            :title="'传感器实时数据'"
            :subtitle="`监控 ${selectedSensors.length} 个传感器`"
            :sensor-ids="selectedSensors"
            :height="'400px'"
            :show-legend="true"
            :line-smooth="true"
            @data-request="onChartDataRequest"
            @time-range-change="onTimeRangeChange"
          />
        </div>
      </div>
    </div>

    <!-- 传感器详情模态框 -->
    <div class="modal-overlay" v-if="showSensorDetails" @click="closeSensorDetails">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>传感器详情</h3>
          <button @click="closeSensorDetails" class="close-btn">✕</button>
        </div>
        <div class="modal-body" v-if="selectedSensorDetails">
          <div class="detail-grid">
            <div class="detail-item">
              <label>传感器ID:</label>
              <span>{{ selectedSensorDetails.sensor_id }}</span>
            </div>
            <div class="detail-item">
              <label>名称:</label>
              <span>{{ selectedSensorDetails.name }}</span>
            </div>
            <div class="detail-item">
              <label>位置:</label>
              <span>{{ selectedSensorDetails.location || '未设置' }}</span>
            </div>
            <div class="detail-item">
              <label>类型:</label>
              <span>{{ sensorTypeById.get(selectedSensorDetails.sensor_type_id)?.name || '未知' }}</span>
            </div>
            <div class="detail-item">
              <label>状态:</label>
              <span :class="selectedSensorDetails.is_active ? 'status-active' : 'status-inactive'">
                {{ selectedSensorDetails.is_active ? '活跃' : '非活跃' }}
              </span>
            </div>
            <div class="detail-item">
              <label>IP地址:</label>
              <span>{{ selectedSensorDetails.ip_address || '未设置' }}</span>
            </div>
            <div class="detail-item">
              <label>端口:</label>
              <span>{{ selectedSensorDetails.port || '未设置' }}</span>
            </div>
            <div class="detail-item">
              <label>采样间隔:</label>
              <span>{{ selectedSensorDetails.sampling_interval || '默认' }}秒</span>
            </div>
            <div class="detail-item full-width">
              <label>描述:</label>
              <span>{{ selectedSensorDetails.description || '无描述' }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加传感器模态框 -->
    <div class="modal-overlay" v-if="showAddSensorModal" @click="closeAddSensorModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>添加传感器</h3>
          <button @click="closeAddSensorModal" class="close-btn">✕</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="addSensor" class="sensor-form">
            <div class="form-group">
              <label for="sensorId">传感器ID *</label>
              <input 
                id="sensorId"
                v-model="newSensor.sensor_id" 
                type="text" 
                required 
                placeholder="例如: TEMP_001"
              />
            </div>
            <div class="form-group">
              <label for="sensorName">传感器名称 *</label>
              <input 
                id="sensorName"
                v-model="newSensor.name" 
                type="text" 
                required 
                placeholder="例如: 温度传感器1号"
              />
            </div>
            <div class="form-group">
              <label for="sensorType">传感器类型 *</label>
              <select id="sensorType" v-model="newSensor.sensor_type_id" required>
                <option value="">请选择类型</option>
                <option 
                  v-for="type in sensorTypes" 
                  :key="type.id" 
                  :value="type.id"
                >
                  {{ type.name }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label for="sensorLocation">位置</label>
              <input 
                id="sensorLocation"
                v-model="newSensor.location" 
                type="text" 
                placeholder="例如: 车间A-1号机台"
              />
            </div>
            <div class="form-group">
              <label for="sensorDescription">描述</label>
              <textarea 
                id="sensorDescription"
                v-model="newSensor.description" 
                placeholder="传感器的详细描述..."
                rows="3"
              ></textarea>
            </div>
            <div class="form-actions">
              <button type="button" @click="closeAddSensorModal" class="btn-cancel">
                取消
              </button>
              <button type="submit" :disabled="addingSensor" class="btn-submit">
                {{ addingSensor ? '添加中...' : '添加传感器' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Grid, List, Refresh, Plus, FullScreen, Close, ArrowRight,
  Warning, CircleCheck, Connection, Disconnect, TrendCharts,
  Monitor, DataAnalysis, Bell
} from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { useSensorStore } from '@/stores/sensor'
import { websocketService } from '@/services/websocket'
import SensorCard from '@/components/SensorCard.vue'
import RealtimeChart from '@/components/RealtimeChart.vue'
import StatisticsChart from '@/components/charts/StatisticsChart.vue'
import type { Sensor } from '@/services/api'
import { formatRelativeTime } from '@/utils/date'

// 路由
const router = useRouter()

// Store
const sensorStore = useSensorStore()

// 响应式数据
const loading = ref(false)
const showSensorDetails = ref(false)
const showAddSensorModal = ref(false)
const selectedSensorDetails = ref<Sensor | null>(null)
const subscribedSensors = ref(new Set<string>())
const selectedSensors = ref<string[]>([])
const selectedChartType = ref('line')
const mainChart = ref()
const addingSensor = ref(false)

// 新增的仪表盘相关数据
const viewMode = ref<'grid' | 'list'>('grid')
const refreshing = ref(false)
const statusLoading = ref(false)
const recentAlarms = ref<any[]>([])
const fullscreenDialogVisible = ref(false)
const fullscreenChart = ref<any>(null)
const realTimeCharts = ref<any[]>([])

// 系统状态
const systemStatus = ref({
  cpu: 0,
  memory: 0,
  disk: 0,
  network: true
})

// 快速统计
const quickStats = ref([
  {
    key: 'sensors',
    label: '在线传感器',
    value: 0,
    icon: Monitor,
    iconClass: 'success',
    change: '+2.5%',
    changeIcon: 'ArrowUp',
    changeClass: 'positive'
  },
  {
    key: 'data',
    label: '今日数据量',
    value: 0,
    icon: DataAnalysis,
    iconClass: 'primary',
    change: '+15.3%',
    changeIcon: 'ArrowUp',
    changeClass: 'positive'
  },
  {
    key: 'alarms',
    label: '活跃报警',
    value: 0,
    icon: Bell,
    iconClass: 'warning',
    change: '-8.2%',
    changeIcon: 'ArrowDown',
    changeClass: 'negative'
  },
  {
    key: 'performance',
    label: '系统性能',
    value: '良好',
    icon: TrendCharts,
    iconClass: 'info',
    change: '稳定',
    changeIcon: 'Minus',
    changeClass: 'stable'
  }
])

// 新传感器表单数据
const newSensor = ref({
  sensor_id: '',
  name: '',
  sensor_type_id: '',
  location: '',
  description: ''
})

// 计算属性
const {
  sensors,
  sensorTypes,
  gateways,
  realtimeData,
  activeSensors,
  onlineGateways,
  sensorById,
  sensorTypeById,
  error
} = sensorStore

const realtimeDataCount = computed(() => realtimeData.size)

const connectionStatus = computed(() => {
  return websocketService.isConnected ? '已连接' : '未连接'
})

const connectionStatusClass = computed(() => {
  return websocketService.isConnected ? 'connected' : 'disconnected'
})

// 新增计算属性
const chartRefsMap = computed(() => {
  const map = new Map()
  return map
})

// 方法
const refreshAllData = async () => {
  loading.value = true
  try {
    await Promise.all([
      sensorStore.fetchSensors(),
      sensorStore.fetchSensorTypes(),
      sensorStore.fetchGateways(),
      sensorStore.fetchLatestData()
    ])
  } catch (err) {
    console.error('刷新数据失败:', err)
  } finally {
    loading.value = false
  }
}

const onViewSensorDetails = (sensor: Sensor) => {
  selectedSensorDetails.value = sensor
  showSensorDetails.value = true
}

const closeSensorDetails = () => {
  showSensorDetails.value = false
  selectedSensorDetails.value = null
}

const onViewSensorChart = (sensor: Sensor) => {
  if (!selectedSensors.value.includes(sensor.sensor_id)) {
    selectedSensors.value.push(sensor.sensor_id)
  }
  
  // 滚动到图表区域
  setTimeout(() => {
    const chartsSection = document.querySelector('.charts-section')
    if (chartsSection) {
      chartsSection.scrollIntoView({ behavior: 'smooth' })
    }
  }, 100)
}

const onToggleSubscription = (sensor: Sensor) => {
  if (subscribedSensors.value.has(sensor.sensor_id)) {
    subscribedSensors.value.delete(sensor.sensor_id)
    sensorStore.unsubscribeFromSensors([sensor.sensor_id])
  } else {
    subscribedSensors.value.add(sensor.sensor_id)
    sensorStore.subscribeToSensors([sensor.sensor_id])
  }
}

const onChartDataRequest = async (params: any) => {
  try {
    const data = await sensorStore.fetchHistoricalData(params)
    mainChart.value?.updateData(data)
  } catch (err) {
    console.error('获取图表数据失败:', err)
    mainChart.value?.setError('获取数据失败')
  }
}

const onTimeRangeChange = (range: string) => {
  console.log('时间范围变更:', range)
}

const closeAddSensorModal = () => {
  showAddSensorModal.value = false
  newSensor.value = {
    sensor_id: '',
    name: '',
    sensor_type_id: '',
    location: '',
    description: ''
  }
}

const addSensor = async () => {
  if (addingSensor.value) return
  
  try {
    addingSensor.value = true
    await sensorStore.createSensor({
      ...newSensor.value,
      sensor_type_id: Number(newSensor.value.sensor_type_id),
      is_active: true
    })
    closeAddSensorModal()
  } catch (err) {
    console.error('添加传感器失败:', err)
    alert('添加传感器失败，请检查输入信息')
  } finally {
    addingSensor.value = false
  }
}

// 新增的仪表盘方法
const updateQuickStats = (stats: any) => {
  quickStats.value[0].value = stats.online_sensors || activeSensors.value.length
  quickStats.value[1].value = stats.today_data_count || realtimeDataCount.value
  quickStats.value[2].value = stats.active_alarms || 0
}

const addChart = () => {
  if (sensors.length === 0) {
    ElMessage.warning('暂无可用传感器')
    return
  }
  
  const sensor = sensors[0]
  realTimeCharts.value.push({
    id: Date.now(),
    title: sensor.name,
    sensorId: sensor.sensor_id,
    type: 'line',
    height: 300
  })
  
  ElMessage.success('图表添加成功')
}

const removeChart = async (index: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个图表吗？', '确认删除', {
      type: 'warning'
    })
    
    realTimeCharts.value.splice(index, 1)
    ElMessage.success('图表删除成功')
  } catch {
    // 用户取消删除
  }
}

const toggleChartFullscreen = (index: number) => {
  fullscreenChart.value = realTimeCharts.value[index]
  fullscreenDialogVisible.value = true
}

const closeFullscreenChart = () => {
  fullscreenDialogVisible.value = false
  fullscreenChart.value = null
}

const acknowledgeAlarm = async (alarmId: number) => {
  try {
    // 模拟API调用
    const index = recentAlarms.value.findIndex(alarm => alarm.id === alarmId)
    if (index > -1) {
      recentAlarms.value[index].status = 'acknowledged'
    }
    ElMessage.success('报警已确认')
  } catch (error) {
    ElMessage.error('确认报警失败')
  }
}

const clearAlarm = async (alarmId: number) => {
  try {
    // 模拟API调用
    const index = recentAlarms.value.findIndex(alarm => alarm.id === alarmId)
    if (index > -1) {
      recentAlarms.value.splice(index, 1)
    }
    ElMessage.success('报警已清除')
  } catch (error) {
    ElMessage.error('清除报警失败')
  }
}

const viewAllAlarms = () => {
  router.push('/alarms')
}

const getAlarmClass = (level: string) => {
  const classMap: Record<string, string> = {
    'critical': 'critical',
    'high': 'high',
    'medium': 'medium',
    'low': 'low'
  }
  return classMap[level] || 'medium'
}

const getProgressColor = (percentage: number) => {
  if (percentage < 60) return '#67c23a'
  if (percentage < 80) return '#e6a23c'
  return '#f56c6c'
}

const refreshSystemStatus = () => {
  statusLoading.value = true
  // 模拟系统状态更新
  setTimeout(() => {
    systemStatus.value = {
      cpu: Math.floor(Math.random() * 100),
      memory: Math.floor(Math.random() * 100),
      disk: Math.floor(Math.random() * 100),
      network: Math.random() > 0.1
    }
    statusLoading.value = false
  }, 1000)
}

// 初始化WebSocket连接
const initializeWebSocket = () => {
  if (!websocketService.isConnected) {
    websocketService.connect()
  }
  
  // 设置实时数据处理
  sensorStore.setupRealtimeData()
}

// 生命周期
onMounted(async () => {
  await refreshAllData()
  initializeWebSocket()
  
  // 自动订阅所有活跃传感器
  const activeSensorIds = activeSensors.value.map(s => s.sensor_id)
  if (activeSensorIds.length > 0) {
    activeSensorIds.forEach(id => subscribedSensors.value.add(id))
    sensorStore.subscribeToSensors(activeSensorIds)
    selectedSensors.value = activeSensorIds.slice(0, 5) // 最多显示5个传感器的图表
    
    // 初始化默认图表
    const defaultSensors = activeSensors.value.slice(0, 3)
    defaultSensors.forEach((sensor, index) => {
      realTimeCharts.value.push({
        id: Date.now() + index,
        title: sensor.name,
        sensorId: sensor.sensor_id,
        type: 'line',
        height: 300
      })
    })
  }
  
  // 模拟报警数据
  recentAlarms.value = [
    {
      id: 1,
      title: '温度异常',
      description: '传感器温度超过阈值',
      level: 'high',
      created_at: new Date().toISOString(),
      sensor_name: '温度传感器1'
    }
  ]
  
  // 更新快速统计
  updateQuickStats({
    online_sensors: activeSensors.value.length,
    today_data_count: realtimeDataCount.value,
    active_alarms: recentAlarms.value.length
  })
})

onUnmounted(() => {
  // 取消所有订阅
  if (subscribedSensors.value.size > 0) {
    sensorStore.unsubscribeFromSensors(Array.from(subscribedSensors.value))
  }
})
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background-color: #f8fafc;
  padding: 20px;
}

.dashboard-header {
  margin-bottom: 32px;
}

.dashboard-header h1 {
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 20px 0;
}

.header-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
  border: 1px solid #e5e7eb;
}

.stat-card.connected {
  border-color: #10b981;
  background: linear-gradient(135deg, #ecfdf5 0%, #ffffff 100%);
}

.stat-card.disconnected {
  border-color: #ef4444;
  background: linear-gradient(135deg, #fef2f2 0%, #ffffff 100%);
}

.stat-number {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
}

.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.section-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.refresh-btn, .add-btn {
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  border: 1px solid;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.refresh-btn {
  background: white;
  color: #374151;
  border-color: #d1d5db;
}

.refresh-btn:hover:not(:disabled) {
  background: #f9fafb;
  border-color: #9ca3af;
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.refresh-icon.spinning {
  animation: spin 1s linear infinite;
}

.add-btn {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.add-btn:hover {
  background: #2563eb;
  border-color: #2563eb;
}

.add-btn.primary {
  padding: 12px 24px;
  font-size: 16px;
}

.sensors-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.empty-state, .loading-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-state h3 {
  font-size: 20px;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.empty-state p {
  color: #6b7280;
  margin: 0 0 24px 0;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

.charts-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chart-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.chart-type-select {
  padding: 6px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  background: white;
  color: #374151;
}

.charts-grid {
  margin-top: 20px;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  color: #6b7280;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.modal-body {
  padding: 24px;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-item.full-width {
  grid-column: 1 / -1;
}

.detail-item label {
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.detail-item span {
  font-size: 14px;
  color: #1f2937;
  font-weight: 500;
}

.status-active {
  color: #059669 !important;
}

.status-inactive {
  color: #dc2626 !important;
}

/* 表单样式 */
.sensor-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 14px;
  color: #374151;
  font-weight: 500;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

.btn-cancel,
.btn-submit {
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  border: 1px solid;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-cancel {
  background: white;
  color: #374151;
  border-color: #d1d5db;
}

.btn-cancel:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}

.btn-submit {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.btn-submit:hover:not(:disabled) {
  background: #2563eb;
  border-color: #2563eb;
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .dashboard {
    padding: 16px;
  }
  
  .dashboard-header h1 {
    font-size: 24px;
  }
  
  .header-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .section-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .section-controls {
    justify-content: flex-start;
  }
  
  .sensors-grid {
    grid-template-columns: 1fr;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column;
  }
}
</style>