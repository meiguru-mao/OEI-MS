import { ref, type Ref } from 'vue'
import type { SensorData } from './api'

export interface WebSocketMessage {
  type: string
  data?: any
  sensor_ids?: string[]
  timestamp?: string
  content?: any
}

export interface SensorDataMessage {
  type: 'sensor_data'
  data: {
    sensor_id: string
    value: number
    timestamp: string
    quality: string
  }
}

export interface SystemMessage {
  type: 'sensor_status' | 'gateway_heartbeat' | 'system_notification'
  sensor_id?: string
  gateway_id?: string
  status?: string
  timestamp: string
  content?: any
}

type MessageHandler = (message: WebSocketMessage) => void
type SensorDataHandler = (data: SensorDataMessage['data']) => void
type SystemMessageHandler = (message: SystemMessage) => void

export class WebSocketService {
  private ws: WebSocket | null = null
  private url: string
  private clientId: string
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectInterval = 3000
  private heartbeatInterval: number | null = null
  private messageHandlers: MessageHandler[] = []
  private sensorDataHandlers: SensorDataHandler[] = []
  private systemMessageHandlers: SystemMessageHandler[] = []
  
  // 响应式状态
  public connected: Ref<boolean> = ref(false)
  public connecting: Ref<boolean> = ref(false)
  public error: Ref<string | null> = ref(null)
  
  constructor(baseUrl?: string) {
    const wsBaseUrl = baseUrl || import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000'
    this.clientId = `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    this.url = `${wsBaseUrl}/api/v1/ws/ws/${this.clientId}`
  }
  
  /**
   * 连接WebSocket
   */
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        resolve()
        return
      }
      
      this.connecting.value = true
      this.error.value = null
      
      try {
        this.ws = new WebSocket(this.url)
        
        this.ws.onopen = () => {
          console.log('WebSocket连接已建立')
          this.connected.value = true
          this.connecting.value = false
          this.reconnectAttempts = 0
          this.startHeartbeat()
          resolve()
        }
        
        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            this.handleMessage(message)
          } catch (error) {
            console.error('解析WebSocket消息失败:', error)
          }
        }
        
        this.ws.onclose = (event) => {
          console.log('WebSocket连接已关闭:', event.code, event.reason)
          this.connected.value = false
          this.connecting.value = false
          this.stopHeartbeat()
          
          // 自动重连
          if (!event.wasClean && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnect()
          }
        }
        
        this.ws.onerror = (error) => {
          console.error('WebSocket错误:', error)
          this.error.value = 'WebSocket连接错误'
          this.connecting.value = false
          reject(error)
        }
        
      } catch (error) {
        this.connecting.value = false
        this.error.value = '创建WebSocket连接失败'
        reject(error)
      }
    })
  }
  
  /**
   * 断开连接
   */
  disconnect(): void {
    this.stopHeartbeat()
    if (this.ws) {
      this.ws.close(1000, '主动断开连接')
      this.ws = null
    }
    this.connected.value = false
  }
  
  /**
   * 重连
   */
  private reconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('达到最大重连次数，停止重连')
      this.error.value = '连接失败，请刷新页面重试'
      return
    }
    
    this.reconnectAttempts++
    console.log(`尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)
    
    setTimeout(() => {
      this.connect().catch(console.error)
    }, this.reconnectInterval)
  }
  
  /**
   * 发送消息
   */
  private send(message: WebSocketMessage): boolean {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('WebSocket未连接，无法发送消息')
      return false
    }
    
    try {
      this.ws.send(JSON.stringify(message))
      return true
    } catch (error) {
      console.error('发送WebSocket消息失败:', error)
      return false
    }
  }
  
  /**
   * 订阅传感器数据
   */
  subscribeSensors(sensorIds: string[]): boolean {
    return this.send({
      type: 'subscribe',
      sensor_ids: sensorIds
    })
  }
  
  /**
   * 取消订阅传感器数据
   */
  unsubscribeSensors(sensorIds: string[]): boolean {
    return this.send({
      type: 'unsubscribe',
      sensor_ids: sensorIds
    })
  }
  
  /**
   * 发送心跳
   */
  private sendHeartbeat(): void {
    this.send({
      type: 'ping',
      timestamp: new Date().toISOString()
    })
  }
  
  /**
   * 开始心跳
   */
  private startHeartbeat(): void {
    this.heartbeatInterval = window.setInterval(() => {
      this.sendHeartbeat()
    }, 30000) // 30秒心跳
  }
  
  /**
   * 停止心跳
   */
  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }
  
  /**
   * 处理接收到的消息
   */
  private handleMessage(message: WebSocketMessage): void {
    // 调用通用消息处理器
    this.messageHandlers.forEach(handler => {
      try {
        handler(message)
      } catch (error) {
        console.error('消息处理器执行失败:', error)
      }
    })
    
    // 根据消息类型分发
    switch (message.type) {
      case 'sensor_data':
        this.sensorDataHandlers.forEach(handler => {
          try {
            handler(message.data)
          } catch (error) {
            console.error('传感器数据处理器执行失败:', error)
          }
        })
        break
        
      case 'sensor_status':
      case 'gateway_heartbeat':
      case 'system_notification':
        this.systemMessageHandlers.forEach(handler => {
          try {
            handler(message as SystemMessage)
          } catch (error) {
            console.error('系统消息处理器执行失败:', error)
          }
        })
        break
        
      case 'pong':
        // 心跳响应
        console.log('收到心跳响应')
        break
        
      case 'subscription_confirmed':
      case 'unsubscription_confirmed':
        console.log(`订阅操作确认: ${message.type}`, message.sensor_ids)
        break
        
      default:
        console.log('未知消息类型:', message.type, message)
    }
  }
  
  /**
   * 添加消息处理器
   */
  onMessage(handler: MessageHandler): () => void {
    this.messageHandlers.push(handler)
    return () => {
      const index = this.messageHandlers.indexOf(handler)
      if (index > -1) {
        this.messageHandlers.splice(index, 1)
      }
    }
  }
  
  /**
   * 添加传感器数据处理器
   */
  onSensorData(handler: SensorDataHandler): () => void {
    this.sensorDataHandlers.push(handler)
    return () => {
      const index = this.sensorDataHandlers.indexOf(handler)
      if (index > -1) {
        this.sensorDataHandlers.splice(index, 1)
      }
    }
  }
  
  /**
   * 添加系统消息处理器
   */
  onSystemMessage(handler: SystemMessageHandler): () => void {
    this.systemMessageHandlers.push(handler)
    return () => {
      const index = this.systemMessageHandlers.indexOf(handler)
      if (index > -1) {
        this.systemMessageHandlers.splice(index, 1)
      }
    }
  }
  
  /**
   * 获取连接状态
   */
  getStatus() {
    return {
      connected: this.connected.value,
      connecting: this.connecting.value,
      error: this.error.value,
      clientId: this.clientId,
      reconnectAttempts: this.reconnectAttempts
    }
  }
}

// 全局WebSocket服务实例
export const websocketService = new WebSocketService()