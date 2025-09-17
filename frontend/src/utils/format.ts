/**
 * 格式化工具函数
 */

/**
 * 格式化数值
 * @param value 数值
 * @param precision 精度
 * @returns 格式化后的数值字符串
 */
export function formatNumber(value: number, precision: number = 2): string {
  if (typeof value !== 'number' || isNaN(value)) return '--'
  
  // 根据数值大小选择合适的精度
  if (Math.abs(value) >= 1000000) {
    return (value / 1000000).toFixed(1) + 'M'
  } else if (Math.abs(value) >= 1000) {
    return (value / 1000).toFixed(1) + 'K'
  } else if (Math.abs(value) >= 1) {
    return value.toFixed(precision)
  } else {
    return value.toFixed(Math.max(precision, 4))
  }
}

/**
 * 格式化百分比
 * @param value 数值 (0-1)
 * @param precision 精度
 * @returns 格式化后的百分比字符串
 */
export function formatPercentage(value: number, precision: number = 1): string {
  if (typeof value !== 'number' || isNaN(value)) return '--'
  return (value * 100).toFixed(precision) + '%'
}

/**
 * 格式化文件大小
 * @param bytes 字节数
 * @returns 格式化后的文件大小字符串
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

/**
 * 格式化货币
 * @param value 数值
 * @param currency 货币符号
 * @returns 格式化后的货币字符串
 */
export function formatCurrency(value: number, currency: string = '¥'): string {
  if (typeof value !== 'number' || isNaN(value)) return '--'
  return currency + value.toLocaleString('zh-CN', { minimumFractionDigits: 2 })
}

/**
 * 格式化电话号码
 * @param phone 电话号码
 * @returns 格式化后的电话号码
 */
export function formatPhone(phone: string): string {
  if (!phone) return '--'
  const cleaned = phone.replace(/\D/g, '')
  
  if (cleaned.length === 11) {
    return cleaned.replace(/(\d{3})(\d{4})(\d{4})/, '$1-$2-$3')
  }
  
  return phone
}

/**
 * 格式化身份证号
 * @param idCard 身份证号
 * @returns 格式化后的身份证号（脱敏）
 */
export function formatIdCard(idCard: string): string {
  if (!idCard || idCard.length !== 18) return '--'
  return idCard.replace(/(\d{6})\d{8}(\d{4})/, '$1********$2')
}

/**
 * 格式化银行卡号
 * @param cardNumber 银行卡号
 * @returns 格式化后的银行卡号（脱敏）
 */
export function formatBankCard(cardNumber: string): string {
  if (!cardNumber) return '--'
  const cleaned = cardNumber.replace(/\D/g, '')
  
  if (cleaned.length >= 16) {
    return cleaned.replace(/(\d{4})\d*(\d{4})/, '$1 **** **** $2')
  }
  
  return cardNumber
}

/**
 * 格式化邮箱（脱敏）
 * @param email 邮箱地址
 * @returns 格式化后的邮箱地址
 */
export function formatEmail(email: string): string {
  if (!email || !email.includes('@')) return '--'
  
  const [username, domain] = email.split('@')
  if (username.length <= 2) return email
  
  const maskedUsername = username.charAt(0) + '*'.repeat(username.length - 2) + username.charAt(username.length - 1)
  return maskedUsername + '@' + domain
}

/**
 * 格式化地址（省略中间部分）
 * @param address 地址
 * @param maxLength 最大长度
 * @returns 格式化后的地址
 */
export function formatAddress(address: string, maxLength: number = 30): string {
  if (!address) return '--'
  
  if (address.length <= maxLength) return address
  
  const start = address.substring(0, Math.floor(maxLength / 2))
  const end = address.substring(address.length - Math.floor(maxLength / 2))
  
  return start + '...' + end
}

/**
 * 格式化JSON字符串
 * @param obj 对象
 * @param indent 缩进空格数
 * @returns 格式化后的JSON字符串
 */
export function formatJSON(obj: any, indent: number = 2): string {
  try {
    return JSON.stringify(obj, null, indent)
  } catch (error) {
    return String(obj)
  }
}

/**
 * 格式化温度
 * @param value 温度值
 * @param unit 单位 ('C' | 'F' | 'K')
 * @returns 格式化后的温度字符串
 */
export function formatTemperature(value: number, unit: 'C' | 'F' | 'K' = 'C'): string {
  if (typeof value !== 'number' || isNaN(value)) return '--'
  
  const unitSymbols = {
    C: '°C',
    F: '°F',
    K: 'K'
  }
  
  return value.toFixed(1) + unitSymbols[unit]
}

/**
 * 格式化压力值
 * @param value 压力值
 * @param unit 单位
 * @returns 格式化后的压力字符串
 */
export function formatPressure(value: number, unit: string = 'Pa'): string {
  if (typeof value !== 'number' || isNaN(value)) return '--'
  
  if (unit === 'Pa' && value >= 1000) {
    return (value / 1000).toFixed(2) + ' kPa'
  }
  
  return value.toFixed(2) + ' ' + unit
}

/**
 * 格式化电压值
 * @param value 电压值
 * @param unit 单位
 * @returns 格式化后的电压字符串
 */
export function formatVoltage(value: number, unit: string = 'V'): string {
  if (typeof value !== 'number' || isNaN(value)) return '--'
  
  if (value >= 1000) {
    return (value / 1000).toFixed(2) + ' kV'
  } else if (value < 1) {
    return (value * 1000).toFixed(0) + ' mV'
  }
  
  return value.toFixed(2) + ' ' + unit
}

/**
 * 格式化电流值
 * @param value 电流值
 * @param unit 单位
 * @returns 格式化后的电流字符串
 */
export function formatCurrent(value: number, unit: string = 'A'): string {
  if (typeof value !== 'number' || isNaN(value)) return '--'
  
  if (value < 1) {
    return (value * 1000).toFixed(0) + ' mA'
  }
  
  return value.toFixed(2) + ' ' + unit
}