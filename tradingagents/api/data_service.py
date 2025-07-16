#!/usr/bin/env python3
"""
独立数据服务API
为后续独立部署数据服务做准备，提供标准化的数据访问接口
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from fastapi import FastAPI, HTTPException, Depends, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from ..utils.logging_manager import get_logger
from ..dataflows.mongodb_storage import MongoDBDataStorage
from ..dataflows.cache_manager import CacheManager
from ..dataflows.data_source_manager import DataSourceManager
from ..dataflows.scheduled_updater import scheduled_updater
from ..dataflows.priority_manager import priority_manager

logger = get_logger(__name__)

# Pydantic模型定义
class StockInfo(BaseModel):
    """股票信息模型"""
    code: str
    name: str
    market: str
    industry: Optional[str] = None
    sector: Optional[str] = None

class HistoricalDataRequest(BaseModel):
    """历史数据请求模型"""
    stock_code: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    fields: Optional[List[str]] = None

class DataRefreshRequest(BaseModel):
    """数据刷新请求模型"""
    update_type: str = Field(..., description="更新类型: historical, fundamental, company")
    stock_codes: Optional[List[str]] = Field(None, description="指定股票代码，为空则更新所有")
    force: bool = Field(False, description="是否强制更新")

class PriorityConfigRequest(BaseModel):
    """优先级配置请求模型"""
    market: str
    data_type: str
    sources: List[Dict[str, Any]]

class DataServiceResponse(BaseModel):
    """数据服务响应模型"""
    success: bool
    data: Optional[Any] = None
    message: str = ""
    timestamp: datetime = Field(default_factory=datetime.now)

class DataServiceAPI:
    """独立数据服务API"""
    
    def __init__(self):
        self.app = FastAPI(
            title="TradingAgents Data Service",
            description="独立数据服务API，提供股票数据访问和管理功能",
            version="1.0.0"
        )
        
        # 添加CORS中间件
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self.mongodb = MongoDBDataStorage()
        self.cache = CacheManager()
        self.data_sources = DataSourceManager()
        
        self.setup_routes()
    
    async def initialize(self):
        """初始化数据服务"""
        try:
            await self.mongodb.initialize()
            await self.cache.initialize()
            await scheduled_updater.initialize()
            await priority_manager.initialize()
            
            # 启动定时任务
            await scheduled_updater.start()
            
            logger.info("DataServiceAPI initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize DataServiceAPI: {e}")
            raise
    
    def setup_routes(self):
        """设置API路由"""
        
        @self.app.get("/", response_model=DataServiceResponse)
        async def root():
            """根路径"""
            return DataServiceResponse(
                success=True,
                message="TradingAgents Data Service is running",
                data={"version": "1.0.0", "status": "healthy"}
            )
        
        @self.app.get("/health")
        async def health_check():
            """健康检查"""
            try:
                # 检查各个组件状态
                mongodb_status = await self.mongodb.health_check()
                cache_status = await self.cache.health_check()
                scheduler_status = scheduled_updater.get_update_status()
                
                return {
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "components": {
                        "mongodb": mongodb_status,
                        "cache": cache_status,
                        "scheduler": scheduler_status
                    }
                }
            except Exception as e:
                raise HTTPException(status_code=503, detail=f"Service unhealthy: {e}")
        
        @self.app.get("/api/v1/stocks", response_model=DataServiceResponse)
        async def get_stocks(
            market: Optional[str] = Query(None, description="市场类型: cn, hk, us"),
            limit: int = Query(100, description="返回数量限制"),
            offset: int = Query(0, description="偏移量")
        ):
            """获取股票列表"""
            try:
                stocks = await self.mongodb.get_stocks(market, limit, offset)
                return DataServiceResponse(
                    success=True,
                    data=stocks,
                    message=f"Retrieved {len(stocks)} stocks"
                )
            except Exception as e:
                logger.error(f"Failed to get stocks: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/stocks/{stock_code}/historical", response_model=DataServiceResponse)
        async def get_historical_data(
            stock_code: str = Path(..., description="股票代码"),
            start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
            end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
            fields: Optional[str] = Query(None, description="字段列表，逗号分隔")
        ):
            """获取历史数据"""
            try:
                # 构建缓存键
                cache_key = f"historical:{stock_code}:{start_date}:{end_date}:{fields}"
                
                # 尝试从缓存获取
                cached_data = await self.cache.get(cache_key)
                if cached_data:
                    return DataServiceResponse(
                        success=True,
                        data=cached_data,
                        message="Data from cache"
                    )
                
                # 从数据库获取
                field_list = fields.split(',') if fields else None
                data = await self.mongodb.get_historical_data(
                    stock_code, start_date, end_date, field_list
                )
                
                # 缓存结果
                if data:
                    await self.cache.set(cache_key, data, ttl=3600)  # 1小时缓存
                
                return DataServiceResponse(
                    success=True,
                    data=data,
                    message=f"Retrieved {len(data) if data else 0} records"
                )
                
            except Exception as e:
                logger.error(f"Failed to get historical data for {stock_code}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/stocks/{stock_code}/fundamental", response_model=DataServiceResponse)
        async def get_fundamental_data(stock_code: str = Path(..., description="股票代码")):
            """获取基本面数据"""
            try:
                cache_key = f"fundamental:{stock_code}"
                
                # 尝试从缓存获取
                cached_data = await self.cache.get(cache_key)
                if cached_data:
                    return DataServiceResponse(
                        success=True,
                        data=cached_data,
                        message="Data from cache"
                    )
                
                # 从数据库获取
                data = await self.mongodb.get_fundamental_data(stock_code)
                
                # 缓存结果
                if data:
                    await self.cache.set(cache_key, data, ttl=7200)  # 2小时缓存
                
                return DataServiceResponse(
                    success=True,
                    data=data,
                    message="Retrieved fundamental data"
                )
                
            except Exception as e:
                logger.error(f"Failed to get fundamental data for {stock_code}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/stocks/{stock_code}/realtime", response_model=DataServiceResponse)
        async def get_realtime_data(stock_code: str = Path(..., description="股票代码")):
            """获取实时数据"""
            try:
                cache_key = f"realtime:{stock_code}"
                
                # 尝试从缓存获取
                cached_data = await self.cache.get(cache_key)
                if cached_data:
                    return DataServiceResponse(
                        success=True,
                        data=cached_data,
                        message="Data from cache"
                    )
                
                # 实时获取数据
                data = await self.data_sources.fetch_realtime_data(stock_code)
                
                # 缓存结果
                if data:
                    await self.cache.set(cache_key, data, ttl=60)  # 1分钟缓存
                
                return DataServiceResponse(
                    success=True,
                    data=data,
                    message="Retrieved realtime data"
                )
                
            except Exception as e:
                logger.error(f"Failed to get realtime data for {stock_code}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/v1/data/refresh", response_model=DataServiceResponse)
        async def trigger_data_refresh(request: DataRefreshRequest):
            """触发数据刷新"""
            try:
                # 异步执行数据更新
                task_id = f"refresh_{request.update_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                asyncio.create_task(
                    scheduled_updater.trigger_manual_update(
                        request.update_type, 
                        request.stock_codes
                    )
                )
                
                return DataServiceResponse(
                    success=True,
                    data={"task_id": task_id},
                    message=f"Data refresh task started: {request.update_type}"
                )
                
            except Exception as e:
                logger.error(f"Failed to trigger data refresh: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/config/priority", response_model=DataServiceResponse)
        async def get_priority_config():
            """获取数据源优先级配置"""
            try:
                config = await priority_manager.get_all_configs()
                return DataServiceResponse(
                    success=True,
                    data=config,
                    message="Retrieved priority configuration"
                )
            except Exception as e:
                logger.error(f"Failed to get priority config: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/v1/config/priority", response_model=DataServiceResponse)
        async def update_priority_config(request: PriorityConfigRequest):
            """更新数据源优先级配置"""
            try:
                await priority_manager.update_priority_config(
                    request.market,
                    request.data_type,
                    request.sources
                )
                
                return DataServiceResponse(
                    success=True,
                    message=f"Updated priority config for {request.market}:{request.data_type}"
                )
                
            except Exception as e:
                logger.error(f"Failed to update priority config: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/status/scheduler", response_model=DataServiceResponse)
        async def get_scheduler_status():
            """获取定时任务状态"""
            try:
                status = scheduled_updater.get_update_status()
                return DataServiceResponse(
                    success=True,
                    data=status,
                    message="Retrieved scheduler status"
                )
            except Exception as e:
                logger.error(f"Failed to get scheduler status: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    async def shutdown(self):
        """关闭数据服务"""
        try:
            await scheduled_updater.stop()
            await self.mongodb.close()
            await self.cache.close()
            logger.info("DataServiceAPI shutdown completed")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

# 全局实例
data_service_api = DataServiceAPI()

async def create_app():
    """创建FastAPI应用"""
    await data_service_api.initialize()
    return data_service_api.app

def run_data_service(host: str = "0.0.0.0", port: int = 8001):
    """运行数据服务"""
    uvicorn.run(
        "tradingagents.api.data_service:create_app",
        host=host,
        port=port,
        factory=True,
        reload=False
    )

if __name__ == "__main__":
    run_data_service()
