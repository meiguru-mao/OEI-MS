# OEI-MS 部署脚本 (PowerShell版本)
# 用于快速部署和管理 OEI-MS 系统

param(
    [Parameter(Position=0)]
    [string]$Command,
    [Parameter(Position=1)]
    [string]$Parameter
)

# 颜色定义
$Colors = @{
    Red = 'Red'
    Green = 'Green'
    Yellow = 'Yellow'
    Blue = 'Blue'
    White = 'White'
}

# 日志函数
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor $Colors.Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor $Colors.Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $Colors.Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Colors.Red
}

# 检查Docker和Docker Compose
function Test-Dependencies {
    Write-Info "检查依赖..."
    
    try {
        $null = Get-Command docker -ErrorAction Stop
    }
    catch {
        Write-Error "Docker 未安装，请先安装 Docker Desktop"
        exit 1
    }
    
    try {
        $null = Get-Command docker-compose -ErrorAction Stop
    }
    catch {
        Write-Error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    }
    
    Write-Success "依赖检查通过"
}

# 创建必要的目录
function New-RequiredDirectories {
    Write-Info "创建必要的目录..."
    
    $directories = @(
        "mosquitto\data",
        "mosquitto\log",
        "backend\logs"
    )
    
    foreach ($dir in $directories) {
        if (!(Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }
    
    Write-Success "目录创建完成"
}

# 生成环境配置文件
function New-EnvironmentFile {
    Write-Info "生成环境配置文件..."
    
    if (!(Test-Path ".env")) {
        $secretKey = [System.Web.Security.Membership]::GeneratePassword(64, 0)
        
        $envContent = @"
# 数据库配置
POSTGRES_DB=oei_ms
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123

# Redis配置
REDIS_PASSWORD=redis123

# JWT配置
SECRET_KEY=$secretKey
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
"@
        
        $envContent | Out-File -FilePath ".env" -Encoding UTF8
        Write-Success "环境配置文件已生成: .env"
    }
    else {
        Write-Warning "环境配置文件已存在，跳过生成"
    }
}

# 构建镜像
function Build-Images {
    Write-Info "构建Docker镜像..."
    
    try {
        docker-compose build --no-cache
        Write-Success "镜像构建完成"
    }
    catch {
        Write-Error "镜像构建失败: $_"
        exit 1
    }
}

# 启动服务
function Start-Services {
    Write-Info "启动服务..."
    
    try {
        docker-compose up -d
        Write-Success "服务启动完成"
    }
    catch {
        Write-Error "服务启动失败: $_"
        exit 1
    }
}

# 停止服务
function Stop-Services {
    Write-Info "停止服务..."
    
    try {
        docker-compose down
        Write-Success "服务已停止"
    }
    catch {
        Write-Error "服务停止失败: $_"
        exit 1
    }
}

# 重启服务
function Restart-Services {
    Write-Info "重启服务..."
    
    try {
        docker-compose restart
        Write-Success "服务重启完成"
    }
    catch {
        Write-Error "服务重启失败: $_"
        exit 1
    }
}

# 查看日志
function Show-Logs {
    param([string]$Service)
    
    if ([string]::IsNullOrEmpty($Service)) {
        Write-Info "查看所有服务日志..."
        docker-compose logs -f
    }
    else {
        Write-Info "查看 $Service 服务日志..."
        docker-compose logs -f $Service
    }
}

# 检查服务状态
function Test-ServiceStatus {
    Write-Info "检查服务状态..."
    
    docker-compose ps
    
    Write-Host ""
    Write-Info "健康检查..."
    
    # 检查后端API
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Success "后端API服务正常"
        }
    }
    catch {
        Write-Error "后端API服务异常"
    }
    
    # 检查前端
    try {
        $response = Invoke-WebRequest -Uri "http://localhost/health" -TimeoutSec 5 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Success "前端服务正常"
        }
    }
    catch {
        Write-Error "前端服务异常"
    }
}

# 清理资源
function Remove-DockerResources {
    Write-Warning "清理Docker资源..."
    
    $confirmation = Read-Host "确定要清理所有容器、镜像和卷吗？(y/N)"
    
    if ($confirmation -eq 'y' -or $confirmation -eq 'Y') {
        try {
            docker-compose down -v --rmi all
            docker system prune -f
            Write-Success "清理完成"
        }
        catch {
            Write-Error "清理失败: $_"
        }
    }
    else {
        Write-Info "取消清理"
    }
}

# 备份数据
function Backup-Data {
    Write-Info "备份数据..."
    
    $backupDir = "backup\$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    
    try {
        # 备份数据库
        docker-compose exec -T postgres pg_dump -U postgres oei_ms | Out-File -FilePath "$backupDir\database.sql" -Encoding UTF8
        
        # 备份Redis数据
        docker-compose exec -T redis redis-cli --rdb - | Set-Content -Path "$backupDir\redis.rdb" -Encoding Byte
        
        # 备份MQTT数据
        docker cp oei-mosquitto:/mosquitto/data "$backupDir\mqtt_data"
        
        Write-Success "数据备份完成: $backupDir"
    }
    catch {
        Write-Error "数据备份失败: $_"
    }
}

# 恢复数据
function Restore-Data {
    param([string]$BackupDir)
    
    if ([string]::IsNullOrEmpty($BackupDir)) {
        Write-Error "请指定备份目录"
        exit 1
    }
    
    if (!(Test-Path $BackupDir)) {
        Write-Error "备份目录不存在: $BackupDir"
        exit 1
    }
    
    Write-Warning "恢复数据..."
    
    try {
        # 恢复数据库
        if (Test-Path "$BackupDir\database.sql") {
            Get-Content "$BackupDir\database.sql" | docker-compose exec -T postgres psql -U postgres -d oei_ms
            Write-Success "数据库恢复完成"
        }
        
        # 恢复Redis数据
        if (Test-Path "$BackupDir\redis.rdb") {
            docker-compose stop redis
            docker cp "$BackupDir\redis.rdb" oei-redis:/data/dump.rdb
            docker-compose start redis
            Write-Success "Redis数据恢复完成"
        }
        
        # 恢复MQTT数据
        if (Test-Path "$BackupDir\mqtt_data") {
            docker cp "$BackupDir\mqtt_data\." oei-mosquitto:/mosquitto/data/
            docker-compose restart mosquitto
            Write-Success "MQTT数据恢复完成"
        }
    }
    catch {
        Write-Error "数据恢复失败: $_"
    }
}

# 开发模式
function Start-DevMode {
    Write-Info "启动开发模式..."
    
    try {
        docker-compose -f docker-compose.dev.yml up -d
        
        Write-Success "开发环境启动完成"
        Write-Info "访问地址:"
        Write-Host "  - 前端开发服务器: http://localhost:3000" -ForegroundColor White
        Write-Host "  - 后端API: http://localhost:8001" -ForegroundColor White
        Write-Host "  - pgAdmin: http://localhost:5050" -ForegroundColor White
        Write-Host "  - Redis Commander: http://localhost:8081" -ForegroundColor White
        Write-Host "  - MQTT Explorer: http://localhost:4000" -ForegroundColor White
    }
    catch {
        Write-Error "开发环境启动失败: $_"
    }
}

# 显示帮助信息
function Show-Help {
    Write-Host "OEI-MS 部署脚本 (PowerShell版本)" -ForegroundColor $Colors.Blue
    Write-Host ""
    Write-Host "用法: .\deploy.ps1 [命令] [参数]" -ForegroundColor White
    Write-Host ""
    Write-Host "命令:" -ForegroundColor White
    Write-Host "  init          初始化部署环境" -ForegroundColor White
    Write-Host "  build         构建Docker镜像" -ForegroundColor White
    Write-Host "  start         启动服务" -ForegroundColor White
    Write-Host "  stop          停止服务" -ForegroundColor White
    Write-Host "  restart       重启服务" -ForegroundColor White
    Write-Host "  status        查看服务状态" -ForegroundColor White
    Write-Host "  logs [服务名]  查看日志" -ForegroundColor White
    Write-Host "  backup        备份数据" -ForegroundColor White
    Write-Host "  restore <目录> 恢复数据" -ForegroundColor White
    Write-Host "  cleanup       清理Docker资源" -ForegroundColor White
    Write-Host "  dev           启动开发模式" -ForegroundColor White
    Write-Host "  help          显示帮助信息" -ForegroundColor White
    Write-Host ""
    Write-Host "示例:" -ForegroundColor White
    Write-Host "  .\deploy.ps1 init       # 初始化部署环境" -ForegroundColor White
    Write-Host "  .\deploy.ps1 start      # 启动所有服务" -ForegroundColor White
    Write-Host "  .\deploy.ps1 logs backend # 查看后端日志" -ForegroundColor White
    Write-Host "  .\deploy.ps1 backup     # 备份数据" -ForegroundColor White
}

# 初始化部署环境
function Initialize-Deployment {
    Write-Info "初始化部署环境..."
    
    Test-Dependencies
    New-RequiredDirectories
    New-EnvironmentFile
    
    Write-Success "部署环境初始化完成"
    Write-Info "接下来可以运行: .\deploy.ps1 build 然后 .\deploy.ps1 start"
}

# 主函数
function Main {
    switch ($Command.ToLower()) {
        "init" {
            Initialize-Deployment
        }
        "build" {
            Build-Images
        }
        "start" {
            Start-Services
        }
        "stop" {
            Stop-Services
        }
        "restart" {
            Restart-Services
        }
        "status" {
            Test-ServiceStatus
        }
        "logs" {
            Show-Logs -Service $Parameter
        }
        "backup" {
            Backup-Data
        }
        "restore" {
            Restore-Data -BackupDir $Parameter
        }
        "cleanup" {
            Remove-DockerResources
        }
        "dev" {
            Start-DevMode
        }
        { $_ -in @("help", "--help", "-h", "") } {
            Show-Help
        }
        default {
            Write-Error "未知命令: $Command"
            Show-Help
            exit 1
        }
    }
}

# 执行主函数
Main