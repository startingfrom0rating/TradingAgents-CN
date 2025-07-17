# 🚀 TradingAgents 数据源微服务

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **专业级金融数据源微服务，为TradingAgents提供高可用、高性能的数据基础设施**

## ✨ 核心特性

### 🌐 **微服务架构**
- **独立部署**: 可作为独立微服务运行
- **标准API**: RESTful API + OpenAPI文档
- **容器化**: Docker + Kubernetes就绪
- **高可用**: 多实例负载均衡

### 📊 **多数据源支持**
- **国内数据**: Tushare、AKShare、BaoStock
- **国际数据**: yfinance、FinnHub
- **智能路由**: 自动选择最优数据源
- **故障切换**: 数据源不可用时自动切换

### ⚡ **高性能缓存**
- **多层缓存**: Redis + 内存 + 文件
- **智能TTL**: 差异化缓存策略
- **预热机制**: 启动时预加载热数据
- **缓存穿透**: 防止缓存击穿

### 🔧 **灵活配置**
- **优先级配置**: 用户自定义数据源优先级
- **A/B测试**: 数据源效果对比
- **环境感知**: development/staging/production
- **热更新**: 运行时配置更新

### 🛡️ **高可用性**
- **健康检查**: 实时监控服务状态
- **优雅降级**: 微服务不可用时自动切换到本地
- **重试机制**: 指数退避重试
- **熔断保护**: 防止雪崩效应

### ⏰ **自动化运维**
- **定时任务**: 自动数据更新
- **监控告警**: 完整的监控体系
- **日志管理**: 结构化日志
- **性能统计**: 详细的性能指标

## 🚀 快速开始

### 1️⃣ 环境准备
```bash
# 系统要求
Python 3.10+
Docker 20.10+ (可选)
MongoDB 5.0+ (可选)
Redis 6.0+ (可选)
```

### 2️⃣ 项目安装
```bash
# 克隆项目
git clone https://github.com/hsliuping/TradingAgents-CN.git
cd TradingAgents-CN
git checkout feature/data-source-optimization

# 创建虚拟环境
python -m venv env
.\env\Scripts\activate  # Windows
source env/bin/activate  # Linux/macOS

# 安装依赖
pip install -r requirements.txt

# 配置环境
cp .env.example .env
# 编辑 .env 文件，配置API密钥
```

### 3️⃣ 启动方式

#### 🏠 本地模式 (推荐新手)
```bash
# 无需启动微服务，直接使用
python -c "
import asyncio
from tradingagents.adapters.data_adapter import get_stock_data
data = asyncio.run(get_stock_data('600036'))
print(f'✅ 获取到 {len(data)} 条数据')
"
```

#### 🐳 Docker模式 (推荐生产)
```bash
# 一键启动完整服务栈
python manage_data_service.py start --build

# 验证服务
curl http://localhost:8001/health
```

#### 🔧 开发模式
```bash
# 直接启动微服务
python run_data_service.py
```

### 4️⃣ API调用
```python
import asyncio
from tradingagents.adapters.data_adapter import get_stock_data, get_stock_fundamentals

async def main():
    # 获取历史数据
    hist_data = await get_stock_data("600036")
    print(f"📊 招商银行历史数据: {len(hist_data)} 条")
    
    # 获取基本面数据
    fund_data = await get_stock_fundamentals("600036")
    print(f"💰 PE比率: {fund_data.get('pe_ratio')}")

asyncio.run(main())
```

## 📚 文档导航

| 文档 | 说明 | 链接 |
|------|------|------|
| 🚀 **部署指南** | 完整的安装部署手册 | [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) |
| 📡 **API参考** | 详细的API接口文档 | [API_REFERENCE.md](docs/API_REFERENCE.md) |
| 🛠️ **使用示例** | 各种使用场景示例 | [examples/](examples/) |
| 🧪 **测试脚本** | 功能测试和验证 | [test_*.py](.) |

## 🏗️ 架构设计

### 系统架构图
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   用户应用      │    │   Web界面       │    │   第三方系统    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Nginx代理     │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │ 数据源微服务API │
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   数据适配器    │    │   缓存管理器    │    │   任务调度器    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │   Redis缓存     │              │
         │              └─────────────────┘              │
         │                                               │
┌─────────────────┐                            ┌─────────────────┐
│ 统一数据源管理  │                            │   MongoDB存储   │
└─────────────────┘                            └─────────────────┘
         │
┌─────────────────────────────────────────────────────────────────┐
│                    外部数据源                                   │
│  Tushare  │  AKShare  │  BaoStock  │  yfinance  │  FinnHub     │
└─────────────────────────────────────────────────────────────────┘
```

### 调用层次
```
用户代码
    ↓
便捷函数 (get_stock_data, get_stock_fundamentals)
    ↓
数据适配器 (DataAdapter)
    ↓
┌─────────────────┬─────────────────┐
│   微服务模式     │    本地模式      │
│                │                │
│ 数据服务客户端   │ 统一数据源管理器  │
│ (HTTP API)     │ (直接调用)      │
└─────────────────┴─────────────────┘
    ↓                    ↓
数据源微服务          本地数据源
(独立进程)           (AKShare/Tushare等)
```

## 🎯 使用场景

### 📈 **量化交易**
```python
# 获取多只股票数据进行策略回测
import asyncio
from tradingagents.adapters.data_adapter import DataAdapter, DataMode

async def backtest_strategy():
    adapter = DataAdapter(mode=DataMode.AUTO)
    await adapter.initialize()
    
    # 获取股票池
    stocks = await adapter.get_stocks(market="cn", limit=50)
    
    # 并发获取历史数据
    tasks = [adapter.get_historical_data(stock['code']) for stock in stocks]
    results = await asyncio.gather(*tasks)
    
    # 策略计算...
    await adapter.close()
```

### 📊 **数据分析**
```python
# 获取行业数据进行分析
async def industry_analysis():
    adapter = DataAdapter()
    await adapter.initialize()
    
    # 获取银行股
    banks = await adapter.get_stocks(industry="银行")
    
    # 获取基本面数据
    fundamentals = []
    for bank in banks:
        fund_data = await adapter.get_fundamental_data(bank['code'])
        if fund_data:
            fundamentals.append(fund_data)
    
    # 分析PE、PB分布...
    await adapter.close()
```

### 🤖 **自动化监控**
```python
# 实时监控股价变化
async def price_monitor():
    adapter = DataAdapter()
    await adapter.initialize()
    
    watch_list = ["600036", "000001", "000002"]
    
    while True:
        for code in watch_list:
            realtime = await adapter.get_realtime_data(code)
            if realtime and realtime['change_percent'] > 5:
                print(f"🚨 {code} 涨幅超过5%: {realtime['change_percent']:.2f}%")
        
        await asyncio.sleep(60)  # 每分钟检查一次
```

## 🔧 管理工具

### 服务管理
```bash
# 启动服务
python manage_data_service.py start

# 查看状态
python manage_data_service.py status

# 查看日志
python manage_data_service.py logs --follow

# 扩缩容
python manage_data_service.py scale --service data-service --replicas 3

# 测试API
python manage_data_service.py test
```

### 健康监控
```bash
# 服务健康检查
curl http://localhost:8001/health

# 调度器状态
curl http://localhost:8001/api/v1/status/scheduler

# 数据源状态
curl http://localhost:8001/api/v1/status/sources
```

### 配置管理
```python
# 更新数据源优先级
from tradingagents.clients.data_service_client import DataServiceClient

async def update_config():
    async with DataServiceClient() as client:
        sources = [
            {
                "source_name": "tushare",
                "priority": 1,
                "enabled": True,
                "weight": 1.0
            }
        ]
        await client.update_priority_config("cn", "historical", sources)
```

## 🧪 测试验证

### 运行测试
```bash
# 基础功能测试
python test_data_source_simple.py

# 微服务集成测试
python test_microservice_integration.py

# 定时任务测试
python test_scheduled_tasks.py

# 使用示例
python examples/microservice_usage.py
```

### 性能测试
```bash
# API压力测试
ab -n 1000 -c 10 http://localhost:8001/health

# 并发测试
python -c "
import asyncio
from tradingagents.adapters.data_adapter import get_stock_data

async def test():
    tasks = [get_stock_data('600036') for _ in range(10)]
    results = await asyncio.gather(*tasks)
    print(f'并发获取成功: {len([r for r in results if r])} / {len(tasks)}')

asyncio.run(test())
"
```

## 📊 监控指标

### 服务指标
- **响应时间**: API接口响应时间
- **成功率**: 请求成功率
- **并发数**: 同时处理的请求数
- **错误率**: 错误请求比例

### 数据源指标
- **可用性**: 各数据源可用状态
- **响应时间**: 数据源平均响应时间
- **成功率**: 数据获取成功率
- **切换次数**: 数据源切换频率

### 缓存指标
- **命中率**: 缓存命中率
- **内存使用**: 缓存内存占用
- **过期清理**: 缓存清理频率
- **穿透率**: 缓存穿透比例

## 🤝 贡献指南

### 开发环境
```bash
# 克隆开发分支
git clone https://github.com/hsliuping/TradingAgents-CN.git
cd TradingAgents-CN
git checkout feature/data-source-optimization

# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
python -m pytest tests/

# 代码格式化
black tradingagents/
isort tradingagents/
```

### 提交规范
- **feat**: 新功能
- **fix**: 修复bug
- **docs**: 文档更新
- **style**: 代码格式
- **refactor**: 重构
- **test**: 测试相关
- **chore**: 构建过程或辅助工具的变动

### Pull Request
1. Fork项目
2. 创建功能分支: `git checkout -b feature/amazing-feature`
3. 提交更改: `git commit -m 'feat: add amazing feature'`
4. 推送分支: `git push origin feature/amazing-feature`
5. 创建Pull Request

## 📄 许可证

本项目采用 [MIT License](LICENSE) 许可证。

## 🙏 致谢

感谢以下开源项目和数据提供商：

- **FastAPI**: 现代化的Python Web框架
- **Tushare**: 专业的金融数据接口
- **AKShare**: 开源的金融数据接口
- **MongoDB**: 文档数据库
- **Redis**: 内存数据库
- **Docker**: 容器化平台

## 📞 支持

- **GitHub Issues**: [提交问题](https://github.com/hsliuping/TradingAgents-CN/issues)
- **讨论区**: [参与讨论](https://github.com/hsliuping/TradingAgents-CN/discussions)
- **文档**: [在线文档](https://www.tradingagents.cn/)

---

<div align="center">

**🚀 TradingAgents 数据源微服务 - 为您的金融应用提供强大的数据基础设施！**

[![Star](https://img.shields.io/github/stars/hsliuping/TradingAgents-CN?style=social)](https://github.com/hsliuping/TradingAgents-CN)
[![Fork](https://img.shields.io/github/forks/hsliuping/TradingAgents-CN?style=social)](https://github.com/hsliuping/TradingAgents-CN)
[![Watch](https://img.shields.io/github/watchers/hsliuping/TradingAgents-CN?style=social)](https://github.com/hsliuping/TradingAgents-CN)

</div>
