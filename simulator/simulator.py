#!/usr/bin/env python3
"""
传感器数据模拟器
用于生成模拟的传感器数据并通过MQTT发送到系统
"""

import json
import time
import random
import os
import logging
from datetime import datetime
from typing import Dict, List
import paho.mqtt.client as mqtt
import numpy as np

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SensorSimulator:
    """传感器数据模拟器"""
    
    def __init__(self):
        # MQTT配置
        self.mqtt_host = os.getenv('MQTT_HOST', 'localhost')
        self.mqtt_port = int(os.getenv('MQTT_PORT', 1883))
        self.mqtt_username = os.getenv('MQTT_USERNAME', '')
        self.mqtt_password = os.getenv('MQTT_PASSWORD', '')
        
        # 模拟配置
        self.simulation_interval = int(os.getenv('SIMULATION_INTERVAL', 5))
        self.sensor_count = int(os.getenv('SENSOR_COUNT', 10))
        
        # MQTT客户端
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish
        
        # 如果设置了用户名和密码
        if self.mqtt_username and self.mqtt_password:
            self.client.username_pw_set(self.mqtt_username, self.mqtt_password)
        
        # 传感器配置
        self.sensors = self.initialize_sensors()
        
        # 运行状态
        self.running = False
    
    def initialize_sensors(self) -> List[Dict]:
        """初始化传感器配置"""
        sensor_types = [
            {
                'type': 'temperature',
                'name': '温度传感器',
                'unit': '°C',
                'min_value': -10,
                'max_value': 50,
                'base_value': 25,
                'noise_level': 2
            },
            {
                'type': 'humidity',
                'name': '湿度传感器',
                'unit': '%',
                'min_value': 0,
                'max_value': 100,
                'base_value': 60,
                'noise_level': 5
            },
            {
                'type': 'pressure',
                'name': '压力传感器',
                'unit': 'hPa',
                'min_value': 950,
                'max_value': 1050,
                'base_value': 1013,
                'noise_level': 10
            },
            {
                'type': 'light',
                'name': '光照传感器',
                'unit': 'lux',
                'min_value': 0,
                'max_value': 100000,
                'base_value': 500,
                'noise_level': 100
            },
            {
                'type': 'co2',
                'name': 'CO2传感器',
                'unit': 'ppm',
                'min_value': 300,
                'max_value': 2000,
                'base_value': 400,
                'noise_level': 20
            }
        ]
        
        sensors = []
        for i in range(self.sensor_count):
            sensor_type = sensor_types[i % len(sensor_types)]
            sensor = {
                'id': f'sensor_{i+1:03d}',
                'name': f'{sensor_type["name"]}_{i+1:02d}',
                'type': sensor_type['type'],
                'unit': sensor_type['unit'],
                'location': f'区域{(i // 2) + 1}',
                'gateway_id': f'gateway_{(i // 5) + 1:02d}',
                'min_value': sensor_type['min_value'],
                'max_value': sensor_type['max_value'],
                'base_value': sensor_type['base_value'],
                'noise_level': sensor_type['noise_level'],
                'current_value': sensor_type['base_value'],
                'trend': 0,  # 趋势值
                'last_update': None
            }
            sensors.append(sensor)
        
        return sensors
    
    def on_connect(self, client, userdata, flags, rc):
        """MQTT连接回调"""
        if rc == 0:
            logger.info(f"成功连接到MQTT broker: {self.mqtt_host}:{self.mqtt_port}")
        else:
            logger.error(f"连接MQTT broker失败，错误代码: {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        """MQTT断开连接回调"""
        logger.warning(f"与MQTT broker断开连接，错误代码: {rc}")
    
    def on_publish(self, client, userdata, mid):
        """MQTT发布回调"""
        logger.debug(f"消息发布成功，消息ID: {mid}")
    
    def generate_sensor_value(self, sensor: Dict) -> float:
        """生成传感器数值"""
        # 基于时间的周期性变化
        current_time = datetime.now()
        hour = current_time.hour
        minute = current_time.minute
        
        # 不同类型传感器的时间模式
        if sensor['type'] == 'temperature':
            # 温度有日周期变化
            daily_cycle = 5 * np.sin(2 * np.pi * hour / 24)
            seasonal_offset = random.uniform(-2, 2)
        elif sensor['type'] == 'humidity':
            # 湿度与温度相反
            daily_cycle = -3 * np.sin(2 * np.pi * hour / 24)
            seasonal_offset = random.uniform(-5, 5)
        elif sensor['type'] == 'light':
            # 光照有明显的日周期
            if 6 <= hour <= 18:
                daily_cycle = sensor['base_value'] * 2 * np.sin(np.pi * (hour - 6) / 12)
            else:
                daily_cycle = sensor['base_value'] * 0.1
            seasonal_offset = 0
        else:
            daily_cycle = random.uniform(-1, 1)
            seasonal_offset = random.uniform(-sensor['noise_level']/2, sensor['noise_level']/2)
        
        # 添加随机噪声
        noise = random.gauss(0, sensor['noise_level'] / 3)
        
        # 添加趋势（缓慢变化）
        sensor['trend'] += random.gauss(0, 0.1)
        sensor['trend'] = max(-2, min(2, sensor['trend']))  # 限制趋势范围
        
        # 计算最终值
        value = (
            sensor['base_value'] + 
            daily_cycle + 
            seasonal_offset + 
            noise + 
            sensor['trend']
        )
        
        # 确保值在合理范围内
        value = max(sensor['min_value'], min(sensor['max_value'], value))
        
        # 更新传感器当前值
        sensor['current_value'] = value
        sensor['last_update'] = current_time.isoformat()
        
        return round(value, 2)
    
    def create_sensor_message(self, sensor: Dict) -> Dict:
        """创建传感器消息"""
        value = self.generate_sensor_value(sensor)
        
        # 随机生成一些异常情况
        status = 'normal'
        if random.random() < 0.05:  # 5%概率异常
            status = random.choice(['warning', 'error'])
        elif random.random() < 0.1:  # 10%概率离线
            status = 'offline'
        
        message = {
            'sensor_id': sensor['id'],
            'sensor_name': sensor['name'],
            'sensor_type': sensor['type'],
            'location': sensor['location'],
            'gateway_id': sensor['gateway_id'],
            'value': value,
            'unit': sensor['unit'],
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'metadata': {
                'battery_level': random.randint(20, 100) if status != 'offline' else 0,
                'signal_strength': random.randint(-80, -30) if status != 'offline' else -100,
                'temperature': random.uniform(20, 35),  # 设备温度
                'firmware_version': '1.2.3'
            }
        }
        
        return message
    
    def publish_sensor_data(self, sensor: Dict):
        """发布传感器数据"""
        try:
            message = self.create_sensor_message(sensor)
            topic = f"sensors/{sensor['gateway_id']}/{sensor['id']}/data"
            
            # 发布数据
            result = self.client.publish(
                topic, 
                json.dumps(message), 
                qos=1,
                retain=False
            )
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"发布传感器数据: {sensor['id']} = {message['value']} {sensor['unit']}")
            else:
                logger.error(f"发布传感器数据失败: {sensor['id']}, 错误代码: {result.rc}")
                
        except Exception as e:
            logger.error(f"发布传感器数据异常: {sensor['id']}, 错误: {e}")
    
    def publish_gateway_status(self):
        """发布网关状态"""
        try:
            # 获取所有网关ID
            gateway_ids = list(set(sensor['gateway_id'] for sensor in self.sensors))
            
            for gateway_id in gateway_ids:
                # 获取该网关下的传感器
                gateway_sensors = [s for s in self.sensors if s['gateway_id'] == gateway_id]
                
                status_message = {
                    'gateway_id': gateway_id,
                    'status': 'online',
                    'sensor_count': len(gateway_sensors),
                    'online_sensors': len([s for s in gateway_sensors if s.get('status', 'normal') != 'offline']),
                    'timestamp': datetime.now().isoformat(),
                    'system_info': {
                        'cpu_usage': random.uniform(10, 80),
                        'memory_usage': random.uniform(30, 90),
                        'disk_usage': random.uniform(20, 70),
                        'uptime': random.randint(3600, 86400 * 30),  # 1小时到30天
                        'ip_address': f'192.168.1.{random.randint(100, 200)}'
                    }
                }
                
                topic = f"gateways/{gateway_id}/status"
                result = self.client.publish(
                    topic,
                    json.dumps(status_message),
                    qos=1,
                    retain=True
                )
                
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    logger.debug(f"发布网关状态: {gateway_id}")
                    
        except Exception as e:
            logger.error(f"发布网关状态异常: {e}")
    
    def connect_mqtt(self):
        """连接MQTT broker"""
        try:
            logger.info(f"正在连接MQTT broker: {self.mqtt_host}:{self.mqtt_port}")
            self.client.connect(self.mqtt_host, self.mqtt_port, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            logger.error(f"连接MQTT broker失败: {e}")
            return False
    
    def disconnect_mqtt(self):
        """断开MQTT连接"""
        try:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("已断开MQTT连接")
        except Exception as e:
            logger.error(f"断开MQTT连接异常: {e}")
    
    def run(self):
        """运行模拟器"""
        logger.info(f"启动传感器数据模拟器，传感器数量: {self.sensor_count}，发送间隔: {self.simulation_interval}秒")
        
        # 连接MQTT
        if not self.connect_mqtt():
            logger.error("无法连接MQTT broker，退出")
            return
        
        # 等待连接建立
        time.sleep(2)
        
        self.running = True
        gateway_status_counter = 0
        
        try:
            while self.running:
                # 发布所有传感器数据
                for sensor in self.sensors:
                    self.publish_sensor_data(sensor)
                    time.sleep(0.1)  # 避免发送过快
                
                # 每10次循环发布一次网关状态
                gateway_status_counter += 1
                if gateway_status_counter >= 10:
                    self.publish_gateway_status()
                    gateway_status_counter = 0
                
                logger.info(f"已发布 {len(self.sensors)} 个传感器的数据")
                
                # 等待下一次发送
                time.sleep(self.simulation_interval)
                
        except KeyboardInterrupt:
            logger.info("收到中断信号，正在停止模拟器...")
        except Exception as e:
            logger.error(f"模拟器运行异常: {e}")
        finally:
            self.running = False
            self.disconnect_mqtt()
            logger.info("传感器数据模拟器已停止")

def main():
    """主函数"""
    simulator = SensorSimulator()
    simulator.run()

if __name__ == '__main__':
    main()