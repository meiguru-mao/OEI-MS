/**
 * 日期时间格式化工具函数
 */

/**
 * 格式化日期时间
 * @param date 日期对象或时间戳
 * @param format 格式字符串，默认为 'YYYY-MM-DD HH:mm:ss'
 * @returns 格式化后的日期时间字符串
 */
export function formatDateTime(date: Date | number | string, format: string = 'YYYY-MM-DD HH:mm:ss'): string {
  const d = new Date(date)
  
  if (isNaN(d.getTime())) {
    return '--'
  }
  
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')
  
  return format
    .replace('YYYY', String(year))
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

/**
 * 格式化日期
 * @param date 日期对象或时间戳
 * @returns 格式化后的日期字符串 (YYYY-MM-DD)
 */
export function formatDate(date: Date | number | string): string {
  return formatDateTime(date, 'YYYY-MM-DD')
}

/**
 * 格式化时间
 * @param date 日期对象或时间戳
 * @returns 格式化后的时间字符串 (HH:mm:ss)
 */
export function formatTime(date: Date | number | string): string {
  return formatDateTime(date, 'HH:mm:ss')
}

/**
 * 格式化相对时间
 * @param date 日期对象或时间戳
 * @returns 相对时间字符串 (如: 2分钟前, 1小时前)
 */
export function formatRelativeTime(date: Date | number | string): string {
  const d = new Date(date)
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  
  if (isNaN(d.getTime())) {
    return '--'
  }
  
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  
  if (days > 0) {
    return `${days}天前`
  } else if (hours > 0) {
    return `${hours}小时前`
  } else if (minutes > 0) {
    return `${minutes}分钟前`
  } else if (seconds > 0) {
    return `${seconds}秒前`
  } else {
    return '刚刚'
  }
}

/**
 * 获取时间范围
 * @param range 时间范围类型
 * @returns 开始时间和结束时间
 */
export function getTimeRange(range: '1h' | '24h' | '7d' | '30d'): { startTime: Date; endTime: Date } {
  const endTime = new Date()
  const startTime = new Date()
  
  switch (range) {
    case '1h':
      startTime.setHours(startTime.getHours() - 1)
      break
    case '24h':
      startTime.setHours(startTime.getHours() - 24)
      break
    case '7d':
      startTime.setDate(startTime.getDate() - 7)
      break
    case '30d':
      startTime.setDate(startTime.getDate() - 30)
      break
  }
  
  return { startTime, endTime }
}

/**
 * 判断是否为今天
 * @param date 日期对象或时间戳
 * @returns 是否为今天
 */
export function isToday(date: Date | number | string): boolean {
  const d = new Date(date)
  const today = new Date()
  
  return d.getFullYear() === today.getFullYear() &&
         d.getMonth() === today.getMonth() &&
         d.getDate() === today.getDate()
}

/**
 * 判断是否为昨天
 * @param date 日期对象或时间戳
 * @returns 是否为昨天
 */
export function isYesterday(date: Date | number | string): boolean {
  const d = new Date(date)
  const yesterday = new Date()
  yesterday.setDate(yesterday.getDate() - 1)
  
  return d.getFullYear() === yesterday.getFullYear() &&
         d.getMonth() === yesterday.getMonth() &&
         d.getDate() === yesterday.getDate()
}

/**
 * 获取友好的日期显示
 * @param date 日期对象或时间戳
 * @returns 友好的日期字符串
 */
export function getFriendlyDate(date: Date | number | string): string {
  if (isToday(date)) {
    return `今天 ${formatTime(date)}`
  } else if (isYesterday(date)) {
    return `昨天 ${formatTime(date)}`
  } else {
    return formatDateTime(date)
  }
}

/**
 * 解析ISO日期字符串
 * @param isoString ISO格式的日期字符串
 * @returns Date对象
 */
export function parseISOString(isoString: string): Date {
  return new Date(isoString)
}

/**
 * 转换为ISO字符串
 * @param date 日期对象
 * @returns ISO格式的日期字符串
 */
export function toISOString(date: Date): string {
  return date.toISOString()
}

/**
 * 获取时间戳
 * @param date 日期对象，默认为当前时间
 * @returns 时间戳
 */
export function getTimestamp(date: Date = new Date()): number {
  return date.getTime()
}

/**
 * 从时间戳创建日期
 * @param timestamp 时间戳
 * @returns Date对象
 */
export function fromTimestamp(timestamp: number): Date {
  return new Date(timestamp)
}

/**
 * 格式化持续时间
 * @param milliseconds 毫秒数
 * @returns 格式化后的持续时间字符串
 */
export function formatDuration(milliseconds: number): string {
  const seconds = Math.floor(milliseconds / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  
  if (days > 0) {
    return `${days}天 ${hours % 24}小时`
  } else if (hours > 0) {
    return `${hours}小时 ${minutes % 60}分钟`
  } else if (minutes > 0) {
    return `${minutes}分钟 ${seconds % 60}秒`
  } else {
    return `${seconds}秒`
  }
}

/**
 * 获取月份的天数
 * @param year 年份
 * @param month 月份 (0-11)
 * @returns 该月的天数
 */
export function getDaysInMonth(year: number, month: number): number {
  return new Date(year, month + 1, 0).getDate()
}

/**
 * 获取星期几
 * @param date 日期对象或时间戳
 * @returns 星期几的中文名称
 */
export function getWeekday(date: Date | number | string): string {
  const d = new Date(date)
  const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
  return weekdays[d.getDay()]
}

/**
 * 添加时间
 * @param date 基础日期
 * @param amount 数量
 * @param unit 单位
 * @returns 新的日期对象
 */
export function addTime(date: Date, amount: number, unit: 'seconds' | 'minutes' | 'hours' | 'days' | 'months' | 'years'): Date {
  const result = new Date(date)
  
  switch (unit) {
    case 'seconds':
      result.setSeconds(result.getSeconds() + amount)
      break
    case 'minutes':
      result.setMinutes(result.getMinutes() + amount)
      break
    case 'hours':
      result.setHours(result.getHours() + amount)
      break
    case 'days':
      result.setDate(result.getDate() + amount)
      break
    case 'months':
      result.setMonth(result.getMonth() + amount)
      break
    case 'years':
      result.setFullYear(result.getFullYear() + amount)
      break
  }
  
  return result
}

/**
 * 减去时间
 * @param date 基础日期
 * @param amount 数量
 * @param unit 单位
 * @returns 新的日期对象
 */
export function subtractTime(date: Date, amount: number, unit: 'seconds' | 'minutes' | 'hours' | 'days' | 'months' | 'years'): Date {
  return addTime(date, -amount, unit)
}

/**
 * 获取日期范围内的所有日期
 * @param startDate 开始日期
 * @param endDate 结束日期
 * @returns 日期数组
 */
export function getDateRange(startDate: Date, endDate: Date): Date[] {
  const dates: Date[] = []
  const currentDate = new Date(startDate)
  
  while (currentDate <= endDate) {
    dates.push(new Date(currentDate))
    currentDate.setDate(currentDate.getDate() + 1)
  }
  
  return dates
}

/**
 * 比较两个日期
 * @param date1 日期1
 * @param date2 日期2
 * @returns -1: date1 < date2, 0: date1 = date2, 1: date1 > date2
 */
export function compareDates(date1: Date | number | string, date2: Date | number | string): number {
  const d1 = new Date(date1).getTime()
  const d2 = new Date(date2).getTime()
  
  if (d1 < d2) return -1
  if (d1 > d2) return 1
  return 0
}

/**
 * 检查日期是否在范围内
 * @param date 要检查的日期
 * @param startDate 开始日期
 * @param endDate 结束日期
 * @returns 是否在范围内
 */
export function isDateInRange(date: Date | number | string, startDate: Date | number | string, endDate: Date | number | string): boolean {
  const d = new Date(date).getTime()
  const start = new Date(startDate).getTime()
  const end = new Date(endDate).getTime()
  
  return d >= start && d <= end
}