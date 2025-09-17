import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ApiService, type Sensor, type SensorType, type SensorData, type Gateway } from '@/services/api'
import { websocketService } from '@/services/websocket'

export const useSensorStore = defineStore('sensor', () => {
  // 状态
  const sensors = ref<Sensor[]>([])
  const sensorTypes = ref<SensorType[]>([])
  const gateways = ref<Gateway[]>([])
  const realtimeData = ref<Map<string, SensorData>>(new Map())
  const historicalData = ref<Map<string, SensorData[]>>(new Map())
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  // 计算属性
  const activeSensors = computed(() => 
    sensors.value.filter(sensor => sensor.is_active)
  )
  
  const onlineGateways = computed(() => 
    gateways.value.filter(gateway => gateway.is_online)
  )
  
  const sensorById = computed(() => {
    const map = new Map<number, Sensor>()
    sensors.value.forEach(sensor => {
      map.set(sensor.id, sensor)
    })
    return map
  })
  
  const sensorTypeById = computed(() => {
    const map = new Map<number, SensorType>()
    sensorTypes.value.forEach(type => {
      map.set(type.id, type)
    })
    return map
  })
  
  // 传感器类型操作
  const fetchSensorTypes = async () => {
    try {
      loading.value = true
      error.value = null
      sensorTypes.value = await ApiService.getSensorTypes()
    } catch (err) {
      error.value = '获取传感器类型失败'
      console.error('获取传感器类型失败:', err)
    } finally {
      loading.value = false
    }
  }
  
  const createSensorType = async (data: {
    name: string
    description?: string
    unit?: string
    min_value?: number
    max_value?: number
  }) => {
    try {
      loading.value = true
      error.value = null
      const newType = await ApiService.createSensorType(data)
      sensorTypes.value.push(newType)
      return newType
    } catch (err) {
      error.value = '创建传感器类型失败'
      console.error('创建传感器类型失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const updateSensorType = async (id: number, data: Partial<{
    name: string
    description?: string
    unit?: string
    min_value?: number
    max_value?: number
  }>) => {
    try {
      loading.value = true
      error.value = null
      const updatedType = await ApiService.updateSensorType(id, data)
      const index = sensorTypes.value.findIndex(type => type.id === id)
      if (index > -1) {
        sensorTypes.value[index] = updatedType
      }
      return updatedType
    } catch (err) {
      error.value = '更新传感器类型失败'
      console.error('更新传感器类型失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const deleteSensorType = async (id: number) => {
    try {
      loading.value = true
      error.value = null
      await ApiService.deleteSensorType(id)
      const index = sensorTypes.value.findIndex(type => type.id === id)
      if (index > -1) {
        sensorTypes.value.splice(index, 1)
      }
    } catch (err) {
      error.value = '删除传感器类型失败'
      console.error('删除传感器类型失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // 传感器操作
  const fetchSensors = async (params?: {
    skip?: number
    limit?: number
    is_active?: boolean
  }) => {
    try {
      loading.value = true
      error.value = null
      sensors.value = await ApiService.getSensors(params)
    } catch (err) {
      error.value = '获取传感器列表失败'
      console.error('获取传感器列表失败:', err)
    } finally {
      loading.value = false
    }
  }
  
  const createSensor = async (data: {
    sensor_id: string
    name: string
    location?: string
    description?: string
    is_active?: boolean
    sensor_type_id: number
    ip_address?: string
    port?: number
    protocol?: string
    sampling_interval?: number
  }) => {
    try {
      loading.value = true
      error.value = null
      const newSensor = await ApiService.createSensor(data)
      sensors.value.push(newSensor)
      return newSensor
    } catch (err) {
      error.value = '创建传感器失败'
      console.error('创建传感器失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const updateSensor = async (id: number, data: Partial<{
    sensor_id: string
    name: string
    location?: string
    description?: string
    is_active?: boolean
    sensor_type_id: number
    ip_address?: string
    port?: number
    protocol?: string
    sampling_interval?: number
  }>) => {
    try {
      loading.value = true
      error.value = null
      const updatedSensor = await ApiService.updateSensor(id, data)
      const index = sensors.value.findIndex(sensor => sensor.id === id)
      if (index > -1) {
        sensors.value[index] = updatedSensor
      }
      return updatedSensor
    } catch (err) {
      error.value = '更新传感器失败'
      console.error('更新传感器失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const deleteSensor = async (id: number) => {
    try {
      loading.value = true
      error.value = null
      await ApiService.deleteSensor(id)
      const index = sensors.value.findIndex(sensor => sensor.id === id)
      if (index > -1) {
        sensors.value.splice(index, 1)
      }
    } catch (err) {
      error.value = '删除传感器失败'
      console.error('删除传感器失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // 网关操作
  const fetchGateways = async () => {
    try {
      loading.value = true
      error.value = null
      gateways.value = await ApiService.getGateways()
    } catch (err) {
      error.value = '获取网关列表失败'
      console.error('获取网关列表失败:', err)
    } finally {
      loading.value = false
    }
  }
  
  // 实时数据操作
  const fetchLatestData = async (sensorIds?: string[]) => {
    try {
      const data = await ApiService.getLatestData(sensorIds)
      data.forEach(item => {
        realtimeData.value.set(item.sensor_id, item)
      })
    } catch (err) {
      console.error('获取最新数据失败:', err)
    }
  }
  
  const fetchHistoricalData = async (query: {
    sensor_ids?: string[]
    start_time?: string
    end_time?: string
    limit?: number
    aggregation?: string
    interval?: string
  }) => {
    try {
      loading.value = true
      error.value = null
      const data = await ApiService.querySensorData(query)
      
      // 按传感器ID分组存储历史数据
      const groupedData = new Map<string, SensorData[]>()
      data.forEach(item => {
        if (!groupedData.has(item.sensor_id)) {
          groupedData.set(item.sensor_id, [])
        }
        groupedData.get(item.sensor_id)!.push(item)
      })
      
      // 更新历史数据
      groupedData.forEach((sensorData, sensorId) => {
        historicalData.value.set(sensorId, sensorData)
      })
      
      return data
    } catch (err) {
      error.value = '获取历史数据失败'
      console.error('获取历史数据失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // WebSocket实时数据处理
  const setupRealtimeData = () => {
    // 监听传感器数据
    websocketService.onSensorData((data) => {
      const sensorData: SensorData = {
        timestamp: data.timestamp,
        sensor_id: data.sensor_id,
        value: data.value,
        quality: data.quality
      }
      realtimeData.value.set(data.sensor_id, sensorData)
    })
    
    // 监听系统消息
    websocketService.onSystemMessage((message) => {
      if (message.type === 'sensor_status' && message.sensor_id) {
        // 更新传感器状态
        const sensor = sensors.value.find(s => s.sensor_id === message.sensor_id)
        if (sensor) {
          // 可以在这里更新传感器的状态信息
          console.log(`传感器 ${message.sensor_id} 状态更新:`, message.status)
        }
      } else if (message.type === 'gateway_heartbeat' && message.gateway_id) {
        // 更新网关心跳状态
        const gateway = gateways.value.find(g => g.gateway_id === message.gateway_id)
        if (gateway) {
          gateway.is_online = true
          gateway.last_heartbeat = message.timestamp
        }
      }
    })
  }
  
  // 订阅传感器实时数据
  const subscribeToSensors = (sensorIds: string[]) => {
    websocketService.subscribeSensors(sensorIds)
  }
  
  // 取消订阅传感器实时数据
  const unsubscribeFromSensors = (sensorIds: string[]) => {
    websocketService.unsubscribeSensors(sensorIds)
  }
  
  // 清除错误
  const clearError = () => {
    error.value = null
  }
  
  // 重置状态
  const reset = () => {
    sensors.value = []
    sensorTypes.value = []
    gateways.value = []
    realtimeData.value.clear()
    historicalData.value.clear()
    loading.value = false
    error.value = null
  }
  
  return {
    // 状态
    sensors,
    sensorTypes,
    gateways,
    realtimeData,
    historicalData,
    loading,
    error,
    
    // 计算属性
    activeSensors,
    onlineGateways,
    sensorById,
    sensorTypeById,
    
    // 方法
    fetchSensorTypes,
    createSensorType,
    updateSensorType,
    deleteSensorType,
    fetchSensors,
    createSensor,
    updateSensor,
    deleteSensor,
    fetchGateways,
    fetchLatestData,
    fetchHistoricalData,
    setupRealtimeData,
    subscribeToSensors,
    unsubscribeFromSensors,
    clearError,
    reset
  }
})