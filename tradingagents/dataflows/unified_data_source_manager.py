#!/usr/bin/env python3
"""
统一数据源管理器
统一管理所有数据源，支持智能路由和负载均衡
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

from ..utils.logging_manager import get_logger
from .priority_manager import priority_manager, DataSourceConfig
from ..tools.unified_tools import get_stock_data, get_stock_fundamentals, get_company_info

logger = get_logger(__name__)

@dataclass
class DataSourceResult:
    """数据源结果"""
    success: bool
    data: Optional[Any] = None
    source: Optional[str] = None
    error: Optional[str] = None
    response_time: float = 0.0

class UnifiedDataSourceManager:
    """统一数据源管理器"""
    
    def __init__(self):
        self.source_health = {}
        self.source_stats = {}
        
        # 数据源映射
        self.source_mapping = {
            "baostock": "baostock",
            "akshare": "akshare", 
            "tushare": "tushare",
            "yahoo": "yahoo",
            "finnhub": "finnhub"
        }
    
    async def fetch_historical_data(
        self, 
        stock_code: str, 
        market: str = "cn",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """获取历史数据"""
        try:
            # 获取数据源优先级列表
            sources = await priority_manager.get_priority_list(market, "historical")
            
            for source_config in sources:
                if not source_config.enabled:
                    continue
                
                try:
                    result = await self._fetch_from_source(
                        source_config.source_name,
                        "historical",
                        stock_code=stock_code,
                        market=market,
                        start_date=start_date,
                        end_date=end_date
                    )
                    
                    if result.success and result.data:
                        self._update_source_stats(source_config.source_name, True, result.response_time)
                        return result.data
                    
                except Exception as e:
                    logger.warning(f"Source {source_config.source_name} failed: {e}")
                    self._update_source_stats(source_config.source_name, False, 0)
                    continue
            
            logger.error(f"All sources failed for historical data: {stock_code}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to fetch historical data for {stock_code}: {e}")
            return None
    
    async def fetch_fundamental_data(
        self, 
        stock_code: str, 
        market: str = "cn"
    ) -> Optional[Dict[str, Any]]:
        """获取基本面数据"""
        try:
            sources = await priority_manager.get_priority_list(market, "fundamental")
            
            for source_config in sources:
                if not source_config.enabled:
                    continue
                
                try:
                    result = await self._fetch_from_source(
                        source_config.source_name,
                        "fundamental",
                        stock_code=stock_code,
                        market=market
                    )
                    
                    if result.success and result.data:
                        self._update_source_stats(source_config.source_name, True, result.response_time)
                        return result.data
                    
                except Exception as e:
                    logger.warning(f"Source {source_config.source_name} failed: {e}")
                    self._update_source_stats(source_config.source_name, False, 0)
                    continue
            
            logger.error(f"All sources failed for fundamental data: {stock_code}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to fetch fundamental data for {stock_code}: {e}")
            return None
    
    async def fetch_realtime_data(
        self, 
        stock_code: str, 
        market: str = "cn"
    ) -> Optional[Dict[str, Any]]:
        """获取实时数据"""
        try:
            sources = await priority_manager.get_priority_list(market, "realtime")
            
            for source_config in sources:
                if not source_config.enabled:
                    continue
                
                try:
                    result = await self._fetch_from_source(
                        source_config.source_name,
                        "realtime",
                        stock_code=stock_code,
                        market=market
                    )
                    
                    if result.success and result.data:
                        self._update_source_stats(source_config.source_name, True, result.response_time)
                        return result.data
                    
                except Exception as e:
                    logger.warning(f"Source {source_config.source_name} failed: {e}")
                    self._update_source_stats(source_config.source_name, False, 0)
                    continue
            
            logger.error(f"All sources failed for realtime data: {stock_code}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to fetch realtime data for {stock_code}: {e}")
            return None
    
    async def fetch_company_info(
        self, 
        stock_code: str, 
        market: str = "cn"
    ) -> Optional[Dict[str, Any]]:
        """获取公司信息"""
        try:
            sources = await priority_manager.get_priority_list(market, "company_info")
            
            # 如果没有专门的公司信息配置，使用基本面数据源
            if not sources:
                sources = await priority_manager.get_priority_list(market, "fundamental")
            
            for source_config in sources:
                if not source_config.enabled:
                    continue
                
                try:
                    result = await self._fetch_from_source(
                        source_config.source_name,
                        "company_info",
                        stock_code=stock_code,
                        market=market
                    )
                    
                    if result.success and result.data:
                        self._update_source_stats(source_config.source_name, True, result.response_time)
                        return result.data
                    
                except Exception as e:
                    logger.warning(f"Source {source_config.source_name} failed: {e}")
                    self._update_source_stats(source_config.source_name, False, 0)
                    continue
            
            logger.error(f"All sources failed for company info: {stock_code}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to fetch company info for {stock_code}: {e}")
            return None
    
    async def _fetch_from_source(
        self, 
        source_name: str, 
        data_type: str, 
        **kwargs
    ) -> DataSourceResult:
        """从指定数据源获取数据"""
        start_time = datetime.now()
        
        try:
            stock_code = kwargs.get("stock_code")
            market = kwargs.get("market", "cn")
            
            # 根据数据类型调用相应的工具
            if data_type == "historical":
                # 调用统一工具获取历史数据
                data = await get_stock_data(
                    stock_code, 
                    market=market,
                    start_date=kwargs.get("start_date"),
                    end_date=kwargs.get("end_date")
                )
            elif data_type == "fundamental":
                # 调用统一工具获取基本面数据
                data = await get_stock_fundamentals(stock_code, market=market)
            elif data_type == "realtime":
                # 调用统一工具获取实时数据
                data = await get_stock_data(stock_code, market=market, period="1d")
            elif data_type == "company_info":
                # 调用统一工具获取公司信息
                data = await get_company_info(stock_code, market=market)
            else:
                raise ValueError(f"Unknown data type: {data_type}")
            
            response_time = (datetime.now() - start_time).total_seconds()
            
            if data:
                return DataSourceResult(
                    success=True,
                    data=data,
                    source=source_name,
                    response_time=response_time
                )
            else:
                return DataSourceResult(
                    success=False,
                    source=source_name,
                    error="No data returned",
                    response_time=response_time
                )
                
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds()
            return DataSourceResult(
                success=False,
                source=source_name,
                error=str(e),
                response_time=response_time
            )
    
    def _update_source_stats(self, source_name: str, success: bool, response_time: float):
        """更新数据源统计信息"""
        if source_name not in self.source_stats:
            self.source_stats[source_name] = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "avg_response_time": 0.0,
                "last_success": None,
                "last_failure": None
            }
        
        stats = self.source_stats[source_name]
        stats["total_requests"] += 1
        
        if success:
            stats["successful_requests"] += 1
            stats["last_success"] = datetime.now()
        else:
            stats["failed_requests"] += 1
            stats["last_failure"] = datetime.now()
        
        # 更新平均响应时间
        if response_time > 0:
            current_avg = stats["avg_response_time"]
            total_requests = stats["total_requests"]
            stats["avg_response_time"] = (current_avg * (total_requests - 1) + response_time) / total_requests
    
    def get_source_stats(self) -> Dict[str, Any]:
        """获取数据源统计信息"""
        return self.source_stats.copy()
    
    def get_source_health(self) -> Dict[str, Any]:
        """获取数据源健康状态"""
        health_status = {}
        
        for source_name, stats in self.source_stats.items():
            total = stats["total_requests"]
            success = stats["successful_requests"]
            
            if total > 0:
                success_rate = success / total
                health_status[source_name] = {
                    "status": "healthy" if success_rate > 0.8 else "degraded" if success_rate > 0.5 else "unhealthy",
                    "success_rate": success_rate,
                    "avg_response_time": stats["avg_response_time"],
                    "last_success": stats["last_success"].isoformat() if stats["last_success"] else None,
                    "last_failure": stats["last_failure"].isoformat() if stats["last_failure"] else None
                }
            else:
                health_status[source_name] = {
                    "status": "unknown",
                    "success_rate": 0.0,
                    "avg_response_time": 0.0,
                    "last_success": None,
                    "last_failure": None
                }
        
        return health_status

# 全局实例
unified_data_source_manager = UnifiedDataSourceManager()
