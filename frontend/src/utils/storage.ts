/**
 * 本地存储工具函数
 */

/**
 * 存储类型
 */
export type StorageType = 'localStorage' | 'sessionStorage'

/**
 * 存储配置
 */
interface StorageConfig {
  type: StorageType
  prefix?: string
  encrypt?: boolean
}

/**
 * 默认配置
 */
const defaultConfig: StorageConfig = {
  type: 'localStorage',
  prefix: 'oei_ms_',
  encrypt: false
}

/**
 * 获取存储对象
 * @param type 存储类型
 * @returns Storage对象
 */
function getStorage(type: StorageType): Storage {
  return type === 'localStorage' ? localStorage : sessionStorage
}

/**
 * 生成存储键名
 * @param key 原始键名
 * @param prefix 前缀
 * @returns 完整键名
 */
function getStorageKey(key: string, prefix?: string): string {
  return prefix ? `${prefix}${key}` : key
}

/**
 * 简单加密（Base64）
 * @param data 数据
 * @returns 加密后的数据
 */
function encrypt(data: string): string {
  try {
    return btoa(encodeURIComponent(data))
  } catch {
    return data
  }
}

/**
 * 简单解密（Base64）
 * @param data 加密的数据
 * @returns 解密后的数据
 */
function decrypt(data: string): string {
  try {
    return decodeURIComponent(atob(data))
  } catch {
    return data
  }
}

/**
 * 存储管理类
 */
export class StorageManager {
  private config: StorageConfig
  private storage: Storage

  constructor(config: Partial<StorageConfig> = {}) {
    this.config = { ...defaultConfig, ...config }
    this.storage = getStorage(this.config.type)
  }

  /**
   * 设置存储项
   * @param key 键名
   * @param value 值
   * @param options 选项
   */
  set<T>(key: string, value: T, options?: { ttl?: number }): void {
    try {
      const storageKey = getStorageKey(key, this.config.prefix)
      
      const data = {
        value,
        timestamp: Date.now(),
        ttl: options?.ttl
      }
      
      let serialized = JSON.stringify(data)
      
      if (this.config.encrypt) {
        serialized = encrypt(serialized)
      }
      
      this.storage.setItem(storageKey, serialized)
    } catch (error) {
      console.error('Storage set error:', error)
    }
  }

  /**
   * 获取存储项
   * @param key 键名
   * @param defaultValue 默认值
   * @returns 存储的值
   */
  get<T>(key: string, defaultValue?: T): T | undefined {
    try {
      const storageKey = getStorageKey(key, this.config.prefix)
      let item = this.storage.getItem(storageKey)
      
      if (!item) {
        return defaultValue
      }
      
      if (this.config.encrypt) {
        item = decrypt(item)
      }
      
      const data = JSON.parse(item)
      
      // 检查是否过期
      if (data.ttl && Date.now() - data.timestamp > data.ttl * 1000) {
        this.remove(key)
        return defaultValue
      }
      
      return data.value
    } catch (error) {
      console.error('Storage get error:', error)
      return defaultValue
    }
  }

  /**
   * 移除存储项
   * @param key 键名
   */
  remove(key: string): void {
    try {
      const storageKey = getStorageKey(key, this.config.prefix)
      this.storage.removeItem(storageKey)
    } catch (error) {
      console.error('Storage remove error:', error)
    }
  }

  /**
   * 清空所有存储项
   */
  clear(): void {
    try {
      if (this.config.prefix) {
        // 只清空带前缀的项
        const keys = Object.keys(this.storage)
        keys.forEach(key => {
          if (key.startsWith(this.config.prefix!)) {
            this.storage.removeItem(key)
          }
        })
      } else {
        this.storage.clear()
      }
    } catch (error) {
      console.error('Storage clear error:', error)
    }
  }

  /**
   * 检查键是否存在
   * @param key 键名
   * @returns 是否存在
   */
  has(key: string): boolean {
    const storageKey = getStorageKey(key, this.config.prefix)
    return this.storage.getItem(storageKey) !== null
  }

  /**
   * 获取所有键名
   * @returns 键名数组
   */
  keys(): string[] {
    const keys: string[] = []
    const prefix = this.config.prefix || ''
    
    for (let i = 0; i < this.storage.length; i++) {
      const key = this.storage.key(i)
      if (key && key.startsWith(prefix)) {
        keys.push(key.substring(prefix.length))
      }
    }
    
    return keys
  }

  /**
   * 获取存储大小（字节）
   * @returns 存储大小
   */
  size(): number {
    let size = 0
    const prefix = this.config.prefix || ''
    
    for (let i = 0; i < this.storage.length; i++) {
      const key = this.storage.key(i)
      if (key && key.startsWith(prefix)) {
        const value = this.storage.getItem(key)
        if (value) {
          size += key.length + value.length
        }
      }
    }
    
    return size
  }

  /**
   * 获取剩余存储空间（估算）
   * @returns 剩余空间字节数
   */
  remainingSpace(): number {
    const maxSize = 5 * 1024 * 1024 // 5MB (localStorage 通常限制)
    return maxSize - this.size()
  }
}

// 默认存储实例
export const storage = new StorageManager()

// 会话存储实例
export const sessionStorage = new StorageManager({ type: 'sessionStorage' })

// 加密存储实例
export const secureStorage = new StorageManager({ encrypt: true })

/**
 * 快捷存储函数
 */
export const store = {
  /**
   * 设置用户信息
   */
  setUser(user: any): void {
    storage.set('user', user)
  },

  /**
   * 获取用户信息
   */
  getUser(): any {
    return storage.get('user')
  },

  /**
   * 移除用户信息
   */
  removeUser(): void {
    storage.remove('user')
  },

  /**
   * 设置访问令牌
   */
  setToken(token: string): void {
    secureStorage.set('access_token', token)
  },

  /**
   * 获取访问令牌
   */
  getToken(): string | undefined {
    return secureStorage.get('access_token')
  },

  /**
   * 移除访问令牌
   */
  removeToken(): void {
    secureStorage.remove('access_token')
  },

  /**
   * 设置刷新令牌
   */
  setRefreshToken(token: string): void {
    secureStorage.set('refresh_token', token)
  },

  /**
   * 获取刷新令牌
   */
  getRefreshToken(): string | undefined {
    return secureStorage.get('refresh_token')
  },

  /**
   * 移除刷新令牌
   */
  removeRefreshToken(): void {
    secureStorage.remove('refresh_token')
  },

  /**
   * 设置用户偏好设置
   */
  setPreferences(preferences: any): void {
    storage.set('preferences', preferences)
  },

  /**
   * 获取用户偏好设置
   */
  getPreferences(): any {
    return storage.get('preferences', {})
  },

  /**
   * 设置主题
   */
  setTheme(theme: string): void {
    storage.set('theme', theme)
  },

  /**
   * 获取主题
   */
  getTheme(): string {
    return storage.get('theme', 'light')
  },

  /**
   * 设置语言
   */
  setLanguage(language: string): void {
    storage.set('language', language)
  },

  /**
   * 获取语言
   */
  getLanguage(): string {
    return storage.get('language', 'zh-CN')
  },

  /**
   * 清空所有数据
   */
  clearAll(): void {
    storage.clear()
    secureStorage.clear()
  }
}

/**
 * 存储事件监听
 */
export function onStorageChange(callback: (event: StorageEvent) => void): () => void {
  window.addEventListener('storage', callback)
  
  return () => {
    window.removeEventListener('storage', callback)
  }
}

/**
 * 检查存储是否可用
 * @param type 存储类型
 * @returns 是否可用
 */
export function isStorageAvailable(type: StorageType): boolean {
  try {
    const storage = getStorage(type)
    const testKey = '__storage_test__'
    storage.setItem(testKey, 'test')
    storage.removeItem(testKey)
    return true
  } catch {
    return false
  }
}