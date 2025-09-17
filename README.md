# OEI-MS (Open Equipment Intelligence - Monitoring System)

开放式设备智能监控系统 - 一个基于现代技术栈的工业物联网监控平台

## 📋 项目简介

OEI-MS 是一个功能完整的工业设备监控系统，专为现代工业环境设计。系统采用微服务架构，支持实时数据采集、智能分析、可视化展示和报警管理，为工业设备的智能化管理提供全面解决方案。

## ✨ 核心特性

### 🔧 技术架构
- **前端**: Vue 3 + TypeScript + Element Plus + ECharts
- **后端**: FastAPI + Python 3.11 + SQLAlchemy + Pydantic
- **数据库**: PostgreSQL + Redis
- **消息队列**: MQTT (Eclipse Mosquitto)
- **容器化**: Docker + Docker Compose
- **实时通信**: WebSocket + MQTT

### 📊 功能模块
- **实时监控**: 多传感器数据实时采集和展示
- **数据可视化**: 基于 ECharts 的丰富图表组件
- **智能报警**: 多级报警机制和通知系统
- **设备管理**: 传感器和网关设备统一管理
- **数据分析**: 历史数据分析和趋势预测
- **用户权限**: 基于角色的访问控制
- **系统监控**: 服务健康检查和性能监控

### 🚀 技术亮点
- **高性能**: 异步处理 + 缓存优化
- **高可用**: 微服务架构 + 容器化部署
- **实时性**: WebSocket + MQTT 双重保障
- **可扩展**: 模块化设计 + 插件机制
- **易部署**: 一键 Docker 部署
- **跨平台**: 支持 Windows/Linux/macOS

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端 (Vue3)    │    │  后端 (FastAPI)  │    │  数据库层        │
│                 │    │                 │    │                 │
│ ├─ 仪表盘       │    │ ├─ REST API     │    │ ├─ PostgreSQL   │
│ ├─ 实时监控     │◄──►│ ├─ WebSocket    │◄──►│ ├─ Redis        │
│ ├─ 数据分析     │    │ ├─ MQTT Client  │    │ └─ 时序数据     │
│ ├─ 报警管理     │    │ ├─ 任务调度     │    │                 │
│ └─ 系统管理     │    │ └─ 权限控制     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                ┌─────────────────▼─────────────────┐
                │         消息中间件               │
                │                                 │
                │ ├─ MQTT Broker (Mosquitto)     │
                │ ├─ 设备连接管理                │
                │ ├─ 消息路由                    │
                │ └─ 数据采集                    │
                └─────────────────┬─────────────────┘
                                 │
                ┌─────────────────▼─────────────────┐
                │         设备层                   │
                │                                 │
                │ ├─ 传感器设备                   │
                │ ├─ 网关设备                     │
                │ ├─ 数据模拟器                   │
                │ └─ 第三方设备接入               │
                └─────────────────────────────────┘
```

## 📦 快速开始

### 环境要求

- **Docker**: >= 20.10
- **Docker Compose**: >= 2.0
- **Node.js**: >= 18.0 (开发环境)
- **Python**: >= 3.11 (开发环境)

### 🚀 一键部署

#### Windows 用户

```powershell
# 1. 克隆项目
git clone https://github.com/your-org/oei-ms.git
cd oei-ms

# 2. 初始化环境
.\deploy.ps1 init

# 3. 构建并启动
.\deploy.ps1 build
.\deploy.ps1 start
```

#### Linux/macOS 用户

```bash
# 1. 克隆项目
git clone https://github.com/your-org/oei-ms.git
cd oei-ms

# 2. 初始化环境
chmod +x deploy.sh
./deploy.sh init

# 3. 构建并启动
./deploy.sh build
./deploy.sh start
```

### 🔍 验证部署

部署完成后，访问以下地址验证系统状态：

- **前端应用**: http://localhost
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

## 🛠️ 开发环境

### 启动开发环境

```bash
# 启动开发环境（包含开发工具）
./deploy.sh dev
# 或 Windows: .\deploy.ps1 dev
```

开发环境包含以下工具：

- **pgAdmin**: http://localhost:5050 (数据库管理)
- **Redis Commander**: http://localhost:8081 (Redis管理)
- **MQTT Explorer**: http://localhost:4000 (MQTT调试)

### 本地开发

#### 后端开发

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 📚 详细文档

### 项目结构

```
oei-ms/
├── backend/                 # 后端服务
│   ├── app/                # 应用代码
│   │   ├── api/           # API路由
│   │   ├── core/          # 核心配置
│   │   ├── models/        # 数据模型
│   │   ├── services/      # 业务逻辑
│   │   └── utils/         # 工具函数
│   ├── requirements.txt   # Python依赖
│   └── Dockerfile        # Docker配置
├── frontend/               # 前端应用
│   ├── src/              # 源代码
│   │   ├── components/   # Vue组件
│   │   ├── views/        # 页面视图
│   │   ├── services/     # API服务
│   │   ├── stores/       # 状态管理
│   │   └── utils/        # 工具函数
│   ├── package.json      # Node.js依赖
│   └── Dockerfile        # Docker配置
├── simulator/              # 数据模拟器
├── mosquitto/              # MQTT配置
├── docker-compose.yml      # 生产环境配置
├── docker-compose.dev.yml  # 开发环境配置
├── deploy.sh              # Linux/macOS部署脚本
├── deploy.ps1             # Windows部署脚本
└── README.md              # 项目文档
```

### API 文档

系统启动后，可通过以下地址查看完整的API文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 主要API端点

```
GET    /health              # 健康检查
GET    /api/sensors         # 获取传感器列表
POST   /api/sensors         # 创建传感器
GET    /api/sensors/{id}    # 获取传感器详情
GET    /api/data            # 获取传感器数据
GET    /api/alarms          # 获取报警信息
POST   /api/auth/login      # 用户登录
WS     /ws                  # WebSocket连接
```

## 🔧 配置说明

### 环境变量

系统支持通过环境变量进行配置，主要配置项包括：

```bash
# 数据库配置
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://user:pass@host:port/db

# MQTT配置
MQTT_HOST=localhost
MQTT_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=

# JWT配置
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=false
```

### MQTT 主题结构

```
sensors/{gateway_id}/{sensor_id}/data     # 传感器数据
gateways/{gateway_id}/status              # 网关状态
system/alarms                             # 系统报警
system/commands                           # 系统命令
```

## 🔒 安全特性

- **JWT认证**: 基于Token的用户认证
- **RBAC权限**: 基于角色的访问控制
- **HTTPS支持**: SSL/TLS加密传输
- **输入验证**: 严格的数据验证机制
- **SQL注入防护**: ORM层面的安全保护
- **CORS配置**: 跨域请求安全控制

## 📊 监控和运维

### 系统监控

- **健康检查**: `/health` 端点提供系统状态
- **性能指标**: CPU、内存、磁盘使用率监控
- **服务状态**: 各微服务运行状态监控
- **数据库监控**: 连接池、查询性能监控

### 日志管理

- **结构化日志**: JSON格式日志输出
- **日志级别**: DEBUG/INFO/WARNING/ERROR
- **日志轮转**: 自动日志文件轮转
- **集中收集**: 支持ELK等日志收集系统

### 备份恢复

```bash
# 数据备份
./deploy.sh backup

# 数据恢复
./deploy.sh restore backup/20240101_120000
```

## 🚀 部署选项

### Docker Compose (推荐)

适用于单机部署和开发环境：

```bash
# 生产环境
docker-compose up -d

# 开发环境
docker-compose -f docker-compose.dev.yml up -d
```

### Kubernetes

适用于大规模生产环境，配置文件位于 `k8s/` 目录。

### 云平台部署

支持部署到主流云平台：
- AWS ECS/EKS
- Azure Container Instances/AKS
- Google Cloud Run/GKE
- 阿里云容器服务

## 🤝 贡献指南

我们欢迎社区贡献！请遵循以下步骤：

1. **Fork** 项目到你的GitHub账户
2. **创建** 功能分支 (`git checkout -b feature/AmazingFeature`)
3. **提交** 你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. **推送** 到分支 (`git push origin feature/AmazingFeature`)
5. **创建** Pull Request

### 开发规范

- **代码风格**: 遵循项目现有代码风格
- **提交信息**: 使用清晰的提交信息
- **测试覆盖**: 为新功能添加测试
- **文档更新**: 更新相关文档

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🆘 支持和帮助

### 常见问题

**Q: 如何重置管理员密码？**
A: 可以通过数据库直接修改，或使用管理脚本重置。

**Q: 如何添加新的传感器类型？**
A: 在后端添加新的传感器模型，前端添加对应的显示组件。

**Q: 如何扩展报警规则？**
A: 修改 `app/services/alarm.py` 中的报警逻辑。

### 获取帮助

- **GitHub Issues**: [提交问题](https://github.com/your-org/oei-ms/issues)
- **讨论区**: [GitHub Discussions](https://github.com/your-org/oei-ms/discussions)
- **邮件支持**: support@oei-ms.com
- **文档站点**: https://docs.oei-ms.com

## 🎯 路线图

### v1.1 (计划中)
- [ ] 移动端适配
- [ ] 数据导出功能
- [ ] 更多图表类型
- [ ] 报警规则引擎

### v1.2 (计划中)
- [ ] 机器学习预测
- [ ] 多租户支持
- [ ] 插件系统
- [ ] 国际化支持

### v2.0 (远期)
- [ ] 边缘计算支持
- [ ] 区块链集成
- [ ] AI智能分析
- [ ] 数字孪生

## 🏆 致谢

感谢以下开源项目和贡献者：

- [FastAPI](https://fastapi.tiangolo.com/) - 现代Python Web框架
- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架
- [Element Plus](https://element-plus.org/) - Vue 3组件库
- [ECharts](https://echarts.apache.org/) - 数据可视化库
- [PostgreSQL](https://www.postgresql.org/) - 开源关系数据库
- [Redis](https://redis.io/) - 内存数据库
- [Eclipse Mosquitto](https://mosquitto.org/) - MQTT消息代理

---

<div align="center">
  <p>如果这个项目对你有帮助，请给我们一个 ⭐️</p>
  <p>Made with ❤️ by OEI-MS Team</p>
</div>