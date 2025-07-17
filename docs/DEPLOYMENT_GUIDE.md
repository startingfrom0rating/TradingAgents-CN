# TradingAgents 数据源微服务部署指南

## 📋 目录

- [系统要求](#系统要求)
- [快速开始](#快速开始)
- [详细安装](#详细安装)
- [部署方式](#部署方式)
- [配置管理](#配置管理)
- [API调用](#api调用)
- [监控运维](#监控运维)
- [故障排除](#故障排除)

## 🔧 系统要求

### 基础环境
- **Python**: 3.10+ (推荐 3.11)
- **操作系统**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **内存**: 最低 2GB，推荐 4GB+
- **磁盘**: 最低 5GB 可用空间

### 可选依赖
- **Docker**: 20.10+ (容器化部署)
- **Docker Compose**: 2.0+ (一键部署)
- **Kubernetes**: 1.20+ (集群部署)
- **MongoDB**: 5.0+ (数据持久化)
- **Redis**: 6.0+ (缓存加速)

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/hsliuping/TradingAgents-CN.git
cd TradingAgents-CN
git checkout feature/data-source-optimization
```

### 2. 环境配置
```bash
# 创建虚拟环境
python -m venv env

# 激活虚拟环境
# Windows
.\env\Scripts\activate
# Linux/macOS
source env/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置文件
```bash
# 复制配置模板
cp .env.example .env

# 编辑配置文件
# 配置API密钥、数据库连接等
```

### 4. 启动服务
```bash
# 方式1: 直接启动 (开发模式)
python run_data_service.py

# 方式2: Docker启动 (推荐)
python manage_data_service.py start --build

# 方式3: 本地模式 (无需微服务)
python -c "
import asyncio
from tradingagents.adapters.data_adapter import get_stock_data
print(asyncio.run(get_stock_data('600036')))
"
```

### 5. 验证安装
```bash
# 健康检查
curl http://localhost:8001/health

# 或使用PowerShell
Invoke-RestMethod -Uri "http://localhost:8001/health"

# 运行测试
python test_microservice_integration.py
```

## 📦 详细安装

### 步骤1: 环境准备

#### Python环境
```bash
# 检查Python版本
python --version  # 应该是 3.10+

# 如果版本不符合，安装新版本
# Windows: 从 python.org 下载安装
# Ubuntu: sudo apt install python3.11
# macOS: brew install python@3.11
```

#### Git配置
```bash
# 配置Git (如果尚未配置)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 步骤2: 项目下载
```bash
# 克隆项目
git clone https://github.com/hsliuping/TradingAgents-CN.git
cd TradingAgents-CN

# 切换到数据源优化分支
git checkout feature/data-source-optimization

# 查看项目结构
ls -la
```

### 步骤3: 依赖安装
```bash
# 创建虚拟环境
python -m venv env

# 激活虚拟环境
# Windows PowerShell
.\env\Scripts\Activate.ps1
# Windows CMD
.\env\Scripts\activate.bat
# Linux/macOS
source env/bin/activate

# 升级pip
python -m pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt

# 验证关键包安装
python -c "import fastapi, uvicorn, aiohttp, motor, aioredis; print('✅ 核心依赖安装成功')"
```

### 步骤4: 配置设置

#### 基础配置
```bash
# 复制配置模板
cp .env.example .env

# 编辑配置文件 (使用你喜欢的编辑器)
# Windows
notepad .env
# Linux/macOS
nano .env
# 或使用VS Code
code .env
```

#### 配置文件说明
```bash
# .env 文件配置项说明

# === 数据源API密钥 ===
TUSHARE_TOKEN=your_tushare_token_here          # Tushare专业版Token
FINNHUB_API_KEY=your_finnhub_key_here          # FinnHub API密钥
DASHSCOPE_API_KEY=your_dashscope_key_here      # 阿里云DashScope密钥

# === 数据库配置 ===
MONGODB_ENABLED=true                           # 是否启用MongoDB
MONGODB_HOST=localhost                         # MongoDB主机
MONGODB_PORT=27017                            # MongoDB端口
MONGODB_USERNAME=admin                         # MongoDB用户名
MONGODB_PASSWORD=tradingagents123             # MongoDB密码
MONGODB_DATABASE=tradingagents                # 数据库名

# === 缓存配置 ===
REDIS_ENABLED=true                            # 是否启用Redis
REDIS_HOST=localhost                          # Redis主机
REDIS_PORT=6379                              # Redis端口
REDIS_PASSWORD=tradingagents123              # Redis密码
REDIS_DB=0                                   # Redis数据库编号

# === 微服务配置 ===
DATA_SERVICE_URL=http://localhost:8001       # 数据服务URL
DATA_SERVICE_HOST=0.0.0.0                   # 服务监听地址
DATA_SERVICE_PORT=8001                       # 服务端口
DATA_SERVICE_WORKERS=2                       # 工作进程数

# === 环境配置 ===
TRADINGAGENTS_ENV=development                # 环境: development/staging/production
TRADINGAGENTS_LOG_LEVEL=INFO                # 日志级别
```

#### API密钥获取

**Tushare Token**:
1. 访问 [Tushare官网](https://tushare.pro/)
2. 注册账号并实名认证
3. 获取Token并配置到 `TUSHARE_TOKEN`

**FinnHub API Key**:
1. 访问 [FinnHub官网](https://finnhub.io/)
2. 注册免费账号
3. 获取API Key并配置到 `FINNHUB_API_KEY`

### 步骤5: 数据库安装 (可选)

#### MongoDB安装
```bash
# Ubuntu
sudo apt update
sudo apt install mongodb

# macOS
brew install mongodb-community

# Windows
# 从 https://www.mongodb.com/try/download/community 下载安装

# 启动MongoDB
sudo systemctl start mongodb  # Ubuntu
brew services start mongodb-community  # macOS
```

#### Redis安装
```bash
# Ubuntu
sudo apt install redis-server

# macOS
brew install redis

# Windows
# 从 https://github.com/microsoftarchive/redis/releases 下载

# 启动Redis
sudo systemctl start redis  # Ubuntu
brew services start redis  # macOS
```

## 🐳 部署方式

### 方式1: 开发模式 (推荐新手)

```bash
# 激活虚拟环境
.\env\Scripts\activate  # Windows
source env/bin/activate  # Linux/macOS

# 直接启动微服务
python run_data_service.py
```

**特点**:
- ✅ 简单快速，适合开发调试
- ✅ 实时代码更新
- ❌ 需要手动管理依赖服务
- ❌ 不适合生产环境

### 方式2: Docker Compose (推荐生产)

```bash
# 一键启动完整服务栈
python manage_data_service.py start --build

# 或直接使用docker-compose
docker-compose -f docker-compose.data-service.yml up -d --build
```

**特点**:
- ✅ 包含完整服务栈 (微服务+MongoDB+Redis+Nginx)
- ✅ 生产级配置
- ✅ 自动重启和健康检查
- ✅ 数据持久化

**服务组件**:
- `data-service`: 数据源微服务 (端口8001)
- `mongodb`: MongoDB数据库 (端口27017)
- `redis`: Redis缓存 (端口6379)
- `nginx`: 反向代理 (端口80)

### 方式3: Kubernetes (企业级)

```bash
# 部署到Kubernetes集群
kubectl apply -f k8s/data-service-deployment.yaml

# 检查部署状态
kubectl get pods -n tradingagents
kubectl get services -n tradingagents

# 端口转发访问
kubectl port-forward service/data-service 8001:8001 -n tradingagents
```

**特点**:
- ✅ 高可用性和自动扩缩容
- ✅ 滚动更新和回滚
- ✅ 服务发现和负载均衡
- ✅ 企业级监控和日志

### 方式4: 本地模式 (无微服务)

```bash
# 直接使用本地数据源，无需启动微服务
python -c "
import asyncio
from tradingagents.adapters.data_adapter import DataAdapter, DataMode

async def test():
    adapter = DataAdapter(mode=DataMode.LOCAL)
    await adapter.initialize()
    data = await adapter.get_historical_data('600036')
    print(f'获取到 {len(data)} 条数据')
    await adapter.close()

asyncio.run(test())
"
```

**特点**:
- ✅ 零配置，开箱即用
- ✅ 无需外部依赖
- ✅ 适合快速测试
- ❌ 功能有限，无持久化

## ⚙️ 配置管理

### 环境配置

#### 开发环境
```bash
# .env 配置
TRADINGAGENTS_ENV=development
DATA_SERVICE_URL=http://localhost:8001
MONGODB_ENABLED=false  # 可选
REDIS_ENABLED=false    # 可选
```

#### 测试环境
```bash
# .env 配置
TRADINGAGENTS_ENV=testing
DATA_SERVICE_URL=http://localhost:8001
MONGODB_ENABLED=true
REDIS_ENABLED=false    # 禁用缓存以确保测试准确性
```

#### 生产环境
```bash
# .env 配置
TRADINGAGENTS_ENV=production
DATA_SERVICE_URL=http://data-service:8001  # 容器内部地址
MONGODB_ENABLED=true
REDIS_ENABLED=true
DATA_SERVICE_WORKERS=4  # 增加工作进程
```

### 数据源配置

#### 优先级配置
```python
# 通过API配置数据源优先级
import asyncio
from tradingagents.clients.data_service_client import DataServiceClient

async def configure_priority():
    async with DataServiceClient() as client:
        # A股历史数据优先级
        sources = [
            {
                "source_name": "tushare",
                "priority": 1,
                "enabled": True,
                "weight": 1.0,
                "timeout_seconds": 30,
                "max_requests_per_minute": 100,
                "retry_count": 3
            },
            {
                "source_name": "akshare", 
                "priority": 2,
                "enabled": True,
                "weight": 0.8,
                "timeout_seconds": 20,
                "max_requests_per_minute": 200,
                "retry_count": 2
            }
        ]
        
        success = await client.update_priority_config("cn", "historical", sources)
        print(f"配置更新: {'成功' if success else '失败'}")

asyncio.run(configure_priority())
```

#### 缓存配置
```python
# 缓存TTL配置
cache_config = {
    'realtime': 60,      # 实时数据缓存1分钟
    'historical': 1800,  # 历史数据缓存30分钟
    'fundamental': 7200, # 基本面数据缓存2小时
    'company': 86400     # 公司信息缓存24小时
}
```

## 📡 API调用

### 基础调用

#### 使用便捷函数 (推荐)
```python
import asyncio
from tradingagents.adapters.data_adapter import (
    get_stock_data, 
    get_stock_fundamentals, 
    get_stock_realtime
)

async def basic_usage():
    # 获取历史数据
    hist_data = await get_stock_data("600036")
    print(f"历史数据: {len(hist_data)} 条")
    
    # 获取基本面数据
    fund_data = await get_stock_fundamentals("600036")
    print(f"PE比率: {fund_data.get('pe_ratio')}")
    
    # 获取实时数据
    realtime_data = await get_stock_realtime("600036")
    print(f"当前价格: {realtime_data.get('price')}")

# 运行示例
asyncio.run(basic_usage())
```

#### 使用数据适配器
```python
import asyncio
from tradingagents.adapters.data_adapter import DataAdapter, DataMode

async def adapter_usage():
    # 创建适配器 (自动模式)
    adapter = DataAdapter(mode=DataMode.AUTO)
    await adapter.initialize()
    
    try:
        # 获取股票列表
        stocks = await adapter.get_stocks(market="cn", limit=10)
        print(f"A股列表: {len(stocks)} 只")
        
        # 获取特定股票数据
        for stock in stocks[:3]:
            code = stock['code']
            name = stock['name']
            
            # 获取历史数据
            hist_data = await adapter.get_historical_data(code)
            print(f"{name}({code}): {len(hist_data)} 条历史数据")
            
    finally:
        await adapter.close()

asyncio.run(adapter_usage())
```

#### 直接使用微服务客户端
```python
import asyncio
from tradingagents.clients.data_service_client import DataServiceClient

async def client_usage():
    async with DataServiceClient() as client:
        # 健康检查
        health = await client.health_check()
        print(f"服务状态: {health['status']}")
        
        # 获取股票数据
        stocks = await client.get_stocks(limit=5)
        print(f"股票数量: {len(stocks)}")
        
        # 获取历史数据
        hist_data = await client.get_historical_data("600036")
        print(f"历史数据: {len(hist_data)} 条")
        
        # 触发数据刷新
        success = await client.trigger_data_refresh("historical", ["600036"])
        print(f"数据刷新: {'成功' if success else '失败'}")

asyncio.run(client_usage())
```

### 高级调用

#### 批量操作
```python
import asyncio
from tradingagents.adapters.data_adapter import DataAdapter, DataMode

async def batch_operations():
    adapter = DataAdapter(mode=DataMode.AUTO)
    await adapter.initialize()
    
    try:
        # 批量获取多只股票数据
        stock_codes = ["600036", "000001", "000002", "600519", "000858"]
        
        # 并发获取历史数据
        tasks = [adapter.get_historical_data(code) for code in stock_codes]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for code, result in zip(stock_codes, results):
            if isinstance(result, Exception):
                print(f"{code}: 获取失败 - {result}")
            else:
                print(f"{code}: 获取到 {len(result)} 条数据")
                
    finally:
        await adapter.close()

asyncio.run(batch_operations())
```

#### 错误处理
```python
import asyncio
from tradingagents.adapters.data_adapter import DataAdapter, DataMode

async def error_handling():
    adapter = DataAdapter(mode=DataMode.AUTO)
    await adapter.initialize()
    
    try:
        # 尝试获取不存在的股票数据
        data = await adapter.get_historical_data("INVALID_CODE")
        if data:
            print(f"获取到数据: {len(data)} 条")
        else:
            print("未获取到数据，可能是股票代码无效")
            
        # 检查服务健康状态
        health = await adapter.health_check()
        print(f"服务状态: {health['status']}")
        
        # 如果微服务不可用，会自动降级到本地模式
        if not adapter._service_available:
            print("微服务不可用，已自动降级到本地模式")
            
    except Exception as e:
        print(f"发生错误: {e}")
        
    finally:
        await adapter.close()

asyncio.run(error_handling())
```

### REST API调用

#### 使用curl
```bash
# 健康检查
curl http://localhost:8001/health

# 获取股票列表
curl "http://localhost:8001/api/v1/stocks?limit=5"

# 获取历史数据
curl "http://localhost:8001/api/v1/stocks/600036/historical"

# 获取基本面数据
curl "http://localhost:8001/api/v1/stocks/600036/fundamental"

# 触发数据刷新
curl -X POST "http://localhost:8001/api/v1/data/refresh" \
     -H "Content-Type: application/json" \
     -d '{"update_type": "historical", "stock_codes": ["600036"]}'
```

#### 使用Python requests
```python
import requests

# 基础配置
BASE_URL = "http://localhost:8001"

def test_api():
    # 健康检查
    response = requests.get(f"{BASE_URL}/health")
    print(f"健康状态: {response.json()}")
    
    # 获取股票列表
    response = requests.get(f"{BASE_URL}/api/v1/stocks", params={"limit": 5})
    stocks = response.json()
    print(f"股票数量: {len(stocks.get('data', []))}")
    
    # 获取历史数据
    response = requests.get(f"{BASE_URL}/api/v1/stocks/600036/historical")
    hist_data = response.json()
    print(f"历史数据: {len(hist_data.get('data', []))} 条")

test_api()
```

## 📊 监控运维

### 服务管理

#### 使用管理脚本
```bash
# 启动服务
python manage_data_service.py start

# 查看状态
python manage_data_service.py status

# 查看日志
python manage_data_service.py logs

# 实时跟踪日志
python manage_data_service.py logs --follow

# 重启服务
python manage_data_service.py restart

# 停止服务
python manage_data_service.py stop

# 扩缩容
python manage_data_service.py scale --service data-service --replicas 3

# 测试API
python manage_data_service.py test
```

#### Docker管理
```bash
# 查看容器状态
docker-compose -f docker-compose.data-service.yml ps

# 查看日志
docker-compose -f docker-compose.data-service.yml logs data-service

# 重启特定服务
docker-compose -f docker-compose.data-service.yml restart data-service

# 扩缩容
docker-compose -f docker-compose.data-service.yml up -d --scale data-service=3

# 停止所有服务
docker-compose -f docker-compose.data-service.yml down
```

### 健康监控

#### 健康检查端点
```bash
# 基础健康检查
curl http://localhost:8001/health

# 详细组件状态
curl http://localhost:8001/api/v1/status/scheduler

# 数据源健康状态
curl http://localhost:8001/api/v1/status/sources
```

#### 监控脚本
```python
import asyncio
import aiohttp
from datetime import datetime

async def monitor_service():
    """服务监控脚本"""
    url = "http://localhost:8001/health"
    
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        status = data.get('status', 'unknown')
                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        print(f"[{timestamp}] 服务状态: {status}")
                    else:
                        print(f"[{timestamp}] 服务异常: HTTP {response.status}")
                        
        except Exception as e:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] 连接失败: {e}")
        
        await asyncio.sleep(30)  # 每30秒检查一次

# 运行监控
asyncio.run(monitor_service())
```

### 性能监控

#### 系统资源监控
```bash
# CPU和内存使用
docker stats

# 磁盘使用
df -h

# 网络连接
netstat -tlnp | grep 8001
```

#### 应用性能监控
```python
import asyncio
import time
from tradingagents.clients.data_service_client import DataServiceClient

async def performance_test():
    """性能测试"""
    async with DataServiceClient() as client:
        # 测试响应时间
        start_time = time.time()
        
        tasks = []
        for i in range(10):  # 并发10个请求
            task = client.get_stocks(limit=10)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        duration = end_time - start_time
        
        success_count = sum(1 for r in results if not isinstance(r, Exception))
        
        print(f"性能测试结果:")
        print(f"  总请求数: {len(tasks)}")
        print(f"  成功请求: {success_count}")
        print(f"  总耗时: {duration:.2f}秒")
        print(f"  平均响应时间: {duration/len(tasks):.2f}秒")
        print(f"  QPS: {len(tasks)/duration:.2f}")

asyncio.run(performance_test())
```

## 🔧 故障排除

### 常见问题

#### 1. 服务启动失败
```bash
# 问题: 端口被占用
# 解决: 检查端口占用
netstat -tlnp | grep 8001
# 或更换端口
export DATA_SERVICE_PORT=8002
python run_data_service.py
```

#### 2. 数据库连接失败
```bash
# 问题: MongoDB连接失败
# 解决: 检查MongoDB状态
sudo systemctl status mongodb
# 或禁用MongoDB
export MONGODB_ENABLED=false
```

#### 3. 依赖包安装失败
```bash
# 问题: 网络问题导致安装失败
# 解决: 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

#### 4. API调用超时
```python
# 问题: 请求超时
# 解决: 增加超时时间
from tradingagents.clients.data_service_client import DataServiceClient

client = DataServiceClient(timeout=60)  # 增加到60秒
```

### 日志分析

#### 查看日志
```bash
# 应用日志
python manage_data_service.py logs

# 系统日志
journalctl -u tradingagents-data-service

# Docker日志
docker logs tradingagents-data-service
```

#### 日志级别配置
```bash
# 调试模式
export TRADINGAGENTS_LOG_LEVEL=DEBUG

# 生产模式
export TRADINGAGENTS_LOG_LEVEL=WARNING
```

### 性能优化

#### 1. 缓存优化
```python
# 启用Redis缓存
export REDIS_ENABLED=true

# 调整缓存TTL
cache_config = {
    'realtime': 30,      # 减少实时数据缓存时间
    'historical': 3600,  # 增加历史数据缓存时间
}
```

#### 2. 并发优化
```bash
# 增加工作进程
export DATA_SERVICE_WORKERS=4

# 调整超时时间
export DATA_SERVICE_TIMEOUT=60
```

#### 3. 数据库优化
```javascript
// MongoDB索引优化
db.historical_data.createIndex({"stock_code": 1, "date": -1})
db.stocks.createIndex({"market": 1, "industry": 1})
```

### 备份恢复

#### 数据备份
```bash
# MongoDB备份
mongodump --host localhost:27017 --db tradingagents --out backup/

# Redis备份
redis-cli --rdb backup/dump.rdb
```

#### 数据恢复
```bash
# MongoDB恢复
mongorestore --host localhost:27017 --db tradingagents backup/tradingagents/

# Redis恢复
redis-cli --rdb dump.rdb
```

## 📞 技术支持

### 获取帮助
- **GitHub Issues**: [提交问题](https://github.com/hsliuping/TradingAgents-CN/issues)
- **文档**: [在线文档](https://www.tradingagents.cn/)
- **社区**: [讨论区](https://github.com/hsliuping/TradingAgents-CN/discussions)

### 贡献代码
1. Fork项目
2. 创建功能分支
3. 提交代码
4. 创建Pull Request

## 📝 快速开始示例

### 5分钟上手指南

#### 1. 最简单的开始
```bash
# 1. 克隆项目
git clone https://github.com/hsliuping/TradingAgents-CN.git
cd TradingAgents-CN
git checkout feature/data-source-optimization

# 2. 安装依赖
python -m venv env
.\env\Scripts\activate  # Windows
pip install -r requirements.txt

# 3. 复制配置
cp .env.example .env

# 4. 测试本地模式 (无需启动微服务)
python -c "
import asyncio
from tradingagents.adapters.data_adapter import get_stock_data
data = asyncio.run(get_stock_data('600036'))
print(f'✅ 获取到招商银行 {len(data)} 条历史数据')
"
```

#### 2. 启动完整微服务
```bash
# 使用Docker Compose一键启动
python manage_data_service.py start --build

# 等待服务启动 (约30秒)
# 验证服务
curl http://localhost:8001/health
```

#### 3. 调用API
```python
# test_api.py
import asyncio
from tradingagents.adapters.data_adapter import get_stock_data, get_stock_fundamentals

async def main():
    # 获取招商银行历史数据
    hist_data = await get_stock_data("600036")
    print(f"📊 历史数据: {len(hist_data)} 条")

    # 获取基本面数据
    fund_data = await get_stock_fundamentals("600036")
    print(f"💰 PE比率: {fund_data.get('pe_ratio', 'N/A')}")

    print("🎉 API调用成功！")

if __name__ == "__main__":
    asyncio.run(main())
```

```bash
# 运行测试
python test_api.py
```

### 常用命令速查

```bash
# === 服务管理 ===
python manage_data_service.py start     # 启动服务
python manage_data_service.py stop      # 停止服务
python manage_data_service.py status    # 查看状态
python manage_data_service.py logs      # 查看日志
python manage_data_service.py test      # 测试API

# === 健康检查 ===
curl http://localhost:8001/health       # 服务健康检查
curl http://localhost:8001/docs         # API文档

# === 数据获取 ===
curl "http://localhost:8001/api/v1/stocks?limit=5"                    # 股票列表
curl "http://localhost:8001/api/v1/stocks/600036/historical"          # 历史数据
curl "http://localhost:8001/api/v1/stocks/600036/fundamental"         # 基本面数据

# === 测试脚本 ===
python test_microservice_integration.py  # 微服务集成测试
python test_scheduled_tasks.py          # 定时任务测试
python examples/microservice_usage.py   # 使用示例
```

---

**TradingAgents 数据源微服务为您提供专业、稳定、高效的金融数据服务！** 🚀
