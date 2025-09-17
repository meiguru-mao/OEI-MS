/**
 * 验证工具函数
 */

/**
 * 验证邮箱格式
 * @param email 邮箱地址
 * @returns 是否有效
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * 验证手机号格式
 * @param phone 手机号
 * @returns 是否有效
 */
export function isValidPhone(phone: string): boolean {
  const phoneRegex = /^1[3-9]\d{9}$/
  return phoneRegex.test(phone)
}

/**
 * 验证身份证号格式
 * @param idCard 身份证号
 * @returns 是否有效
 */
export function isValidIdCard(idCard: string): boolean {
  const idCardRegex = /^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$/
  return idCardRegex.test(idCard)
}

/**
 * 验证密码强度
 * @param password 密码
 * @returns 强度等级 (0-4)
 */
export function getPasswordStrength(password: string): number {
  if (!password) return 0
  
  let strength = 0
  
  // 长度检查
  if (password.length >= 8) strength++
  if (password.length >= 12) strength++
  
  // 字符类型检查
  if (/[a-z]/.test(password)) strength++
  if (/[A-Z]/.test(password)) strength++
  if (/\d/.test(password)) strength++
  if (/[^\w\s]/.test(password)) strength++
  
  return Math.min(strength, 4)
}

/**
 * 验证密码格式
 * @param password 密码
 * @returns 是否有效
 */
export function isValidPassword(password: string): boolean {
  // 至少8位，包含大小写字母和数字
  const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/
  return passwordRegex.test(password)
}

/**
 * 验证URL格式
 * @param url URL地址
 * @returns 是否有效
 */
export function isValidUrl(url: string): boolean {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

/**
 * 验证IP地址格式
 * @param ip IP地址
 * @returns 是否有效
 */
export function isValidIP(ip: string): boolean {
  const ipRegex = /^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
  return ipRegex.test(ip)
}

/**
 * 验证端口号
 * @param port 端口号
 * @returns 是否有效
 */
export function isValidPort(port: number | string): boolean {
  const portNum = typeof port === 'string' ? parseInt(port, 10) : port
  return Number.isInteger(portNum) && portNum >= 1 && portNum <= 65535
}

/**
 * 验证MAC地址格式
 * @param mac MAC地址
 * @returns 是否有效
 */
export function isValidMAC(mac: string): boolean {
  const macRegex = /^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$/
  return macRegex.test(mac)
}

/**
 * 验证数字范围
 * @param value 数值
 * @param min 最小值
 * @param max 最大值
 * @returns 是否在范围内
 */
export function isInRange(value: number, min: number, max: number): boolean {
  return value >= min && value <= max
}

/**
 * 验证字符串长度
 * @param str 字符串
 * @param min 最小长度
 * @param max 最大长度
 * @returns 是否在长度范围内
 */
export function isValidLength(str: string, min: number, max: number): boolean {
  return str.length >= min && str.length <= max
}

/**
 * 验证是否为空
 * @param value 值
 * @returns 是否为空
 */
export function isEmpty(value: any): boolean {
  if (value === null || value === undefined) return true
  if (typeof value === 'string') return value.trim() === ''
  if (Array.isArray(value)) return value.length === 0
  if (typeof value === 'object') return Object.keys(value).length === 0
  return false
}

/**
 * 验证是否为数字
 * @param value 值
 * @returns 是否为数字
 */
export function isNumber(value: any): boolean {
  return typeof value === 'number' && !isNaN(value)
}

/**
 * 验证是否为整数
 * @param value 值
 * @returns 是否为整数
 */
export function isInteger(value: any): boolean {
  return Number.isInteger(value)
}

/**
 * 验证是否为正数
 * @param value 值
 * @returns 是否为正数
 */
export function isPositive(value: number): boolean {
  return isNumber(value) && value > 0
}

/**
 * 验证是否为非负数
 * @param value 值
 * @returns 是否为非负数
 */
export function isNonNegative(value: number): boolean {
  return isNumber(value) && value >= 0
}

/**
 * 验证JSON字符串
 * @param str JSON字符串
 * @returns 是否为有效JSON
 */
export function isValidJSON(str: string): boolean {
  try {
    JSON.parse(str)
    return true
  } catch {
    return false
  }
}

/**
 * 验证日期格式
 * @param dateStr 日期字符串
 * @returns 是否为有效日期
 */
export function isValidDate(dateStr: string): boolean {
  const date = new Date(dateStr)
  return !isNaN(date.getTime())
}

/**
 * 验证传感器ID格式
 * @param sensorId 传感器ID
 * @returns 是否有效
 */
export function isValidSensorId(sensorId: string): boolean {
  // 传感器ID格式：字母数字组合，3-20位
  const sensorIdRegex = /^[a-zA-Z0-9]{3,20}$/
  return sensorIdRegex.test(sensorId)
}

/**
 * 验证网关ID格式
 * @param gatewayId 网关ID
 * @returns 是否有效
 */
export function isValidGatewayId(gatewayId: string): boolean {
  // 网关ID格式：字母数字组合，3-20位
  const gatewayIdRegex = /^[a-zA-Z0-9]{3,20}$/
  return gatewayIdRegex.test(gatewayId)
}

/**
 * 验证MQTT主题格式
 * @param topic MQTT主题
 * @returns 是否有效
 */
export function isValidMQTTTopic(topic: string): boolean {
  // MQTT主题不能包含通配符 + 和 #（除非是订阅）
  const topicRegex = /^[^+#\s]+$/
  return topicRegex.test(topic)
}

/**
 * 验证采样间隔
 * @param interval 采样间隔（秒）
 * @returns 是否有效
 */
export function isValidSamplingInterval(interval: number): boolean {
  return isInteger(interval) && interval >= 1 && interval <= 3600
}

/**
 * 验证传感器数值范围
 * @param value 传感器数值
 * @param min 最小值
 * @param max 最大值
 * @returns 是否在有效范围内
 */
export function isValidSensorValue(value: number, min?: number, max?: number): boolean {
  if (!isNumber(value)) return false
  
  if (min !== undefined && value < min) return false
  if (max !== undefined && value > max) return false
  
  return true
}

/**
 * 验证数据质量值
 * @param quality 数据质量 (0-1)
 * @returns 是否有效
 */
export function isValidDataQuality(quality: number): boolean {
  return isNumber(quality) && quality >= 0 && quality <= 1
}