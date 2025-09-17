# OEI-MS Frontend

基于 Vue 3 + TypeScript 的工业设备监控系统前端应用

## 🏗️ 技术栈

- **框架**: Vue 3.3+ (Composition API)
- **语言**: TypeScript 5.0+
- **构建工具**: Vite 4.0+
- **UI框架**: Element Plus 2.4+
- **图表库**: ECharts 5.4+
- **状态管理**: Pinia 2.1+
- **路由**: Vue Router 4.2+
- **HTTP客户端**: Axios 1.5+
- **WebSocket**: 原生WebSocket API
- **样式**: SCSS + CSS Variables
- **图标**: Element Plus Icons

## 📁 项目结构

```
frontend/
├── public/                  # 静态资源
│   ├── favicon.ico         # 网站图标
│   └── index.html          # HTML模板
├── src/                    # 源代码
│   ├── assets/             # 静态资源
│   │   ├── images/         # 图片资源
│   │   ├── icons/          # 图标资源
│   │   └── styles/         # 全局样式
│   │       ├── index.scss  # 主样式文件
│   │       ├── variables.scss # SCSS变量
│   │       └── mixins.scss # SCSS混入
│   ├── components/         # 公共组件
│   │   ├── common/         # 通用组件
│   │   │   ├── AppHeader.vue
│   │   │   ├── AppSidebar.vue
│   │   │   ├── AppFooter.vue
│   │   │   └── LoadingSpinner.vue
│   │   ├── charts/         # 图表组件
│   │   │   ├── LineChart.vue
│   │   │   ├── BarChart.vue
│   │   │   ├── PieChart.vue
│   │   │   ├── GaugeChart.vue
│   │   │   └── RealTimeChart.vue
│   │   ├── forms/          # 表单组件
│   │   │   ├── SensorForm.vue
│   │   │   ├── GatewayForm.vue
│   │   │   └── AlarmForm.vue
│   │   └── widgets/        # 小部件
│   │       ├── StatCard.vue
│   │       ├── AlarmPanel.vue
│   │       ├── DeviceStatus.vue
│   │       └── DataTable.vue
│   ├── views/              # 页面视图
│   │   ├── Dashboard.vue   # 仪表盘
│   │   ├── Sensors.vue     # 传感器管理
│   │   ├── Gateways.vue    # 网关管理
│   │   ├── DataAnalysis.vue # 数据分析
│   │   ├── Alarms.vue      # 报警管理
│   │   ├── Settings.vue    # 系统设置
│   │   └── Login.vue       # 登录页面
│   ├── router/             # 路由配置
│   │   └── index.ts        # 路由定义
│   ├── stores/             # 状态管理
│   │   ├── auth.ts         # 认证状态
│   │   ├── sensors.ts      # 传感器状态
│   │   ├── gateways.ts     # 网关状态
│   │   ├── alarms.ts       # 报警状态
│   │   └── websocket.ts    # WebSocket状态
│   ├── services/           # API服务
│   │   ├── api.ts          # API基础配置
│   │   ├── auth.ts         # 认证服务
│   │   ├── sensors.ts      # 传感器服务
│   │   ├── gateways.ts     # 网关服务
│   │   ├── data.ts         # 数据服务
│   │   ├── alarms.ts       # 报警服务
│   │   └── websocket.ts    # WebSocket服务
│   ├── utils/              # 工具函数
│   │   ├── index.ts        # 通用工具
│   │   ├── format.ts       # 格式化工具
│   │   ├── validation.ts   # 验证工具
│   │   ├── storage.ts      # 存储工具
│   │   └── constants.ts    # 常量定义
│   ├── types/              # 类型定义
│   │   ├── api.ts          # API类型
│   │   ├── sensor.ts       # 传感器类型
│   │   ├── gateway.ts      # 网关类型
│   │   ├── alarm.ts        # 报警类型
│   │   └── common.ts       # 通用类型
│   ├── composables/        # 组合式函数
│   │   ├── useAuth.ts      # 认证逻辑
│   │   ├── useWebSocket.ts # WebSocket逻辑
│   │   ├── useCharts.ts    # 图表逻辑
│   │   └── useTable.ts     # 表格逻辑
│   ├── App.vue             # 根组件
│   ├── main.ts             # 应用入口
│   └── vite-env.d.ts       # Vite类型声明
├── tests/                  # 测试文件
│   ├── unit/               # 单元测试
│   └── e2e/                # 端到端测试
├── .env                    # 环境变量
├── .env.development        # 开发环境变量
├── .env.production         # 生产环境变量
├── .gitignore              # Git忽略文件
├── .eslintrc.js            # ESLint配置
├── .prettierrc             # Prettier配置
├── index.html              # HTML入口
├── package.json            # 项目配置
├── tsconfig.json           # TypeScript配置
├── vite.config.ts          # Vite配置
├── nginx.conf              # Nginx配置
├── Dockerfile              # Docker配置
├── .dockerignore           # Docker忽略文件
└── README.md               # 项目文档
```

## 🚀 快速开始

### 环境要求

- Node.js 18.0+
- npm 9.0+ 或 yarn 1.22+
- 现代浏览器 (Chrome 90+, Firefox 88+, Safari 14+)

### 本地开发

1. **安装依赖**

```bash
npm install
# 或
yarn install
```

2. **环境配置**

创建 `.env.development` 文件：

```bash
# API配置
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000

# 应用配置
VITE_APP_TITLE=OEI-MS 监控系统
VITE_APP_VERSION=1.0.0

# 功能开关
VITE_ENABLE_MOCK=false
VITE_ENABLE_DEBUG=true
```

3. **启动开发服务器**

```bash
npm run dev
# 或
yarn dev
```

4. **访问应用**

打开浏览器访问: http://localhost:5173

### 构建部署

```bash
# 构建生产版本
npm run build

# 预览构建结果
npm run preview

# 类型检查
npm run type-check

# 代码检查
npm run lint

# 代码格式化
npm run format
```

## 🎨 UI 组件

### 图表组件

#### 实时折线图

```vue
<template>
  <RealTimeChart
    :data="sensorData"
    :options="chartOptions"
    height="400px"
    @point-click="handlePointClick"
  />
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import RealTimeChart from '@/components/charts/RealTimeChart.vue'
import type { ChartData, ChartOptions } from '@/types/charts'

const sensorData = ref<ChartData[]>([])

const chartOptions = computed<ChartOptions>(() => ({
  title: '温度趋势',
  xAxis: { type: 'time' },
  yAxis: { name: '温度 (°C)' },
  series: {
    name: '温度',
    type: 'line',
    smooth: true,
    color: '#409EFF'
  }
}))

const handlePointClick = (point: any) => {
  console.log('点击数据点:', point)
}
</script>
```

#### 仪表盘组件

```vue
<template>
  <GaugeChart
    :value="currentValue"
    :min="0"
    :max="100"
    :thresholds="thresholds"
    :title="title"
    :unit="unit"
  />
</template>

<script setup lang="ts">
import GaugeChart from '@/components/charts/GaugeChart.vue'

interface Props {
  currentValue: number
  title: string
  unit: string
  thresholds?: Array<{ value: number; color: string }>
}

withDefaults(defineProps<Props>(), {
  thresholds: () => [
    { value: 30, color: '#67C23A' },
    { value: 70, color: '#E6A23C' },
    { value: 100, color: '#F56C6C' }
  ]
})
</script>
```

### 数据表格组件

```vue
<template>
  <DataTable
    :data="tableData"
    :columns="columns"
    :loading="loading"
    :pagination="pagination"
    @refresh="handleRefresh"
    @row-click="handleRowClick"
  >
    <template #actions="{ row }">
      <el-button size="small" @click="editRow(row)">编辑</el-button>
      <el-button size="small" type="danger" @click="deleteRow(row)">删除</el-button>
    </template>
  </DataTable>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import DataTable from '@/components/widgets/DataTable.vue'
import type { TableColumn, PaginationConfig } from '@/types/table'

const tableData = ref([])
const loading = ref(false)

const columns: TableColumn[] = [
  { prop: 'id', label: 'ID', width: 80 },
  { prop: 'name', label: '名称', minWidth: 120 },
  { prop: 'type', label: '类型', width: 100 },
  { prop: 'status', label: '状态', width: 100, slot: 'status' },
  { prop: 'actions', label: '操作', width: 150, slot: 'actions' }
]

const pagination = ref<PaginationConfig>({
  current: 1,
  pageSize: 20,
  total: 0
})

const handleRefresh = () => {
  // 刷新数据逻辑
}

const handleRowClick = (row: any) => {
  console.log('点击行:', row)
}
</script>
```

## 🔧 状态管理

### 认证状态

```typescript
// stores/auth.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, LoginCredentials } from '@/types/auth'
import { authService } from '@/services/auth'
import { storage } from '@/utils/storage'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(storage.get('token'))
  const loading = ref(false)

  const isAuthenticated = computed(() => !!token.value)
  const userRole = computed(() => user.value?.role || 'guest')

  const login = async (credentials: LoginCredentials) => {
    loading.value = true
    try {
      const response = await authService.login(credentials)
      token.value = response.access_token
      user.value = response.user
      storage.set('token', response.access_token)
      return response
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    try {
      await authService.logout()
    } finally {
      token.value = null
      user.value = null
      storage.remove('token')
    }
  }

  const refreshToken = async () => {
    try {
      const response = await authService.refresh()
      token.value = response.access_token
      storage.set('token', response.access_token)
    } catch (error) {
      await logout()
      throw error
    }
  }

  return {
    user,
    token,
    loading,
    isAuthenticated,
    userRole,
    login,
    logout,
    refreshToken
  }
})
```

### WebSocket 状态

```typescript
// stores/websocket.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { websocketService } from '@/services/websocket'
import type { WebSocketMessage, ConnectionStatus } from '@/types/websocket'

export const useWebSocketStore = defineStore('websocket', () => {
  const status = ref<ConnectionStatus>('disconnected')
  const messages = ref<WebSocketMessage[]>([])
  const subscriptions = ref<Set<string>>(new Set())

  const isConnected = computed(() => status.value === 'connected')
  const latestMessage = computed(() => messages.value[messages.value.length - 1])

  const connect = async () => {
    status.value = 'connecting'
    try {
      await websocketService.connect()
      status.value = 'connected'
    } catch (error) {
      status.value = 'error'
      throw error
    }
  }

  const disconnect = () => {
    websocketService.disconnect()
    status.value = 'disconnected'
    subscriptions.value.clear()
  }

  const subscribe = (topic: string) => {
    if (isConnected.value) {
      websocketService.subscribe(topic)
      subscriptions.value.add(topic)
    }
  }

  const unsubscribe = (topic: string) => {
    websocketService.unsubscribe(topic)
    subscriptions.value.delete(topic)
  }

  const addMessage = (message: WebSocketMessage) => {
    messages.value.push(message)
    // 保持最近1000条消息
    if (messages.value.length > 1000) {
      messages.value.shift()
    }
  }

  return {
    status,
    messages,
    subscriptions,
    isConnected,
    latestMessage,
    connect,
    disconnect,
    subscribe,
    unsubscribe,
    addMessage
  }
})
```

## 🌐 API 服务

### HTTP 客户端配置

```typescript
// services/api.ts
import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

class ApiClient {
  private instance: AxiosInstance

  constructor() {
    this.instance = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    this.setupInterceptors()
  }

  private setupInterceptors() {
    // 请求拦截器
    this.instance.interceptors.request.use(
      (config) => {
        const authStore = useAuthStore()
        if (authStore.token) {
          config.headers.Authorization = `Bearer ${authStore.token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // 响应拦截器
    this.instance.interceptors.response.use(
      (response) => response,
      async (error) => {
        const authStore = useAuthStore()
        
        if (error.response?.status === 401) {
          try {
            await authStore.refreshToken()
            // 重试原请求
            return this.instance.request(error.config)
          } catch (refreshError) {
            await authStore.logout()
            window.location.href = '/login'
          }
        }

        // 显示错误消息
        const message = error.response?.data?.detail || error.message || '请求失败'
        ElMessage.error(message)
        
        return Promise.reject(error)
      }
    )
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.get<T>(url, config)
    return response.data
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.post<T>(url, data, config)
    return response.data
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.put<T>(url, data, config)
    return response.data
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.delete<T>(url, config)
    return response.data
  }
}

export const apiClient = new ApiClient()
```

### 传感器服务

```typescript
// services/sensors.ts
import { apiClient } from './api'
import type { Sensor, SensorData, CreateSensorRequest, UpdateSensorRequest } from '@/types/sensor'

export const sensorService = {
  // 获取传感器列表
  async getSensors(params?: {
    page?: number
    size?: number
    gateway_id?: number
    type?: string
    is_active?: boolean
  }): Promise<{ items: Sensor[]; total: number }> {
    return apiClient.get('/api/sensors', { params })
  },

  // 获取传感器详情
  async getSensor(id: number): Promise<Sensor> {
    return apiClient.get(`/api/sensors/${id}`)
  },

  // 创建传感器
  async createSensor(data: CreateSensorRequest): Promise<Sensor> {
    return apiClient.post('/api/sensors', data)
  },

  // 更新传感器
  async updateSensor(id: number, data: UpdateSensorRequest): Promise<Sensor> {
    return apiClient.put(`/api/sensors/${id}`, data)
  },

  // 删除传感器
  async deleteSensor(id: number): Promise<void> {
    return apiClient.delete(`/api/sensors/${id}`)
  },

  // 获取传感器数据
  async getSensorData(params: {
    sensor_id?: number
    start_time?: string
    end_time?: string
    limit?: number
  }): Promise<SensorData[]> {
    return apiClient.get('/api/data', { params })
  },

  // 获取最新数据
  async getLatestData(sensor_id?: number): Promise<SensorData[]> {
    return apiClient.get('/api/data/latest', { params: { sensor_id } })
  },

  // 获取统计数据
  async getStatistics(params: {
    sensor_id: number
    start_time: string
    end_time: string
    interval?: string
  }): Promise<any> {
    return apiClient.get('/api/data/statistics', { params })
  }
}
```

## 🔌 WebSocket 集成

### WebSocket 服务

```typescript
// services/websocket.ts
import type { WebSocketMessage } from '@/types/websocket'

class WebSocketService {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectInterval = 5000
  private messageHandlers = new Map<string, Function[]>()

  async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      const wsUrl = import.meta.env.VITE_WS_BASE_URL + '/ws'
      this.ws = new WebSocket(wsUrl)

      this.ws.onopen = () => {
        console.log('WebSocket connected')
        this.reconnectAttempts = 0
        resolve()
      }

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          this.handleMessage(message)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      this.ws.onclose = () => {
        console.log('WebSocket disconnected')
        this.attemptReconnect()
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        reject(error)
      }
    })
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  subscribe(topic: string, handler: Function): void {
    if (!this.messageHandlers.has(topic)) {
      this.messageHandlers.set(topic, [])
    }
    this.messageHandlers.get(topic)!.push(handler)

    // 发送订阅消息
    this.send({
      type: 'subscribe',
      topic
    })
  }

  unsubscribe(topic: string, handler?: Function): void {
    if (handler) {
      const handlers = this.messageHandlers.get(topic)
      if (handlers) {
        const index = handlers.indexOf(handler)
        if (index > -1) {
          handlers.splice(index, 1)
        }
      }
    } else {
      this.messageHandlers.delete(topic)
    }

    // 发送取消订阅消息
    this.send({
      type: 'unsubscribe',
      topic
    })
  }

  private send(message: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    }
  }

  private handleMessage(message: WebSocketMessage): void {
    const handlers = this.messageHandlers.get(message.type)
    if (handlers) {
      handlers.forEach(handler => handler(message))
    }
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
      
      setTimeout(() => {
        this.connect().catch(error => {
          console.error('Reconnection failed:', error)
        })
      }, this.reconnectInterval)
    }
  }
}

export const websocketService = new WebSocketService()
```

## 🎯 组合式函数

### 图表逻辑

```typescript
// composables/useCharts.ts
import { ref, computed, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import type { ECharts, EChartsOption } from 'echarts'

export function useChart(elementRef: Ref<HTMLElement | null>) {
  const chart = ref<ECharts | null>(null)
  const loading = ref(false)

  const initChart = () => {
    if (elementRef.value) {
      chart.value = echarts.init(elementRef.value)
    }
  }

  const setOption = (option: EChartsOption, notMerge = false) => {
    if (chart.value) {
      chart.value.setOption(option, notMerge)
    }
  }

  const resize = () => {
    if (chart.value) {
      chart.value.resize()
    }
  }

  const dispose = () => {
    if (chart.value) {
      chart.value.dispose()
      chart.value = null
    }
  }

  const showLoading = () => {
    loading.value = true
    if (chart.value) {
      chart.value.showLoading()
    }
  }

  const hideLoading = () => {
    loading.value = false
    if (chart.value) {
      chart.value.hideLoading()
    }
  }

  onMounted(() => {
    initChart()
    window.addEventListener('resize', resize)
  })

  onUnmounted(() => {
    dispose()
    window.removeEventListener('resize', resize)
  })

  return {
    chart,
    loading,
    setOption,
    resize,
    showLoading,
    hideLoading
  }
}
```

### 实时数据

```typescript
// composables/useRealTimeData.ts
import { ref, onMounted, onUnmounted } from 'vue'
import { useWebSocketStore } from '@/stores/websocket'
import type { SensorData } from '@/types/sensor'

export function useRealTimeData(sensorId: number, maxPoints = 100) {
  const data = ref<SensorData[]>([])
  const websocketStore = useWebSocketStore()

  const addDataPoint = (point: SensorData) => {
    data.value.push(point)
    // 保持最大数据点数量
    if (data.value.length > maxPoints) {
      data.value.shift()
    }
  }

  const handleMessage = (message: any) => {
    if (message.type === 'sensor_data' && message.sensor_id === sensorId) {
      addDataPoint(message.data)
    }
  }

  onMounted(() => {
    websocketStore.subscribe(`sensor_${sensorId}`, handleMessage)
  })

  onUnmounted(() => {
    websocketStore.unsubscribe(`sensor_${sensorId}`, handleMessage)
  })

  return {
    data,
    addDataPoint
  }
}
```

## 🧪 测试

### 单元测试

```typescript
// tests/unit/components/charts/LineChart.spec.ts
import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import LineChart from '@/components/charts/LineChart.vue'

describe('LineChart', () => {
  it('renders correctly with data', () => {
    const wrapper = mount(LineChart, {
      props: {
        data: [
          { x: '2024-01-01', y: 25 },
          { x: '2024-01-02', y: 30 }
        ],
        options: {
          title: 'Test Chart'
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.chart-container').exists()).toBe(true)
  })

  it('emits point-click event', async () => {
    const wrapper = mount(LineChart, {
      props: {
        data: [{ x: '2024-01-01', y: 25 }]
      }
    })

    // 模拟点击事件
    await wrapper.vm.handlePointClick({ x: '2024-01-01', y: 25 })
    
    expect(wrapper.emitted('point-click')).toBeTruthy()
  })
})
```

### E2E 测试

```typescript
// tests/e2e/dashboard.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Dashboard', () => {
  test('should display dashboard correctly', async ({ page }) => {
    await page.goto('/dashboard')
    
    // 检查页面标题
    await expect(page.locator('h1')).toContainText('仪表盘')
    
    // 检查统计卡片
    await expect(page.locator('.stat-card')).toHaveCount(4)
    
    // 检查图表容器
    await expect(page.locator('.chart-container')).toBeVisible()
  })

  test('should update data in real-time', async ({ page }) => {
    await page.goto('/dashboard')
    
    // 等待WebSocket连接
    await page.waitForTimeout(1000)
    
    // 检查实时数据更新
    const initialValue = await page.locator('.current-value').textContent()
    
    // 等待数据更新
    await page.waitForTimeout(5000)
    
    const updatedValue = await page.locator('.current-value').textContent()
    expect(updatedValue).not.toBe(initialValue)
  })
})
```

## 🎨 样式和主题

### CSS 变量

```scss
// assets/styles/variables.scss
:root {
  // 主色调
  --color-primary: #409eff;
  --color-success: #67c23a;
  --color-warning: #e6a23c;
  --color-danger: #f56c6c;
  --color-info: #909399;

  // 背景色
  --bg-color: #ffffff;
  --bg-color-page: #f2f3f5;
  --bg-color-overlay: #ffffff;

  // 文字颜色
  --text-color-primary: #303133;
  --text-color-regular: #606266;
  --text-color-secondary: #909399;
  --text-color-placeholder: #a8abb2;

  // 边框颜色
  --border-color: #dcdfe6;
  --border-color-light: #e4e7ed;
  --border-color-lighter: #ebeef5;
  --border-color-extra-light: #f2f6fc;

  // 阴影
  --box-shadow-base: 0 2px 4px rgba(0, 0, 0, 0.12), 0 0 6px rgba(0, 0, 0, 0.04);
  --box-shadow-dark: 0 2px 4px rgba(0, 0, 0, 0.12), 0 0 6px rgba(0, 0, 0, 0.12);
  --box-shadow-light: 0 2px 12px 0 rgba(0, 0, 0, 0.1);

  // 圆角
  --border-radius-base: 4px;
  --border-radius-small: 2px;
  --border-radius-round: 20px;
  --border-radius-circle: 100%;

  // 字体
  --font-size-extra-large: 20px;
  --font-size-large: 18px;
  --font-size-medium: 16px;
  --font-size-base: 14px;
  --font-size-small: 13px;
  --font-size-extra-small: 12px;
}

// 暗色主题
[data-theme='dark'] {
  --bg-color: #141414;
  --bg-color-page: #0a0a0a;
  --bg-color-overlay: #1d1e1f;
  
  --text-color-primary: #e5eaf3;
  --text-color-regular: #cfd3dc;
  --text-color-secondary: #a3a6ad;
  --text-color-placeholder: #8d9095;
  
  --border-color: #4c4d4f;
  --border-color-light: #414243;
  --border-color-lighter: #363637;
  --border-color-extra-light: #2b2b2c;
}
```

### 响应式设计

```scss
// assets/styles/mixins.scss
// 断点定义
$breakpoints: (
  xs: 480px,
  sm: 768px,
  md: 992px,
  lg: 1200px,
  xl: 1920px
);

// 响应式混入
@mixin respond-to($breakpoint) {
  @if map-has-key($breakpoints, $breakpoint) {
    @media (min-width: map-get($breakpoints, $breakpoint)) {
      @content;
    }
  }
}

// 使用示例
.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;

  @include respond-to(sm) {
    grid-template-columns: repeat(2, 1fr);
  }

  @include respond-to(lg) {
    grid-template-columns: repeat(3, 1fr);
  }

  @include respond-to(xl) {
    grid-template-columns: repeat(4, 1fr);
  }
}
```

## 🚀 性能优化

### 代码分割

```typescript
// router/index.ts
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue')
  },
  {
    path: '/sensors',
    name: 'Sensors',
    component: () => import('@/views/Sensors.vue')
  },
  {
    path: '/data-analysis',
    name: 'DataAnalysis',
    component: () => import('@/views/DataAnalysis.vue')
  }
]
```

### 组件懒加载

```vue
<template>
  <div>
    <Suspense>
      <template #default>
        <AsyncChart :data="chartData" />
      </template>
      <template #fallback>
        <div class="loading">加载中...</div>
      </template>
    </Suspense>
  </div>
</template>

<script setup lang="ts">
import { defineAsyncComponent } from 'vue'

const AsyncChart = defineAsyncComponent(() => import('@/components/charts/LineChart.vue'))
</script>
```

### 虚拟滚动

```vue
<template>
  <div class="virtual-list" ref="containerRef">
    <div 
      class="virtual-list-phantom" 
      :style="{ height: totalHeight + 'px' }"
    ></div>
    <div 
      class="virtual-list-content"
      :style="{ transform: `translateY(${offsetY}px)` }"
    >
      <div
        v-for="item in visibleItems"
        :key="item.id"
        class="virtual-list-item"
        :style="{ height: itemHeight + 'px' }"
      >
        <slot :item="item" :index="item.index"></slot>
      </div>
    </div>
  </div>
</template>
```

## 📱 移动端适配

### 响应式布局

```vue
<template>
  <div class="mobile-dashboard">
    <!-- 移动端导航 -->
    <div class="mobile-nav" v-if="isMobile">
      <el-tabs v-model="activeTab" type="card">
        <el-tab-pane label="概览" name="overview" />
        <el-tab-pane label="监控" name="monitoring" />
        <el-tab-pane label="报警" name="alarms" />
      </el-tabs>
    </div>

    <!-- 桌面端布局 -->
    <div class="desktop-layout" v-else>
      <aside class="sidebar">
        <!-- 侧边栏内容 -->
      </aside>
      <main class="main-content">
        <!-- 主要内容 -->
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

const screenWidth = ref(window.innerWidth)
const isMobile = computed(() => screenWidth.value < 768)

const handleResize = () => {
  screenWidth.value = window.innerWidth
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>
```

## 🔧 构建配置

### Vite 配置

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import Components from 'unplugin-vue-components/vite'
import AutoImport from 'unplugin-auto-import/vite'

export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      resolvers: [ElementPlusResolver()],
      imports: ['vue', 'vue-router', 'pinia'],
      dts: true
    }),
    Components({
      resolvers: [ElementPlusResolver()],
      dts: true
    })
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  build: {
    target: 'es2015',
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    rollupOptions: {
      output: {
        chunkFileNames: 'js/[name]-[hash].js',
        entryFileNames: 'js/[name]-[hash].js',
        assetFileNames: '[ext]/[name]-[hash].[ext]',
        manualChunks: {
          vendor: ['vue', 'vue-router', 'pinia'],
          element: ['element-plus'],
          echarts: ['echarts']
        }
      }
    }
  },
  server: {
    port: 5173,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true
      }
    }
  }
})
```

## 📚 开发指南

### 代码规范

- 使用 **ESLint** + **Prettier** 进行代码检查和格式化
- 遵循 **Vue 3 Composition API** 最佳实践
- 使用 **TypeScript** 进行类型检查
- 组件命名使用 **PascalCase**
- 文件命名使用 **kebab-case**

### Git 提交规范

```bash
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式调整
refactor: 代码重构
perf: 性能优化
test: 测试相关
chore: 构建过程或辅助工具的变动
```

### 组件开发规范

```vue
<template>
  <!-- 模板内容 -->
</template>

<script setup lang="ts">
// 1. 导入
import { ref, computed, onMounted } from 'vue'
import type { ComponentProps } from '@/types'

// 2. 类型定义
interface Props {
  title: string
  data: any[]
}

interface Emits {
  change: [value: any]
  update: [data: any]
}

// 3. Props 和 Emits
const props = withDefaults(defineProps<Props>(), {
  title: '默认标题'
})

const emit = defineEmits<Emits>()

// 4. 响应式数据
const loading = ref(false)
const items = ref([])

// 5. 计算属性
const filteredItems = computed(() => {
  return items.value.filter(item => item.active)
})

// 6. 方法
const handleClick = () => {
  emit('change', 'value')
}

// 7. 生命周期
onMounted(() => {
  // 初始化逻辑
})
</script>

<style scoped lang="scss">
// 样式
</style>
```

---

更多详细信息请参考主项目 [README](../README.md) 或查看 [在线文档](https://docs.oei-ms.com)。
