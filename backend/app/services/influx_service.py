from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.core.database import get_influx_client, get_write_api, get_query_api
from app.core.config import settings
from app.schemas.sensor import SensorDataCreate, SensorDataQuery, SensorDataPoint


class InfluxService:
    """InfluxDB服务类"""
    
    @staticmethod
    async def write_sensor_data(data: SensorDataCreate):
        """写入传感器数据到InfluxDB"""
        try:
            write_api = get_write_api()
            
            point = Point("sensor_data") \
                .tag("sensor_id", str(data.sensor_id)) \
                .tag("quality", data.quality) \
                .field("value", data.value) \
                .time(data.timestamp)
            
            if data.status:
                point = point.tag("status", data.status)
            
            write_api.write(
                bucket=settings.INFLUXDB_BUCKET,
                org=settings.INFLUXDB_ORG,
                record=point
            )
            
        except Exception as e:
            print(f"写入InfluxDB失败: {e}")
            raise
    
    @staticmethod
    async def write_sensor_data_batch(data_points: List[SensorDataPoint]):
        """批量写入传感器数据"""
        try:
            write_api = get_write_api()
            points = []
            
            for data in data_points:
                point = Point("sensor_data") \
                    .tag("sensor_id", data.sensor_id) \
                    .tag("quality", data.quality) \
                    .field("value", data.value) \
                    .time(data.timestamp)
                points.append(point)
            
            write_api.write(
                bucket=settings.INFLUXDB_BUCKET,
                org=settings.INFLUXDB_ORG,
                record=points
            )
            
        except Exception as e:
            print(f"批量写入InfluxDB失败: {e}")
            raise
    
    @staticmethod
    async def query_sensor_data(query_params: SensorDataQuery) -> List[Dict[str, Any]]:
        """查询传感器数据"""
        try:
            query_api = get_query_api()
            
            # 构建查询语句
            flux_query = f'from(bucket: "{settings.INFLUXDB_BUCKET}")'
            
            # 时间范围
            if query_params.start_time and query_params.end_time:
                start_time = query_params.start_time.isoformat() + "Z"
                end_time = query_params.end_time.isoformat() + "Z"
                flux_query += f' |> range(start: {start_time}, stop: {end_time})'
            elif query_params.start_time:
                start_time = query_params.start_time.isoformat() + "Z"
                flux_query += f' |> range(start: {start_time})'
            else:
                # 默认查询最近24小时
                flux_query += ' |> range(start: -24h)'
            
            # 过滤测量名称
            flux_query += ' |> filter(fn: (r) => r._measurement == "sensor_data")'
            
            # 传感器ID过滤
            if query_params.sensor_ids:
                sensor_filter = ' or '.join([f'r.sensor_id == "{sid}"' for sid in query_params.sensor_ids])
                flux_query += f' |> filter(fn: (r) => {sensor_filter})'
            
            # 聚合
            if query_params.aggregation and query_params.interval:
                flux_query += f' |> aggregateWindow(every: {query_params.interval}, fn: {query_params.aggregation})'
            
            # 限制条数
            flux_query += f' |> limit(n: {query_params.limit})'
            
            # 执行查询
            result = query_api.query(flux_query, org=settings.INFLUXDB_ORG)
            
            # 处理结果
            data_points = []
            for table in result:
                for record in table.records:
                    data_points.append({
                        "timestamp": record.get_time(),
                        "sensor_id": record.values.get("sensor_id"),
                        "value": record.get_value(),
                        "quality": record.values.get("quality"),
                        "status": record.values.get("status")
                    })
            
            return data_points
            
        except Exception as e:
            print(f"查询InfluxDB失败: {e}")
            raise
    
    @staticmethod
    async def get_latest_data(sensor_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """获取最新数据"""
        try:
            query_api = get_query_api()
            
            flux_query = f'from(bucket: "{settings.INFLUXDB_BUCKET}")' \
                        ' |> range(start: -1h)' \
                        ' |> filter(fn: (r) => r._measurement == "sensor_data")'
            
            if sensor_ids:
                sensor_filter = ' or '.join([f'r.sensor_id == "{sid}"' for sid in sensor_ids])
                flux_query += f' |> filter(fn: (r) => {sensor_filter})'
            
            flux_query += ' |> group(columns: ["sensor_id"])' \
                         ' |> last()'
            
            result = query_api.query(flux_query, org=settings.INFLUXDB_ORG)
            
            latest_data = []
            for table in result:
                for record in table.records:
                    latest_data.append({
                        "timestamp": record.get_time(),
                        "sensor_id": record.values.get("sensor_id"),
                        "value": record.get_value(),
                        "quality": record.values.get("quality"),
                        "status": record.values.get("status")
                    })
            
            return latest_data
            
        except Exception as e:
            print(f"获取最新数据失败: {e}")
            raise
    
    @staticmethod
    async def get_data_statistics(
        sensor_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """获取数据统计信息"""
        try:
            query_api = get_query_api()
            
            # 默认时间范围
            if not start_time:
                start_time = datetime.now() - timedelta(days=1)
            if not end_time:
                end_time = datetime.now()
            
            start_str = start_time.isoformat() + "Z"
            end_str = end_time.isoformat() + "Z"
            
            # 统计查询
            stats_query = f'''
            from(bucket: "{settings.INFLUXDB_BUCKET}")
                |> range(start: {start_str}, stop: {end_str})
                |> filter(fn: (r) => r._measurement == "sensor_data")
                |> filter(fn: (r) => r.sensor_id == "{sensor_id}")
                |> group()
            '''
            
            # 获取各种统计值
            stats = {}
            
            # 平均值
            mean_query = stats_query + ' |> mean()'
            mean_result = query_api.query(mean_query, org=settings.INFLUXDB_ORG)
            if mean_result and mean_result[0].records:
                stats['mean'] = mean_result[0].records[0].get_value()
            
            # 最大值
            max_query = stats_query + ' |> max()'
            max_result = query_api.query(max_query, org=settings.INFLUXDB_ORG)
            if max_result and max_result[0].records:
                stats['max'] = max_result[0].records[0].get_value()
            
            # 最小值
            min_query = stats_query + ' |> min()'
            min_result = query_api.query(min_query, org=settings.INFLUXDB_ORG)
            if min_result and min_result[0].records:
                stats['min'] = min_result[0].records[0].get_value()
            
            # 计数
            count_query = stats_query + ' |> count()'
            count_result = query_api.query(count_query, org=settings.INFLUXDB_ORG)
            if count_result and count_result[0].records:
                stats['count'] = count_result[0].records[0].get_value()
            
            return {
                "sensor_id": sensor_id,
                "start_time": start_time,
                "end_time": end_time,
                "statistics": stats
            }
            
        except Exception as e:
            print(f"获取统计信息失败: {e}")
            raise