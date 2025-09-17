#!/bin/bash

# OEI-MS 部署脚本
# 用于快速部署和管理 OEI-MS 系统

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Docker和Docker Compose
check_dependencies() {
    log_info "检查依赖..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    log_success "依赖检查通过"
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    
    mkdir -p mosquitto/data
    mkdir -p mosquitto/log
    mkdir -p backend/logs
    
    # 设置权限
    chmod 755 mosquitto/data
    chmod 755 mosquitto/log
    chmod 755 backend/logs
    
    log_success "目录创建完成"
}

# 生成环境配置文件
generate_env() {
    log_info "生成环境配置文件..."
    
    if [ ! -f .env ]; then
        cat > .env << EOF
# 数据库配置
POSTGRES_DB=oei_ms
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123

# Redis配置
REDIS_PASSWORD=redis123

# JWT配置
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=false

# MQTT配置
MQTT_HOST=mosquitto
MQTT_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=
MQTT_KEEPALIVE=60

# WebSocket配置
WEBSOCKET_PING_INTERVAL=20
WEBSOCKET_PING_TIMEOUT=10

# CORS配置
CORS_ORIGINS=http://localhost:80,http://localhost:3000
EOF
        log_success "环境配置文件已生成: .env"
    else
        log_warning "环境配置文件已存在，跳过生成"
    fi
}

# 构建镜像
build_images() {
    log_info "构建Docker镜像..."
    
    docker-compose build --no-cache
    
    log_success "镜像构建完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    docker-compose up -d
    
    log_success "服务启动完成"
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    
    docker-compose down
    
    log_success "服务已停止"
}

# 重启服务
restart_services() {
    log_info "重启服务..."
    
    docker-compose restart
    
    log_success "服务重启完成"
}

# 查看日志
view_logs() {
    local service=$1
    
    if [ -z "$service" ]; then
        log_info "查看所有服务日志..."
        docker-compose logs -f
    else
        log_info "查看 $service 服务日志..."
        docker-compose logs -f "$service"
    fi
}

# 检查服务状态
check_status() {
    log_info "检查服务状态..."
    
    docker-compose ps
    
    echo ""
    log_info "健康检查..."
    
    # 检查后端API
    if curl -f http://localhost:8000/health &> /dev/null; then
        log_success "后端API服务正常"
    else
        log_error "后端API服务异常"
    fi
    
    # 检查前端
    if curl -f http://localhost/health &> /dev/null; then
        log_success "前端服务正常"
    else
        log_error "前端服务异常"
    fi
}

# 清理资源
cleanup() {
    log_warning "清理Docker资源..."
    
    read -p "确定要清理所有容器、镜像和卷吗？(y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down -v --rmi all
        docker system prune -f
        log_success "清理完成"
    else
        log_info "取消清理"
    fi
}

# 备份数据
backup_data() {
    log_info "备份数据..."
    
    local backup_dir="backup/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # 备份数据库
    docker-compose exec -T postgres pg_dump -U postgres oei_ms > "$backup_dir/database.sql"
    
    # 备份Redis数据
    docker-compose exec -T redis redis-cli --rdb - > "$backup_dir/redis.rdb"
    
    # 备份MQTT数据
    docker cp oei-mosquitto:/mosquitto/data "$backup_dir/mqtt_data"
    
    log_success "数据备份完成: $backup_dir"
}

# 恢复数据
restore_data() {
    local backup_dir=$1
    
    if [ -z "$backup_dir" ]; then
        log_error "请指定备份目录"
        exit 1
    fi
    
    if [ ! -d "$backup_dir" ]; then
        log_error "备份目录不存在: $backup_dir"
        exit 1
    fi
    
    log_warning "恢复数据..."
    
    # 恢复数据库
    if [ -f "$backup_dir/database.sql" ]; then
        docker-compose exec -T postgres psql -U postgres -d oei_ms < "$backup_dir/database.sql"
        log_success "数据库恢复完成"
    fi
    
    # 恢复Redis数据
    if [ -f "$backup_dir/redis.rdb" ]; then
        docker-compose stop redis
        docker cp "$backup_dir/redis.rdb" oei-redis:/data/dump.rdb
        docker-compose start redis
        log_success "Redis数据恢复完成"
    fi
    
    # 恢复MQTT数据
    if [ -d "$backup_dir/mqtt_data" ]; then
        docker cp "$backup_dir/mqtt_data/." oei-mosquitto:/mosquitto/data/
        docker-compose restart mosquitto
        log_success "MQTT数据恢复完成"
    fi
}

# 开发模式
dev_mode() {
    log_info "启动开发模式..."
    
    docker-compose -f docker-compose.dev.yml up -d
    
    log_success "开发环境启动完成"
    log_info "访问地址:"
    echo "  - 前端开发服务器: http://localhost:3000"
    echo "  - 后端API: http://localhost:8001"
    echo "  - pgAdmin: http://localhost:5050"
    echo "  - Redis Commander: http://localhost:8081"
    echo "  - MQTT Explorer: http://localhost:4000"
}

# 显示帮助信息
show_help() {
    echo "OEI-MS 部署脚本"
    echo ""
    echo "用法: $0 [命令] [参数]"
    echo ""
    echo "命令:"
    echo "  init          初始化部署环境"
    echo "  build         构建Docker镜像"
    echo "  start         启动服务"
    echo "  stop          停止服务"
    echo "  restart       重启服务"
    echo "  status        查看服务状态"
    echo "  logs [服务名]  查看日志"
    echo "  backup        备份数据"
    echo "  restore <目录> 恢复数据"
    echo "  cleanup       清理Docker资源"
    echo "  dev           启动开发模式"
    echo "  help          显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 init       # 初始化部署环境"
    echo "  $0 start      # 启动所有服务"
    echo "  $0 logs backend # 查看后端日志"
    echo "  $0 backup     # 备份数据"
}

# 初始化部署环境
init_deployment() {
    log_info "初始化部署环境..."
    
    check_dependencies
    create_directories
    generate_env
    
    log_success "部署环境初始化完成"
    log_info "接下来可以运行: $0 build && $0 start"
}

# 主函数
main() {
    case "$1" in
        init)
            init_deployment
            ;;
        build)
            build_images
            ;;
        start)
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        status)
            check_status
            ;;
        logs)
            view_logs "$2"
            ;;
        backup)
            backup_data
            ;;
        restore)
            restore_data "$2"
            ;;
        cleanup)
            cleanup
            ;;
        dev)
            dev_mode
            ;;
        help|--help|-h)
            show_help
            ;;
        "")
            show_help
            ;;
        *)
            log_error "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"