import axios, { type AxiosInstance, type AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'

// API基础配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// 创建axios实例
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 添加认证token（如果有）
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  (error) => {
    // 统一错误处理
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          ElMessage.error('未授权，请重新登录')
          // 清除token并跳转到登录页
          localStorage.removeItem('access_token')
          // router.push('/login')
          break
        case 403:
          ElMessage.error('权限不足')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        default:
          ElMessage.error(data?.message || '请求失败')
      }
    } else if (error.request) {
      ElMessage.error('网络连接失败')
    } else {
      ElMessage.error('请求配置错误')
    }
    
    return Promise.reject(error)
  }
)

// 传感器类型接口
export interface SensorType {
  id: number
  name: string
  description?: string
  unit?: string
  min_value?: number
  max_value?: number
  created_at: string
  updated_at?: string
}

export interface SensorTypeCreate {
  name: string
  description?: string
  unit?: string
  min_value?: number
  max_value?: number
}

// 传感器接口
export interface Sensor {
  id: number
  sensor_id: string
  name: string
  location?: string
  description?: string
  is_active: boolean
  sensor_type_id: number
  ip_address?: string
  port?: number
  protocol?: string
  sampling_interval: number
  created_at: string
  updated_at?: string
  last_data_time?: string
  sensor_type?: SensorType
}

export interface SensorCreate {
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
}

// 传感器数据接口
export interface SensorData {
  timestamp: string
  sensor_id: string
  value: number
  quality: string
  status?: string
}

export interface SensorDataQuery {
  sensor_ids?: string[]
  start_time?: string
  end_time?: string
  limit?: number
  aggregation?: string
  interval?: string
}

// 网关接口
export interface Gateway {
  id: number
  gateway_id: string
  name: string
  location?: string
  ip_address?: string
  is_online: boolean
  last_heartbeat?: string
  created_at: string
  updated_at?: string
}

// API服务类
export class ApiService {
  // 传感器类型相关
  static async getSensorTypes(): Promise<SensorType[]> {
    const response = await apiClient.get('/api/v1/sensors/types')
    return response.data
  }

  static async createSensorType(data: SensorTypeCreate): Promise<SensorType> {
    const response = await apiClient.post('/api/v1/sensors/types', data)
    return response.data
  }

  static async updateSensorType(id: number, data: Partial<SensorTypeCreate>): Promise<SensorType> {
    const response = await apiClient.put(`/api/v1/sensors/types/${id}`, data)
    return response.data
  }

  static async deleteSensorType(id: number): Promise<void> {
    await apiClient.delete(`/api/v1/sensors/types/${id}`)
  }

  // 传感器相关
  static async getSensors(params?: {
    skip?: number
    limit?: number
    is_active?: boolean
  }): Promise<Sensor[]> {
    const response = await apiClient.get('/api/v1/sensors/', { params })
    return response.data
  }

  static async getSensor(id: number): Promise<Sensor> {
    const response = await apiClient.get(`/api/v1/sensors/${id}`)
    return response.data
  }

  static async createSensor(data: SensorCreate): Promise<Sensor> {
    const response = await apiClient.post('/api/v1/sensors/', data)
    return response.data
  }

  static async updateSensor(id: number, data: Partial<SensorCreate>): Promise<Sensor> {
    const response = await apiClient.put(`/api/v1/sensors/${id}`, data)
    return response.data
  }

  static async deleteSensor(id: number): Promise<void> {
    await apiClient.delete(`/api/v1/sensors/${id}`)
  }

  // 传感器数据相关
  static async querySensorData(query: SensorDataQuery): Promise<SensorData[]> {
    const response = await apiClient.get('/api/v1/sensors/data/query', { params: query })
    return response.data
  }

  static async getLatestData(sensor_ids?: string[]): Promise<SensorData[]> {
    const params = sensor_ids ? { sensor_ids } : {}
    const response = await apiClient.get('/api/v1/sensors/data/latest', { params })
    return response.data
  }

  static async getDataStatistics(params: {
    sensor_id: string
    start_time?: string
    end_time?: string
  }): Promise<any> {
    const response = await apiClient.get('/api/v1/sensors/data/statistics', { params })
    return response.data
  }

  // 获取传感器统计数据
  static async getSensorStatistics(sensorId: string, params?: {
    start_time?: string
    end_time?: string
    aggregation?: string
  }): Promise<any> {
    const response = await apiClient.get(`/api/v1/sensors/${sensorId}/statistics`, { params })
    return response.data
  }

  // 获取传感器历史数据
  static async getSensorHistory(sensorId: string, params?: {
    start_time?: string
    end_time?: string
    limit?: number
    interval?: string
  }): Promise<SensorData[]> {
    const response = await apiClient.get(`/api/v1/sensors/${sensorId}/history`, { params })
    return response.data
  }

  // 网关相关
  static async getGateways(): Promise<Gateway[]> {
    const response = await apiClient.get('/api/v1/sensors/gateways')
    return response.data
  }

  static async createGateway(data: {
    gateway_id: string
    name: string
    location?: string
    ip_address?: string
  }): Promise<Gateway> {
    const response = await apiClient.post('/api/v1/sensors/gateways', data)
    return response.data
  }

  static async updateGateway(id: number, data: Partial<{
    name: string
    location?: string
    ip_address?: string
    is_online?: boolean
  }>): Promise<Gateway> {
    const response = await apiClient.put(`/api/v1/sensors/gateways/${id}`, data)
    return response.data
  }

  static async gatewayHeartbeat(id: number): Promise<void> {
    await apiClient.post(`/api/v1/sensors/gateways/${id}/heartbeat`)
  }

  // 系统统计API
  static async getSystemStats() {
    const response = await apiClient.get('/api/v1/stats')
    return response.data
  }

  static async getHealthCheck() {
    const response = await apiClient.get('/api/v1/health')
    return response.data
  }

  // WebSocket统计API
  static async getWebSocketStats() {
    const response = await apiClient.get('/api/v1/ws/stats')
    return response.data
  }

  // 报警相关API
  static async getAlarms(params?: any) {
    const response = await apiClient.get('/api/v1/alarms', { params })
    return response.data
  }

  static async getAlarm(id: number) {
    const response = await apiClient.get(`/api/v1/alarms/${id}`)
    return response.data
  }

  static async acknowledgeAlarm(id: number) {
    const response = await apiClient.post(`/api/v1/alarms/${id}/acknowledge`)
    return response.data
  }

  static async clearAlarm(id: number) {
    const response = await apiClient.post(`/api/v1/alarms/${id}/clear`)
    return response.data
  }

  // 数据导出API
  static async exportSensorData(params: {
    sensor_ids: number[]
    start_time: string
    end_time: string
    format: 'csv' | 'excel' | 'json'
  }) {
    const response = await apiClient.post('/api/v1/export/sensor-data', params, {
      responseType: 'blob'
    })
    return response.data
  }

  // 配置相关API
  static async getSystemConfig() {
    const response = await apiClient.get('/api/v1/config')
    return response.data
  }

  static async updateSystemConfig(data: any) {
    const response = await apiClient.put('/api/v1/config', data)
    return response.data
  }
}

// WebSocket服务类
export class WebSocketService {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectInterval = 3000
  private messageHandlers: Map<string, Function[]> = new Map()
  private isConnecting = false

  constructor(
    private url: string = 'ws://localhost:8000/api/v1/ws',
    private options: {
      userId?: string
      room?: string
      autoReconnect?: boolean
    } = {}
  ) {
    this.options = { autoReconnect: true, ...options }
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        resolve()
        return
      }

      if (this.isConnecting) {
        reject(new Error('正在连接中'))
        return
      }

      this.isConnecting = true

      try {
        let wsUrl = this.url
        const params = new URLSearchParams()
        
        if (this.options.userId) {
          params.append('user_id', this.options.userId)
        }
        if (this.options.room) {
          params.append('room', this.options.room)
        }
        
        if (params.toString()) {
          wsUrl += `?${params.toString()}`
        }

        this.ws = new WebSocket(wsUrl)

        this.ws.onopen = () => {
          console.log('WebSocket连接已建立')
          this.isConnecting = false
          this.reconnectAttempts = 0
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data)
            this.handleMessage(message)
          } catch (error) {
            console.error('解析WebSocket消息失败:', error)
          }
        }

        this.ws.onclose = (event) => {
          console.log('WebSocket连接已关闭:', event.code, event.reason)
          this.isConnecting = false
          
          if (this.options.autoReconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++
            console.log(`尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)
            setTimeout(() => {
              this.connect().catch(console.error)
            }, this.reconnectInterval)
          }
        }

        this.ws.onerror = (error) => {
          console.error('WebSocket错误:', error)
          this.isConnecting = false
          reject(error)
        }

      } catch (error) {
        this.isConnecting = false
        reject(error)
      }
    })
  }

  disconnect() {
    if (this.ws) {
      this.options.autoReconnect = false
      this.ws.close()
      this.ws = null
    }
  }

  send(message: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    } else {
      console.error('WebSocket未连接')
    }
  }

  on(type: string, handler: Function) {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, [])
    }
    this.messageHandlers.get(type)!.push(handler)
  }

  off(type: string, handler?: Function) {
    if (!this.messageHandlers.has(type)) return
    
    if (handler) {
      const handlers = this.messageHandlers.get(type)!
      const index = handlers.indexOf(handler)
      if (index > -1) {
        handlers.splice(index, 1)
      }
    } else {
      this.messageHandlers.delete(type)
    }
  }

  private handleMessage(message: any) {
    const { type } = message
    if (type && this.messageHandlers.has(type)) {
      const handlers = this.messageHandlers.get(type)!
      handlers.forEach(handler => {
        try {
          handler(message)
        } catch (error) {
          console.error('消息处理器执行失败:', error)
        }
      })
    }
  }

  joinRoom(room: string) {
    this.send({
      type: 'join_room',
      room
    })
  }

  leaveRoom() {
    this.send({
      type: 'leave_room'
    })
  }

  ping() {
    this.send({
      type: 'ping'
    })
  }

  getStats() {
    this.send({
      type: 'get_stats'
    })
  }

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }

  get readyState(): number {
    return this.ws?.readyState ?? WebSocket.CLOSED
  }
}

export default apiClient