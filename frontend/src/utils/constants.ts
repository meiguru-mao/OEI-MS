/**
 * 应用常量定义
 */

// API相关常量
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  TIMEOUT: 10000,
  RETRY_TIMES: 3,
  RETRY_DELAY: 1000
} as const

// WebSocket相关常量
export const WEBSOCKET_CONFIG = {
  URL: import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api/v1/ws',
  RECONNECT_INTERVAL: 3000,
  MAX_RECONNECT_ATTEMPTS: 5,
  HEARTBEAT_INTERVAL: 30000,
  PING_TIMEOUT: 5000
} as const

// MQTT相关常量
export const MQTT_CONFIG = {
  BROKER_URL: import.meta.env.VITE_MQTT_BROKER_URL || 'ws://localhost:9001',
  CLIENT_ID_PREFIX: 'oei_ms_client_',
  KEEP_ALIVE: 60,
  CLEAN_SESSION: true,
  RECONNECT_PERIOD: 3000,
  CONNECT_TIMEOUT: 30000
} as const

// MQTT主题常量
export const MQTT_TOPICS = {
  SENSOR_DATA: 'sensors/+/data',
  SENSOR_STATUS: 'sensors/+/status',
  GATEWAY_STATUS: 'gateways/+/status',
  GATEWAY_HEARTBEAT: 'gateways/+/heartbeat',
  SYSTEM_ALERTS: 'system/alerts',
  SYSTEM_STATUS: 'system/status'
} as const

// 传感器相关常量
export const SENSOR_CONFIG = {
  DEFAULT_SAMPLING_INTERVAL: 60, // 秒
  MIN_SAMPLING_INTERVAL: 1,
  MAX_SAMPLING_INTERVAL: 3600,
  DATA_RETENTION_DAYS: 30,
  MAX_HISTORY_POINTS: 1000,
  QUALITY_THRESHOLD: 0.8
} as const

// 传感器状态
export const SENSOR_STATUS = {
  ONLINE: 'online',
  OFFLINE: 'offline',
  UNKNOWN: 'unknown',
  ERROR: 'error',
  MAINTENANCE: 'maintenance'
} as const

// 数据质量等级
export const DATA_QUALITY = {
  EXCELLENT: { min: 0.9, label: '优秀', color: '#10b981' },
  GOOD: { min: 0.8, label: '良好', color: '#3b82f6' },
  FAIR: { min: 0.6, label: '一般', color: '#f59e0b' },
  POOR: { min: 0, label: '较差', color: '#ef4444' }
} as const

// 报警级别
export const ALARM_LEVELS = {
  CRITICAL: { value: 'critical', label: '严重', color: '#dc2626', priority: 1 },
  HIGH: { value: 'high', label: '高', color: '#ea580c', priority: 2 },
  MEDIUM: { value: 'medium', label: '中', color: '#d97706', priority: 3 },
  LOW: { value: 'low', label: '低', color: '#65a30d', priority: 4 },
  INFO: { value: 'info', label: '信息', color: '#0891b2', priority: 5 }
} as const

// 报警状态
export const ALARM_STATUS = {
  ACTIVE: 'active',
  ACKNOWLEDGED: 'acknowledged',
  CLEARED: 'cleared',
  SUPPRESSED: 'suppressed'
} as const

// 时间范围选项
export const TIME_RANGES = {
  '1h': { label: '最近1小时', value: 1 * 60 * 60 * 1000 },
  '6h': { label: '最近6小时', value: 6 * 60 * 60 * 1000 },
  '24h': { label: '最近24小时', value: 24 * 60 * 60 * 1000 },
  '7d': { label: '最近7天', value: 7 * 24 * 60 * 60 * 1000 },
  '30d': { label: '最近30天', value: 30 * 24 * 60 * 60 * 1000 }
} as const

// 图表配置
export const CHART_CONFIG = {
  DEFAULT_HEIGHT: 400,
  ANIMATION_DURATION: 300,
  COLORS: [
    '#3b82f6', '#ef4444', '#10b981', '#f59e0b', 
    '#8b5cf6', '#06b6d4', '#84cc16', '#f97316'
  ],
  GRID: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  }
} as const

// 分页配置
export const PAGINATION_CONFIG = {
  DEFAULT_PAGE_SIZE: 20,
  PAGE_SIZES: [10, 20, 50, 100],
  MAX_PAGE_SIZE: 1000
} as const

// 文件上传配置
export const UPLOAD_CONFIG = {
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
  ALLOWED_TYPES: {
    IMAGE: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
    DOCUMENT: ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
    EXCEL: ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],
    CSV: ['text/csv'],
    JSON: ['application/json']
  }
} as const

// 用户角色
export const USER_ROLES = {
  ADMIN: { value: 'admin', label: '管理员', permissions: ['*'] },
  OPERATOR: { value: 'operator', label: '操作员', permissions: ['read', 'write'] },
  VIEWER: { value: 'viewer', label: '查看者', permissions: ['read'] },
  GUEST: { value: 'guest', label: '访客', permissions: [] }
} as const

// 权限列表
export const PERMISSIONS = {
  // 传感器权限
  SENSOR_READ: 'sensor:read',
  SENSOR_WRITE: 'sensor:write',
  SENSOR_DELETE: 'sensor:delete',
  
  // 网关权限
  GATEWAY_READ: 'gateway:read',
  GATEWAY_WRITE: 'gateway:write',
  GATEWAY_DELETE: 'gateway:delete',
  
  // 报警权限
  ALARM_READ: 'alarm:read',
  ALARM_WRITE: 'alarm:write',
  ALARM_ACK: 'alarm:acknowledge',
  
  // 系统权限
  SYSTEM_CONFIG: 'system:config',
  SYSTEM_MONITOR: 'system:monitor',
  
  // 用户权限
  USER_READ: 'user:read',
  USER_WRITE: 'user:write',
  USER_DELETE: 'user:delete'
} as const

// 主题配置
export const THEME_CONFIG = {
  LIGHT: {
    name: 'light',
    label: '浅色主题',
    colors: {
      primary: '#3b82f6',
      success: '#10b981',
      warning: '#f59e0b',
      danger: '#ef4444',
      info: '#06b6d4'
    }
  },
  DARK: {
    name: 'dark',
    label: '深色主题',
    colors: {
      primary: '#60a5fa',
      success: '#34d399',
      warning: '#fbbf24',
      danger: '#f87171',
      info: '#22d3ee'
    }
  }
} as const

// 语言配置
export const LANGUAGE_CONFIG = {
  'zh-CN': { name: 'zh-CN', label: '简体中文' },
  'en-US': { name: 'en-US', label: 'English' }
} as const

// 数据导出格式
export const EXPORT_FORMATS = {
  CSV: { value: 'csv', label: 'CSV', extension: '.csv' },
  EXCEL: { value: 'excel', label: 'Excel', extension: '.xlsx' },
  JSON: { value: 'json', label: 'JSON', extension: '.json' },
  PDF: { value: 'pdf', label: 'PDF', extension: '.pdf' }
} as const

// 系统配置
export const SYSTEM_CONFIG = {
  APP_NAME: 'OEI-MS',
  APP_VERSION: '1.0.0',
  COPYRIGHT: '© 2024 OEI-MS. All rights reserved.',
  SUPPORT_EMAIL: 'support@oei-ms.com',
  DOCUMENTATION_URL: 'https://docs.oei-ms.com'
} as const

// 正则表达式
export const REGEX_PATTERNS = {
  EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  PHONE: /^1[3-9]\d{9}$/,
  IP_ADDRESS: /^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/,
  MAC_ADDRESS: /^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$/,
  SENSOR_ID: /^[a-zA-Z0-9]{3,20}$/,
  GATEWAY_ID: /^[a-zA-Z0-9]{3,20}$/,
  PASSWORD: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/
} as const

// 错误代码
export const ERROR_CODES = {
  // 网络错误
  NETWORK_ERROR: 'NETWORK_ERROR',
  TIMEOUT_ERROR: 'TIMEOUT_ERROR',
  
  // 认证错误
  UNAUTHORIZED: 'UNAUTHORIZED',
  FORBIDDEN: 'FORBIDDEN',
  TOKEN_EXPIRED: 'TOKEN_EXPIRED',
  
  // 数据错误
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  NOT_FOUND: 'NOT_FOUND',
  CONFLICT: 'CONFLICT',
  
  // 系统错误
  INTERNAL_ERROR: 'INTERNAL_ERROR',
  SERVICE_UNAVAILABLE: 'SERVICE_UNAVAILABLE'
} as const

// 成功消息
export const SUCCESS_MESSAGES = {
  SAVE_SUCCESS: '保存成功',
  DELETE_SUCCESS: '删除成功',
  UPDATE_SUCCESS: '更新成功',
  CREATE_SUCCESS: '创建成功',
  UPLOAD_SUCCESS: '上传成功',
  EXPORT_SUCCESS: '导出成功',
  IMPORT_SUCCESS: '导入成功'
} as const

// 错误消息
export const ERROR_MESSAGES = {
  NETWORK_ERROR: '网络连接失败，请检查网络设置',
  TIMEOUT_ERROR: '请求超时，请稍后重试',
  UNAUTHORIZED: '未授权访问，请重新登录',
  FORBIDDEN: '权限不足，无法执行此操作',
  NOT_FOUND: '请求的资源不存在',
  VALIDATION_ERROR: '数据验证失败，请检查输入',
  INTERNAL_ERROR: '系统内部错误，请联系管理员',
  SERVICE_UNAVAILABLE: '服务暂时不可用，请稍后重试'
} as const

// 本地存储键名
export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USER_INFO: 'user_info',
  PREFERENCES: 'preferences',
  THEME: 'theme',
  LANGUAGE: 'language',
  SIDEBAR_COLLAPSED: 'sidebar_collapsed',
  DASHBOARD_LAYOUT: 'dashboard_layout'
} as const

// 事件名称
export const EVENT_NAMES = {
  // WebSocket事件
  WS_CONNECTED: 'ws:connected',
  WS_DISCONNECTED: 'ws:disconnected',
  WS_ERROR: 'ws:error',
  WS_MESSAGE: 'ws:message',
  
  // 传感器事件
  SENSOR_DATA_UPDATED: 'sensor:data-updated',
  SENSOR_STATUS_CHANGED: 'sensor:status-changed',
  
  // 报警事件
  ALARM_TRIGGERED: 'alarm:triggered',
  ALARM_CLEARED: 'alarm:cleared',
  
  // 系统事件
  SYSTEM_STATUS_CHANGED: 'system:status-changed',
  USER_LOGIN: 'user:login',
  USER_LOGOUT: 'user:logout'
} as const