<template>
  <div class="statistics-chart">
    <div class="chart-header">
      <h3>{{ title }}</h3>
      <div class="chart-controls">
        <el-select v-model="timeRange" @change="onTimeRangeChange">
          <el-option label="最近1小时" value="1h" />
          <el-option label="最近24小时" value="24h" />
          <el-option label="最近7天" value="7d" />
          <el-option label="最近30天" value="30d" />
        </el-select>
        <el-button @click="refreshData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>
    
    <div class="statistics-grid">
      <!-- 系统概览卡片 -->
      <div class="stat-card">
        <div class="stat-header">
          <h4>系统概览</h4>
        </div>
        <div class="stat-content">
          <div class="stat-item">
            <div class="stat-icon online">
              <el-icon><Monitor /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ systemStats.onlineSensors }}</div>
              <div class="stat-label">在线传感器</div>
            </div>
          </div>
          <div class="stat-item">
            <div class="stat-icon offline">
              <el-icon><Monitor /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ systemStats.offlineSensors }}</div>
              <div class="stat-label">离线传感器</div>
            </div>
          </div>
          <div class="stat-item">
            <div class="stat-icon gateway">
              <el-icon><Connection /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ systemStats.activeGateways }}</div>
              <div class="stat-label">活跃网关</div>
            </div>
          </div>
          <div class="stat-item">
            <div class="stat-icon alarm">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ systemStats.activeAlarms }}</div>
              <div class="stat-label">活跃报警</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 传感器类型分布 -->
      <div class="chart-card">
        <div class="chart-title">
          <h4>传感器类型分布</h4>
        </div>
        <div ref="sensorTypeChart" class="chart-container"></div>
      </div>
      
      <!-- 数据量统计 -->
      <div class="chart-card">
        <div class="chart-title">
          <h4>数据量统计</h4>
        </div>
        <div ref="dataVolumeChart" class="chart-container"></div>
      </div>
      
      <!-- 报警趋势 -->
      <div class="chart-card">
        <div class="chart-title">
          <h4>报警趋势</h4>
        </div>
        <div ref="alarmTrendChart" class="chart-container"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { Refresh, Monitor, Connection, Warning } from '@element-plus/icons-vue'
import { ApiService } from '@/services/api'

interface Props {
  title?: string
  autoRefresh?: boolean
  refreshInterval?: number
}

const props = withDefaults(defineProps<Props>(), {
  title: '系统统计',
  autoRefresh: true,
  refreshInterval: 30000 // 30秒
})

// 响应式数据
const loading = ref(false)
const timeRange = ref('24h')
const systemStats = ref({
  onlineSensors: 0,
  offlineSensors: 0,
  activeGateways: 0,
  activeAlarms: 0
})

// 图表引用
const sensorTypeChart = ref<HTMLDivElement>()
const dataVolumeChart = ref<HTMLDivElement>()
const alarmTrendChart = ref<HTMLDivElement>()

// 图表实例
let sensorTypeChartInstance: echarts.ECharts
let dataVolumeChartInstance: echarts.ECharts
let alarmTrendChartInstance: echarts.ECharts

// 自动刷新定时器
let refreshTimer: NodeJS.Timeout

// 生命周期
onMounted(async () => {
  await initCharts()
  await loadData()
  
  if (props.autoRefresh) {
    startAutoRefresh()
  }
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  
  // 销毁图表实例
  if (sensorTypeChartInstance) sensorTypeChartInstance.dispose()
  if (dataVolumeChartInstance) dataVolumeChartInstance.dispose()
  if (alarmTrendChartInstance) alarmTrendChartInstance.dispose()
})

// 方法
const initCharts = async () => {
  await nextTick()
  
  // 初始化传感器类型分布图表
  if (sensorTypeChart.value) {
    sensorTypeChartInstance = echarts.init(sensorTypeChart.value)
    sensorTypeChartInstance.setOption(getSensorTypeChartOption())
  }
  
  // 初始化数据量统计图表
  if (dataVolumeChart.value) {
    dataVolumeChartInstance = echarts.init(dataVolumeChart.value)
    dataVolumeChartInstance.setOption(getDataVolumeChartOption())
  }
  
  // 初始化报警趋势图表
  if (alarmTrendChart.value) {
    alarmTrendChartInstance = echarts.init(alarmTrendChart.value)
    alarmTrendChartInstance.setOption(getAlarmTrendChartOption())
  }
  
  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
}

const handleResize = () => {
  if (sensorTypeChartInstance) sensorTypeChartInstance.resize()
  if (dataVolumeChartInstance) dataVolumeChartInstance.resize()
  if (alarmTrendChartInstance) alarmTrendChartInstance.resize()
}

const loadData = async () => {
  loading.value = true
  
  try {
    // 并行加载所有数据
    const [statsResponse, sensorTypesResponse, dataVolumeResponse, alarmTrendResponse] = await Promise.all([
      ApiService.getSystemStats(),
      loadSensorTypeData(),
      loadDataVolumeData(),
      loadAlarmTrendData()
    ])
    
    // 更新系统统计
    if (statsResponse.data) {
      systemStats.value = {
        onlineSensors: statsResponse.data.online_sensors || 0,
        offlineSensors: statsResponse.data.offline_sensors || 0,
        activeGateways: statsResponse.data.active_gateways || 0,
        activeAlarms: statsResponse.data.active_alarms || 0
      }
    }
    
    // 更新图表数据
    updateSensorTypeChart(sensorTypesResponse)
    updateDataVolumeChart(dataVolumeResponse)
    updateAlarmTrendChart(alarmTrendResponse)
    
  } catch (error) {
    console.error('加载统计数据失败:', error)
    ElMessage.error('加载统计数据失败')
  } finally {
    loading.value = false
  }
}

const loadSensorTypeData = async () => {
  try {
    const response = await ApiService.getSensorTypes()
    const sensorTypes = response.data || []
    
    // 统计每种类型的传感器数量
    const typeStats = new Map()
    
    for (const type of sensorTypes) {
      const sensorsResponse = await ApiService.getSensors({ type_id: type.id })
      typeStats.set(type.name, sensorsResponse.data?.length || 0)
    }
    
    return Array.from(typeStats.entries()).map(([name, value]) => ({ name, value }))
  } catch (error) {
    console.error('加载传感器类型数据失败:', error)
    return []
  }
}

const loadDataVolumeData = async () => {
  try {
    // 模拟数据量统计数据
    const now = new Date()
    const data = []
    
    for (let i = 23; i >= 0; i--) {
      const time = new Date(now.getTime() - i * 60 * 60 * 1000)
      const value = Math.floor(Math.random() * 1000) + 500
      data.push({
        time: time.toISOString(),
        value
      })
    }
    
    return data
  } catch (error) {
    console.error('加载数据量统计失败:', error)
    return []
  }
}

const loadAlarmTrendData = async () => {
  try {
    const response = await ApiService.getAlarms({
      time_range: timeRange.value,
      group_by: 'hour'
    })
    
    return response.data || []
  } catch (error) {
    console.error('加载报警趋势数据失败:', error)
    return []
  }
}

const getSensorTypeChartOption = () => {
  return {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '传感器类型',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 20,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: []
      }
    ]
  }
}

const getDataVolumeChartOption = () => {
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'time',
      boundaryGap: false
    },
    yAxis: {
      type: 'value',
      name: '数据量'
    },
    series: [
      {
        name: '数据量',
        type: 'line',
        smooth: true,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
          ])
        },
        itemStyle: {
          color: '#409EFF'
        },
        data: []
      }
    ]
  }
}

const getAlarmTrendChartOption = () => {
  return {
    tooltip: {
      trigger: 'axis'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'time',
      boundaryGap: false
    },
    yAxis: {
      type: 'value',
      name: '报警数量'
    },
    series: [
      {
        name: '报警数量',
        type: 'bar',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#f56c6c' },
            { offset: 1, color: '#f56c6c80' }
          ])
        },
        data: []
      }
    ]
  }
}

const updateSensorTypeChart = (data: any[]) => {
  if (sensorTypeChartInstance) {
    sensorTypeChartInstance.setOption({
      series: [{
        data: data
      }]
    })
  }
}

const updateDataVolumeChart = (data: any[]) => {
  if (dataVolumeChartInstance) {
    const chartData = data.map(item => [
      new Date(item.time).getTime(),
      item.value
    ])
    
    dataVolumeChartInstance.setOption({
      series: [{
        data: chartData
      }]
    })
  }
}

const updateAlarmTrendChart = (data: any[]) => {
  if (alarmTrendChartInstance) {
    const chartData = data.map(item => [
      new Date(item.time).getTime(),
      item.count
    ])
    
    alarmTrendChartInstance.setOption({
      series: [{
        data: chartData
      }]
    })
  }
}

const onTimeRangeChange = () => {
  loadData()
}

const refreshData = () => {
  loadData()
}

const startAutoRefresh = () => {
  refreshTimer = setInterval(() => {
    loadData()
  }, props.refreshInterval)
}
</script>

<style scoped>
.statistics-chart {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.chart-header h3 {
  margin: 0;
  color: #333;
  font-size: 20px;
  font-weight: 600;
}

.chart-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.statistics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

.stat-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #e4e7ed;
}

.stat-header h4 {
  margin: 0 0 16px 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.stat-content {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #fff;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: #fff;
}

.stat-icon.online {
  background: #67c23a;
}

.stat-icon.offline {
  background: #909399;
}

.stat-icon.gateway {
  background: #409eff;
}

.stat-icon.alarm {
  background: #f56c6c;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #333;
  line-height: 1;
}

.stat-label {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}

.chart-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #e4e7ed;
}

.chart-title h4 {
  margin: 0 0 16px 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.chart-container {
  width: 100%;
  height: 300px;
}

@media (max-width: 768px) {
  .statistics-grid {
    grid-template-columns: 1fr;
  }
  
  .stat-content {
    grid-template-columns: 1fr;
  }
  
  .chart-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .chart-controls {
    justify-content: center;
  }
}
</style>