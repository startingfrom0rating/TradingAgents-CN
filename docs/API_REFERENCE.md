# TradingAgents 数据源微服务 API 参考手册

## 📋 目录

- [API概述](#api概述)
- [认证授权](#认证授权)
- [基础接口](#基础接口)
- [数据接口](#数据接口)
- [管理接口](#管理接口)
- [Python SDK](#python-sdk)
- [错误处理](#错误处理)
- [限流说明](#限流说明)

## 🌐 API概述

### 基础信息
- **Base URL**: `http://localhost:8001`
- **协议**: HTTP/HTTPS
- **数据格式**: JSON
- **字符编码**: UTF-8
- **API版本**: v1

### 响应格式
```json
{
  "success": true,
  "data": {},
  "message": "操作成功",
  "timestamp": "2025-07-17T10:00:00Z",
  "request_id": "req_123456789"
}
```

### 状态码
- `200`: 成功
- `400`: 请求参数错误
- `401`: 未授权
- `404`: 资源不存在
- `429`: 请求过于频繁
- `500`: 服务器内部错误

## 🔐 认证授权

### API密钥认证 (可选)
```bash
# 请求头添加API密钥
curl -H "X-API-Key: your-api-key" \
     http://localhost:8001/api/v1/stocks
```

### 无认证模式
```bash
# 开发环境默认无需认证
curl http://localhost:8001/api/v1/stocks
```

## 🏠 基础接口

### 健康检查
检查服务运行状态和组件健康情况。

**请求**
```http
GET /health
```

**响应**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-17T10:00:00.123456",
  "components": {
    "mongodb": "healthy",
    "cache": "healthy", 
    "scheduler": "running"
  }
}
```

**示例**
```bash
curl http://localhost:8001/health
```

### 服务信息
获取服务版本和配置信息。

**请求**
```http
GET /
```

**响应**
```json
{
  "name": "TradingAgents Data Service",
  "version": "1.0.0",
  "description": "金融数据源微服务",
  "docs_url": "/docs",
  "health_url": "/health"
}
```

### API文档
- **Swagger UI**: `http://localhost:8001/docs`
- **ReDoc**: `http://localhost:8001/redoc`
- **OpenAPI JSON**: `http://localhost:8001/openapi.json`

## 📊 数据接口

### 股票列表
获取股票基础信息列表。

**请求**
```http
GET /api/v1/stocks
```

**参数**
| 参数 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| market | string | 否 | 市场代码 (cn/us/hk) | 全部 |
| limit | integer | 否 | 返回数量限制 | 100 |
| offset | integer | 否 | 偏移量 | 0 |
| industry | string | 否 | 行业筛选 | 全部 |

**响应**
```json
{
  "success": true,
  "data": [
    {
      "code": "600036",
      "name": "招商银行",
      "market": "cn",
      "industry": "银行",
      "sector": "金融",
      "status": "active"
    }
  ],
  "total": 4500,
  "limit": 100,
  "offset": 0
}
```

**示例**
```bash
# 获取A股银行股
curl "http://localhost:8001/api/v1/stocks?market=cn&industry=银行&limit=10"

# 获取港股列表
curl "http://localhost:8001/api/v1/stocks?market=hk&limit=20"
```

### 历史数据
获取股票历史价格数据。

**请求**
```http
GET /api/v1/stocks/{stock_code}/historical
```

**参数**
| 参数 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| stock_code | string | 是 | 股票代码 | - |
| start_date | string | 否 | 开始日期 (YYYY-MM-DD) | 30天前 |
| end_date | string | 否 | 结束日期 (YYYY-MM-DD) | 今天 |
| fields | string | 否 | 字段列表 (逗号分隔) | 全部 |

**响应**
```json
{
  "success": true,
  "data": [
    {
      "date": "2025-07-17",
      "open": 45.20,
      "high": 46.50,
      "low": 44.80,
      "close": 46.10,
      "volume": 12500000,
      "amount": 575000000.0,
      "change": 0.90,
      "change_percent": 1.99
    }
  ],
  "stock_code": "600036",
  "stock_name": "招商银行",
  "count": 30
}
```

**示例**
```bash
# 获取招商银行最近30天数据
curl "http://localhost:8001/api/v1/stocks/600036/historical"

# 获取指定时间段数据
curl "http://localhost:8001/api/v1/stocks/600036/historical?start_date=2025-01-01&end_date=2025-07-17"

# 只获取收盘价和成交量
curl "http://localhost:8001/api/v1/stocks/600036/historical?fields=date,close,volume"
```

### 基本面数据
获取股票基本面财务数据。

**请求**
```http
GET /api/v1/stocks/{stock_code}/fundamental
```

**响应**
```json
{
  "success": true,
  "data": {
    "stock_code": "600036",
    "stock_name": "招商银行",
    "pe_ratio": 12.5,
    "pb_ratio": 1.8,
    "market_cap": 1500000000000,
    "total_shares": 25000000000,
    "revenue": 300000000000,
    "net_profit": 120000000000,
    "roe": 15.2,
    "debt_ratio": 0.85,
    "updated_at": "2025-07-17T10:00:00Z"
  }
}
```

**示例**
```bash
# 获取招商银行基本面数据
curl "http://localhost:8001/api/v1/stocks/600036/fundamental"

# 获取平安银行基本面数据
curl "http://localhost:8001/api/v1/stocks/000001/fundamental"
```

### 实时数据
获取股票实时价格和交易数据。

**请求**
```http
GET /api/v1/stocks/{stock_code}/realtime
```

**响应**
```json
{
  "success": true,
  "data": {
    "stock_code": "600036",
    "stock_name": "招商银行",
    "price": 46.10,
    "change": 0.90,
    "change_percent": 1.99,
    "volume": 8500000,
    "amount": 391000000.0,
    "high": 46.50,
    "low": 44.80,
    "open": 45.20,
    "prev_close": 45.20,
    "timestamp": "2025-07-17T15:00:00Z",
    "market_status": "trading"
  }
}
```

**示例**
```bash
# 获取招商银行实时数据
curl "http://localhost:8001/api/v1/stocks/600036/realtime"
```

### 公司信息
获取上市公司基本信息。

**请求**
```http
GET /api/v1/stocks/{stock_code}/company
```

**响应**
```json
{
  "success": true,
  "data": {
    "stock_code": "600036",
    "stock_name": "招商银行",
    "company_name": "招商银行股份有限公司",
    "industry": "银行",
    "sector": "金融",
    "description": "招商银行成立于1987年，是中国第一家完全由企业法人持股的股份制商业银行。",
    "website": "https://www.cmbchina.com",
    "employees": 120000,
    "founded_date": "1987-04-08",
    "listing_date": "2002-04-09",
    "registered_capital": 25000000000,
    "business_scope": "吸收公众存款；发放短期、中期和长期贷款..."
  }
}
```

**示例**
```bash
# 获取招商银行公司信息
curl "http://localhost:8001/api/v1/stocks/600036/company"
```

## ⚙️ 管理接口

### 数据刷新
手动触发数据更新。

**请求**
```http
POST /api/v1/data/refresh
```

**请求体**
```json
{
  "update_type": "historical",
  "stock_codes": ["600036", "000001"],
  "force": false
}
```

**参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| update_type | string | 是 | 更新类型: historical/fundamental/realtime/company |
| stock_codes | array | 否 | 股票代码列表，为空则更新全部 |
| force | boolean | 否 | 是否强制更新 |

**响应**
```json
{
  "success": true,
  "data": {
    "task_id": "refresh_123456",
    "update_type": "historical",
    "stock_count": 2,
    "estimated_time": "5分钟"
  },
  "message": "数据刷新任务已启动"
}
```

**示例**
```bash
# 刷新招商银行历史数据
curl -X POST "http://localhost:8001/api/v1/data/refresh" \
     -H "Content-Type: application/json" \
     -d '{"update_type": "historical", "stock_codes": ["600036"]}'

# 强制刷新所有基本面数据
curl -X POST "http://localhost:8001/api/v1/data/refresh" \
     -H "Content-Type: application/json" \
     -d '{"update_type": "fundamental", "force": true}'
```

### 优先级配置
获取和更新数据源优先级配置。

**获取配置**
```http
GET /api/v1/config/priority
```

**响应**
```json
{
  "success": true,
  "data": {
    "cn": {
      "historical": [
        {
          "source_name": "tushare",
          "priority": 1,
          "enabled": true,
          "weight": 1.0,
          "timeout_seconds": 30,
          "max_requests_per_minute": 100,
          "retry_count": 3
        }
      ]
    }
  }
}
```

**更新配置**
```http
POST /api/v1/config/priority
```

**请求体**
```json
{
  "market": "cn",
  "data_type": "historical",
  "sources": [
    {
      "source_name": "tushare",
      "priority": 1,
      "enabled": true,
      "weight": 1.0,
      "timeout_seconds": 30,
      "max_requests_per_minute": 100,
      "retry_count": 3
    }
  ]
}
```

**示例**
```bash
# 获取优先级配置
curl "http://localhost:8001/api/v1/config/priority"

# 更新A股历史数据优先级
curl -X POST "http://localhost:8001/api/v1/config/priority" \
     -H "Content-Type: application/json" \
     -d '{
       "market": "cn",
       "data_type": "historical", 
       "sources": [
         {
           "source_name": "tushare",
           "priority": 1,
           "enabled": true,
           "weight": 1.0,
           "timeout_seconds": 30,
           "max_requests_per_minute": 100,
           "retry_count": 3
         }
       ]
     }'
```

### 调度器状态
获取定时任务调度器状态。

**请求**
```http
GET /api/v1/status/scheduler
```

**响应**
```json
{
  "success": true,
  "data": {
    "is_running": true,
    "stats": {
      "total_updates": 150,
      "successful_updates": 145,
      "failed_updates": 5
    },
    "next_runs": {
      "daily_historical_update": "2025-07-17T18:00:00+08:00",
      "weekly_fundamental_update": "2025-07-20T02:00:00+08:00",
      "monthly_company_update": "2025-08-01T03:00:00+08:00",
      "realtime_cache_refresh": "2025-07-17T15:05:00+08:00"
    }
  }
}
```

**示例**
```bash
# 获取调度器状态
curl "http://localhost:8001/api/v1/status/scheduler"
```

### 数据源状态
获取各数据源健康状态和统计信息。

**请求**
```http
GET /api/v1/status/sources
```

**响应**
```json
{
  "success": true,
  "data": {
    "tushare": {
      "status": "healthy",
      "success_rate": 0.95,
      "avg_response_time": 1.2,
      "total_requests": 1000,
      "successful_requests": 950,
      "last_success": "2025-07-17T14:30:00Z",
      "last_failure": "2025-07-17T10:15:00Z"
    },
    "akshare": {
      "status": "healthy", 
      "success_rate": 0.98,
      "avg_response_time": 0.8,
      "total_requests": 800,
      "successful_requests": 784,
      "last_success": "2025-07-17T14:35:00Z",
      "last_failure": null
    }
  }
}
```

**示例**
```bash
# 获取数据源状态
curl "http://localhost:8001/api/v1/status/sources"
```

## 🐍 Python SDK

### 安装和导入
```python
# 项目已包含SDK，直接导入
from tradingagents.adapters.data_adapter import (
    get_stock_data, 
    get_stock_fundamentals,
    get_stock_realtime,
    DataAdapter,
    DataMode
)
from tradingagents.clients.data_service_client import DataServiceClient
```

### 便捷函数使用
```python
import asyncio

async def quick_start():
    # 获取历史数据
    hist_data = await get_stock_data("600036")
    print(f"历史数据: {len(hist_data)} 条")
    
    # 获取基本面数据
    fund_data = await get_stock_fundamentals("600036")
    print(f"PE比率: {fund_data.get('pe_ratio')}")
    
    # 获取实时数据
    realtime_data = await get_stock_realtime("600036")
    print(f"当前价格: {realtime_data.get('price')}")

asyncio.run(quick_start())
```

### 数据适配器使用
```python
import asyncio
from tradingagents.adapters.data_adapter import DataAdapter, DataMode

async def adapter_example():
    # 创建适配器
    adapter = DataAdapter(mode=DataMode.AUTO)
    await adapter.initialize()
    
    try:
        # 获取股票列表
        stocks = await adapter.get_stocks(market="cn", limit=10)
        
        # 批量获取数据
        tasks = []
        for stock in stocks[:5]:
            task = adapter.get_historical_data(stock['code'])
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        for stock, data in zip(stocks[:5], results):
            print(f"{stock['name']}: {len(data)} 条数据")
            
    finally:
        await adapter.close()

asyncio.run(adapter_example())
```

### 微服务客户端使用
```python
import asyncio
from tradingagents.clients.data_service_client import DataServiceClient

async def client_example():
    async with DataServiceClient() as client:
        # 健康检查
        health = await client.health_check()
        print(f"服务状态: {health['status']}")
        
        # 获取数据
        stocks = await client.get_stocks(limit=5)
        hist_data = await client.get_historical_data("600036")
        
        # 管理操作
        success = await client.trigger_data_refresh("historical", ["600036"])
        config = await client.get_priority_config()
        
        print(f"数据刷新: {'成功' if success else '失败'}")
        print(f"配置项: {len(config)} 个市场")

asyncio.run(client_example())
```

### 错误处理
```python
import asyncio
from tradingagents.adapters.data_adapter import DataAdapter, DataMode

async def error_handling_example():
    adapter = DataAdapter(mode=DataMode.AUTO)
    await adapter.initialize()
    
    try:
        # 尝试获取数据
        data = await adapter.get_historical_data("600036")
        
        if data:
            print(f"成功获取 {len(data)} 条数据")
        else:
            print("未获取到数据")
            
    except Exception as e:
        print(f"发生错误: {e}")
        
        # 检查服务状态
        health = await adapter.health_check()
        print(f"服务状态: {health.get('status')}")
        
    finally:
        await adapter.close()

asyncio.run(error_handling_example())
```

## ❌ 错误处理

### 错误响应格式
```json
{
  "success": false,
  "error": {
    "code": "INVALID_STOCK_CODE",
    "message": "股票代码无效",
    "details": "股票代码 'INVALID' 不存在"
  },
  "timestamp": "2025-07-17T10:00:00Z",
  "request_id": "req_123456789"
}
```

### 常见错误码
| 错误码 | HTTP状态码 | 说明 |
|--------|------------|------|
| INVALID_STOCK_CODE | 400 | 股票代码无效 |
| INVALID_DATE_RANGE | 400 | 日期范围无效 |
| DATA_NOT_FOUND | 404 | 数据不存在 |
| RATE_LIMIT_EXCEEDED | 429 | 请求频率超限 |
| DATA_SOURCE_ERROR | 500 | 数据源错误 |
| SERVICE_UNAVAILABLE | 503 | 服务不可用 |

### 错误处理示例
```python
import aiohttp
import asyncio

async def handle_errors():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get("http://localhost:8001/api/v1/stocks/INVALID/historical") as response:
                if response.status == 200:
                    data = await response.json()
                    print("成功:", data)
                else:
                    error = await response.json()
                    print(f"错误 {response.status}: {error['error']['message']}")
                    
        except aiohttp.ClientError as e:
            print(f"网络错误: {e}")

asyncio.run(handle_errors())
```

## 🚦 限流说明

### 限流规则
- **默认限制**: 每分钟1000次请求
- **IP限制**: 每IP每分钟100次请求
- **数据刷新**: 每小时10次
- **批量操作**: 每次最多100只股票

### 限流响应
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "请求频率超限",
    "details": "每分钟最多100次请求，请稍后重试"
  },
  "retry_after": 60
}
```

### 避免限流
```python
import asyncio
import aiohttp

async def rate_limit_friendly():
    """友好的限流处理"""
    semaphore = asyncio.Semaphore(10)  # 限制并发数
    
    async def fetch_with_limit(session, url):
        async with semaphore:
            async with session.get(url) as response:
                if response.status == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    await asyncio.sleep(retry_after)
                    return await fetch_with_limit(session, url)
                return await response.json()
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for code in ["600036", "000001", "000002"]:
            url = f"http://localhost:8001/api/v1/stocks/{code}/historical"
            task = fetch_with_limit(session, url)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return results

asyncio.run(rate_limit_friendly())
```

---

**TradingAgents 数据源微服务API为您提供完整、稳定、高效的金融数据访问能力！** 📊
