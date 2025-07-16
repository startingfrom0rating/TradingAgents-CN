# 数据源优化计划

**分支**: `feature/data-source-optimization`  
**创建日期**: 2025年7月16日  
**目标**: 全面优化数据获取性能、稳定性和用户体验

## 🎯 优化目标

### 1. 定时数据更新系统 ✨ **核心新功能**
- **历史数据定时更新**: 每日自动更新股票历史价格数据
- **基本面数据定时更新**: 定期更新财务报表、公司信息等
- **增量更新策略**: 只更新变化的数据，提升效率
- **任务调度管理**: 灵活的定时任务配置和监控

### 2. 独立数据服务架构 🏗️ **架构升级**
- **数据服务分离**: 为后续独立部署数据服务做准备
- **API标准化**: 统一的数据服务API接口规范
- **微服务就绪**: 支持数据服务独立扩展和部署
- **服务发现**: 支持多数据服务实例的负载均衡

### 3. 数据源优先级配置 ⚙️ **用户自定义**
- **可视化配置**: Web界面配置数据源优先级
- **动态调整**: 运行时动态调整数据源优先级
- **场景化配置**: 不同数据类型的差异化优先级设置
- **A/B测试**: 支持数据源效果对比测试

### 4. 性能优化
- **响应速度提升**: 减少数据获取延迟，提升用户体验
- **并发处理**: 支持多股票并行数据获取
- **智能缓存**: 优化缓存策略，减少重复请求
- **资源利用**: 降低内存和CPU使用率

### 5. 稳定性增强
- **容错机制**: 增强API失败时的重试和降级策略
- **连接池管理**: 优化HTTP连接池，避免连接超时
- **限流保护**: 防止API调用频率过高被限制
- **异常处理**: 完善错误处理和用户友好提示

### 6. 数据质量
- **数据验证**: 增强数据完整性和准确性检查
- **格式统一**: 统一不同数据源的数据格式
- **实时性保证**: 确保数据的时效性
- **缺失数据处理**: 智能填补和标记缺失数据

## 📊 当前数据源现状分析

### A股数据源
| 数据源 | 用途 | 优势 | 问题 | 优化方向 |
|--------|------|------|------|----------|
| **BaoStock** | 历史数据 | 免费、稳定 | 速度较慢 | 并发优化、缓存策略 |
| **AKShare** | 实时数据 | 数据丰富 | 偶尔不稳定 | 容错机制、备用源 |
| **Tushare** | 专业数据 | 数据质量高 | 需要积分 | 智能调用、成本控制 |

### 港股数据源
| 数据源 | 用途 | 优势 | 问题 | 优化方向 |
|--------|------|------|------|----------|
| **AKShare** | 主要数据源 | 覆盖全面 | API限制 | 限流控制、缓存优化 |
| **Yahoo Finance** | 备用数据源 | 国际化 | 网络延迟 | 连接优化、本地缓存 |

### 美股数据源
| 数据源 | 用途 | 优势 | 问题 | 优化方向 |
|--------|------|------|------|----------|
| **FinnHub** | 基本面数据 | 专业性强 | API配额限制 | 配额管理、数据复用 |
| **Yahoo Finance** | 价格数据 | 免费可靠 | 功能有限 | 数据补充、格式优化 |

## 🔧 具体优化方案

### 1. 定时数据更新系统
```python
class ScheduledDataUpdater:
    """定时数据更新器"""

    def __init__(self):
        self.scheduler = APScheduler()
        self.mongodb = MongoDBManager()
        self.data_sources = DataSourceManager()
        self.logger = get_logger(__name__)

    def setup_scheduled_tasks(self):
        """设置定时任务"""
        # 每日历史数据更新 (交易日收盘后)
        self.scheduler.add_job(
            func=self.update_historical_data,
            trigger='cron',
            hour=18, minute=0,  # 每天18:00
            id='daily_historical_update'
        )

        # 每周基本面数据更新
        self.scheduler.add_job(
            func=self.update_fundamental_data,
            trigger='cron',
            day_of_week='sun', hour=2, minute=0,  # 每周日2:00
            id='weekly_fundamental_update'
        )

        # 每月公司信息更新
        self.scheduler.add_job(
            func=self.update_company_info,
            trigger='cron',
            day=1, hour=3, minute=0,  # 每月1号3:00
            id='monthly_company_update'
        )

    async def update_historical_data(self):
        """更新历史数据"""
        stock_list = await self.mongodb.get_active_stocks()
        for stock in stock_list:
            try:
                # 获取最新数据日期
                last_date = await self.mongodb.get_last_data_date(stock['code'])

                # 增量更新
                new_data = await self.data_sources.fetch_historical_data(
                    stock['code'], start_date=last_date
                )

                # 保存到MongoDB
                await self.mongodb.save_historical_data(stock['code'], new_data)

                self.logger.info(f"Updated historical data for {stock['code']}")

            except Exception as e:
                self.logger.error(f"Failed to update {stock['code']}: {e}")
```

### 2. 独立数据服务架构
```python
class DataServiceAPI:
    """独立数据服务API"""

    def __init__(self):
        self.app = FastAPI(title="TradingAgents Data Service")
        self.mongodb = MongoDBManager()
        self.cache = RedisCache()
        self.setup_routes()

    def setup_routes(self):
        """设置API路由"""

        @self.app.get("/api/v1/stocks/{stock_code}/historical")
        async def get_historical_data(
            stock_code: str,
            start_date: Optional[str] = None,
            end_date: Optional[str] = None,
            fields: Optional[List[str]] = None
        ):
            """获取历史数据"""
            cache_key = f"historical:{stock_code}:{start_date}:{end_date}"

            # 尝试从缓存获取
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                return cached_data

            # 从MongoDB获取
            data = await self.mongodb.get_historical_data(
                stock_code, start_date, end_date, fields
            )

            # 缓存结果
            await self.cache.set(cache_key, data, ttl=3600)

            return data

        @self.app.get("/api/v1/stocks/{stock_code}/fundamentals")
        async def get_fundamental_data(stock_code: str):
            """获取基本面数据"""
            return await self.mongodb.get_fundamental_data(stock_code)

        @self.app.post("/api/v1/data/refresh")
        async def trigger_data_refresh(request: DataRefreshRequest):
            """触发数据刷新"""
            task_id = await self.trigger_background_refresh(request)
            return {"task_id": task_id, "status": "started"}

class DataServiceClient:
    """数据服务客户端"""

    def __init__(self, service_url: str):
        self.service_url = service_url
        self.session = aiohttp.ClientSession()

    async def get_historical_data(self, stock_code: str, **kwargs):
        """获取历史数据"""
        url = f"{self.service_url}/api/v1/stocks/{stock_code}/historical"
        async with self.session.get(url, params=kwargs) as response:
            return await response.json()
```

### 3. 数据源优先级配置系统
```python
class DataSourcePriorityManager:
    """数据源优先级管理器"""

    def __init__(self):
        self.mongodb = MongoDBManager()
        self.config_cache = {}
        self.load_priority_config()

    async def load_priority_config(self):
        """加载优先级配置"""
        config = await self.mongodb.get_data_source_config()
        self.config_cache = config or self.get_default_config()

    def get_default_config(self):
        """默认优先级配置"""
        return {
            "cn_stocks": {
                "historical": ["baostock", "akshare", "tushare"],
                "realtime": ["akshare", "tushare", "baostock"],
                "fundamental": ["tushare", "akshare", "baostock"]
            },
            "hk_stocks": {
                "historical": ["akshare", "yahoo"],
                "realtime": ["akshare", "yahoo"],
                "fundamental": ["akshare", "yahoo"]
            },
            "us_stocks": {
                "historical": ["yahoo", "finnhub"],
                "realtime": ["yahoo", "finnhub"],
                "fundamental": ["finnhub", "yahoo"]
            }
        }

    async def update_priority(self, market: str, data_type: str, priorities: List[str]):
        """更新优先级配置"""
        if market not in self.config_cache:
            self.config_cache[market] = {}

        self.config_cache[market][data_type] = priorities

        # 保存到数据库
        await self.mongodb.save_data_source_config(self.config_cache)

        # 通知其他服务更新配置
        await self.broadcast_config_update()

    def get_priority_list(self, market: str, data_type: str) -> List[str]:
        """获取优先级列表"""
        return self.config_cache.get(market, {}).get(data_type, [])

class DataSourceConfigAPI:
    """数据源配置API"""

    def __init__(self):
        self.priority_manager = DataSourcePriorityManager()

    async def get_config(self):
        """获取当前配置"""
        return self.priority_manager.config_cache

    async def update_config(self, config_update: dict):
        """更新配置"""
        for market, market_config in config_update.items():
            for data_type, priorities in market_config.items():
                await self.priority_manager.update_priority(
                    market, data_type, priorities
                )
        return {"status": "success"}
```

### 4. 智能数据路由系统
```python
class SmartDataRouter:
    """智能数据路由器"""
    
    def __init__(self):
        self.data_sources = {
            'cn': ['baostock', 'akshare', 'tushare'],
            'hk': ['akshare', 'yahoo'],
            'us': ['finnhub', 'yahoo']
        }
        self.health_monitor = DataSourceHealthMonitor()
        self.load_balancer = LoadBalancer()
    
    def get_optimal_source(self, market, data_type):
        """获取最优数据源"""
        available_sources = self.health_monitor.get_healthy_sources(market)
        return self.load_balancer.select_source(available_sources, data_type)
```

### 2. 并发数据获取
```python
class ConcurrentDataFetcher:
    """并发数据获取器"""
    
    async def fetch_multiple_stocks(self, stock_codes, data_types):
        """并发获取多只股票数据"""
        tasks = []
        for code in stock_codes:
            for data_type in data_types:
                task = self.fetch_single_data(code, data_type)
                tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return self.process_results(results)
```

### 3. 智能缓存策略
```python
class IntelligentCache:
    """智能缓存系统"""
    
    def __init__(self):
        self.redis_cache = RedisCache()
        self.memory_cache = MemoryCache()
        self.file_cache = FileCache()
    
    def get_cache_strategy(self, data_type, market):
        """根据数据类型和市场选择缓存策略"""
        if data_type == 'realtime':
            return CacheStrategy(ttl=60, storage='memory')
        elif data_type == 'historical':
            return CacheStrategy(ttl=3600*24, storage='redis')
        else:
            return CacheStrategy(ttl=3600, storage='file')
```

### 4. 健康监控系统
```python
class DataSourceHealthMonitor:
    """数据源健康监控"""
    
    def __init__(self):
        self.health_status = {}
        self.response_times = {}
        self.error_rates = {}
    
    async def monitor_sources(self):
        """监控数据源健康状态"""
        for source in self.data_sources:
            health = await self.check_source_health(source)
            self.update_health_status(source, health)
```

## 📈 优化实施计划

### 阶段1: 定时数据更新系统 (2-3天) ✨ **优先级最高**
- [ ] 设计MongoDB数据存储结构
- [ ] 实现ScheduledDataUpdater定时任务系统
- [ ] 创建历史数据增量更新逻辑
- [ ] 实现基本面数据定时更新
- [ ] 添加任务监控和失败重试机制
- [ ] 创建数据更新状态API

### 阶段2: 数据源优先级配置 (2天) ⚙️ **用户体验关键**
- [ ] 实现DataSourcePriorityManager
- [ ] 创建Web界面配置页面
- [ ] 实现动态配置更新机制
- [ ] 添加配置验证和回滚功能
- [ ] 实现A/B测试框架
- [ ] 创建配置导入导出功能

### 阶段3: 独立数据服务架构 (3-4天) 🏗️ **架构升级**
- [ ] 设计数据服务API规范
- [ ] 实现DataServiceAPI (FastAPI)
- [ ] 创建DataServiceClient客户端
- [ ] 实现服务发现和负载均衡
- [ ] 添加API认证和权限控制
- [ ] 创建数据服务监控面板

### 阶段4: 基础架构优化 (2天)
- [ ] 优化智能数据路由系统
- [ ] 实现数据源健康监控
- [ ] 建立统一的数据接口规范
- [ ] 添加详细的性能监控日志

### 阶段5: 并发和缓存优化 (2-3天)
- [ ] 实现异步并发数据获取
- [ ] 优化缓存策略和存储层次
- [ ] 添加智能预加载机制
- [ ] 实现数据压缩和序列化优化

### 阶段6: 容错和稳定性 (2天)
- [ ] 增强重试机制和指数退避
- [ ] 实现熔断器模式
- [ ] 添加限流和配额管理
- [ ] 完善异常处理和用户提示

### 阶段7: 数据质量保证 (1-2天)
- [ ] 实现数据验证和清洗
- [ ] 添加数据完整性检查
- [ ] 统一数据格式和标准
- [ ] 实现缺失数据智能填补

### 阶段8: 测试和部署 (2天)
- [ ] 性能基准测试
- [ ] 压力测试和稳定性测试
- [ ] 用户体验测试
- [ ] 文档更新和部署
- [ ] 生产环境迁移方案

## 🎯 预期效果

### 性能提升
- **数据获取速度**: 提升50%以上
- **并发处理能力**: 支持10+股票同时分析
- **缓存命中率**: 达到80%以上
- **资源使用**: 降低30%内存和CPU使用

### 稳定性改善
- **API成功率**: 提升到99%以上
- **错误恢复时间**: 减少到秒级
- **用户体验**: 消除数据获取卡顿
- **系统可用性**: 达到99.9%

### 用户体验
- **响应速度**: 数据获取延迟减少60%
- **错误提示**: 友好的错误信息和建议
- **进度反馈**: 实时显示数据获取进度
- **智能重试**: 自动处理临时性错误

## 📊 监控指标

### 性能指标
- 数据获取响应时间
- 并发请求处理能力
- 缓存命中率和效率
- 内存和CPU使用率

### 稳定性指标
- API调用成功率
- 错误率和错误类型分布
- 重试成功率
- 系统可用性时间

### 用户体验指标
- 用户等待时间
- 分析完成率
- 错误反馈质量
- 用户满意度

## 🔄 持续优化

### 监控和反馈
- 实时性能监控仪表板
- 用户反馈收集机制
- 自动化性能报告
- 定期优化评估

### 技术演进
- 新数据源集成评估
- 技术栈升级规划
- 算法优化研究
- 行业最佳实践跟踪

---

**负责人**: 开发团队  
**预计完成时间**: 7-10天  
**优先级**: 高  
**依赖**: v0.1.9稳定版本
