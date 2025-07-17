#!/usr/bin/env python3
"""
数据适配器
统一数据访问接口，支持本地和微服务两种模式
"""

import os
import asyncio
from typing import List, Dict, Optional, Any, Union
from enum import Enum

from ..utils.logging_manager import get_logger
from ..clients.data_service_client import get_data_service_client
from ..dataflows.unified_data_source_manager import unified_data_source_manager

logger = get_logger(__name__)

class DataMode(Enum):
    """数据访问模式"""
    LOCAL = "local"          # 本地模式，直接调用数据源
    MICROSERVICE = "microservice"  # 微服务模式，通过API调用
    AUTO = "auto"           # 自动模式，优先微服务，降级到本地

class DataAdapter:
    """统一数据适配器"""
    
    def __init__(self, mode: DataMode = DataMode.AUTO):
        self.mode = mode
        self.client = None
        self.local_manager = unified_data_source_manager
        self._service_available = None
    
    async def initialize(self):
        """初始化适配器"""
        if self.mode in [DataMode.MICROSERVICE, DataMode.AUTO]:
            self.client = get_data_service_client()
            await self.client.initialize()
            
            # 检查微服务可用性
            if self.mode == DataMode.AUTO:
                await self._check_service_availability()
        
        logger.info(f"DataAdapter initialized in {self.mode.value} mode")
    
    async def _check_service_availability(self) -> bool:
        """检查微服务可用性"""
        try:
            health = await self.client.health_check()
            self._service_available = health.get('status') == 'healthy'
            
            if self._service_available:
                logger.info("Data microservice is available")
            else:
                logger.warning("Data microservice is not healthy, will use local mode")
            
            return self._service_available
        except Exception as e:
            logger.warning(f"Data microservice is not available: {e}, will use local mode")
            self._service_available = False
            return False
    
    def _should_use_microservice(self) -> bool:
        """判断是否应该使用微服务"""
        if self.mode == DataMode.LOCAL:
            return False
        elif self.mode == DataMode.MICROSERVICE:
            return True
        else:  # AUTO mode
            return self._service_available if self._service_available is not None else False
    
    async def get_stocks(self, market: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """获取股票列表"""
        if self._should_use_microservice():
            try:
                return await self.client.get_stocks(market, limit, offset)
            except Exception as e:
                logger.error(f"Microservice call failed: {e}")
                if self.mode == DataMode.AUTO:
                    logger.info("Falling back to local mode")
                    self._service_available = False
                else:
                    raise
        
        # 本地模式或降级
        try:
            # 这里需要实现本地获取股票列表的逻辑
            # 暂时返回模拟数据
            stocks = [
                {"code": "600036", "name": "招商银行", "market": "cn", "industry": "银行"},
                {"code": "000001", "name": "平安银行", "market": "cn", "industry": "银行"},
                {"code": "000002", "name": "万科A", "market": "cn", "industry": "房地产"}
            ]
            
            if market:
                stocks = [s for s in stocks if s.get('market') == market]
            
            return stocks[offset:offset+limit]
        except Exception as e:
            logger.error(f"Local mode failed: {e}")
            return []
    
    async def get_historical_data(
        self, 
        stock_code: str, 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """获取历史数据"""
        if self._should_use_microservice():
            try:
                return await self.client.get_historical_data(stock_code, start_date, end_date, fields)
            except Exception as e:
                logger.error(f"Microservice call failed: {e}")
                if self.mode == DataMode.AUTO:
                    logger.info("Falling back to local mode")
                    self._service_available = False
                else:
                    raise
        
        # 本地模式或降级
        try:
            return await self.local_manager.fetch_historical_data(
                stock_code, 
                market="cn",  # 默认A股
                start_date=start_date,
                end_date=end_date
            )
        except Exception as e:
            logger.error(f"Local mode failed: {e}")
            return []
    
    async def get_fundamental_data(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """获取基本面数据"""
        if self._should_use_microservice():
            try:
                return await self.client.get_fundamental_data(stock_code)
            except Exception as e:
                logger.error(f"Microservice call failed: {e}")
                if self.mode == DataMode.AUTO:
                    logger.info("Falling back to local mode")
                    self._service_available = False
                else:
                    raise
        
        # 本地模式或降级
        try:
            return await self.local_manager.fetch_fundamental_data(stock_code, market="cn")
        except Exception as e:
            logger.error(f"Local mode failed: {e}")
            return None
    
    async def get_realtime_data(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """获取实时数据"""
        if self._should_use_microservice():
            try:
                return await self.client.get_realtime_data(stock_code)
            except Exception as e:
                logger.error(f"Microservice call failed: {e}")
                if self.mode == DataMode.AUTO:
                    logger.info("Falling back to local mode")
                    self._service_available = False
                else:
                    raise
        
        # 本地模式或降级
        try:
            return await self.local_manager.fetch_realtime_data(stock_code, market="cn")
        except Exception as e:
            logger.error(f"Local mode failed: {e}")
            return None
    
    async def get_company_info(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """获取公司信息"""
        if self._should_use_microservice():
            try:
                # 微服务暂时没有专门的公司信息接口，使用基本面数据
                return await self.client.get_fundamental_data(stock_code)
            except Exception as e:
                logger.error(f"Microservice call failed: {e}")
                if self.mode == DataMode.AUTO:
                    logger.info("Falling back to local mode")
                    self._service_available = False
                else:
                    raise
        
        # 本地模式或降级
        try:
            return await self.local_manager.fetch_company_info(stock_code, market="cn")
        except Exception as e:
            logger.error(f"Local mode failed: {e}")
            return None
    
    async def trigger_data_refresh(
        self, 
        update_type: str, 
        stock_codes: Optional[List[str]] = None,
        force: bool = False
    ) -> bool:
        """触发数据刷新"""
        if self._should_use_microservice():
            try:
                return await self.client.trigger_data_refresh(update_type, stock_codes, force)
            except Exception as e:
                logger.error(f"Microservice call failed: {e}")
                if self.mode == DataMode.AUTO:
                    logger.info("Falling back to local mode")
                    self._service_available = False
                else:
                    raise
        
        # 本地模式或降级
        try:
            # 这里需要实现本地数据刷新逻辑
            logger.info(f"Local data refresh triggered: {update_type}")
            return True
        except Exception as e:
            logger.error(f"Local mode failed: {e}")
            return False
    
    async def get_priority_config(self) -> Dict[str, Any]:
        """获取优先级配置"""
        if self._should_use_microservice():
            try:
                return await self.client.get_priority_config()
            except Exception as e:
                logger.error(f"Microservice call failed: {e}")
                if self.mode == DataMode.AUTO:
                    logger.info("Falling back to local mode")
                    self._service_available = False
                else:
                    raise
        
        # 本地模式或降级
        try:
            # 这里需要实现本地优先级配置获取逻辑
            return {}
        except Exception as e:
            logger.error(f"Local mode failed: {e}")
            return {}
    
    async def update_priority_config(
        self, 
        market: str, 
        data_type: str, 
        sources: List[Dict[str, Any]]
    ) -> bool:
        """更新优先级配置"""
        if self._should_use_microservice():
            try:
                return await self.client.update_priority_config(market, data_type, sources)
            except Exception as e:
                logger.error(f"Microservice call failed: {e}")
                if self.mode == DataMode.AUTO:
                    logger.info("Falling back to local mode")
                    self._service_available = False
                else:
                    raise
        
        # 本地模式或降级
        try:
            # 这里需要实现本地优先级配置更新逻辑
            logger.info(f"Local priority config updated: {market}:{data_type}")
            return True
        except Exception as e:
            logger.error(f"Local mode failed: {e}")
            return False
    
    async def get_scheduler_status(self) -> Dict[str, Any]:
        """获取调度器状态"""
        if self._should_use_microservice():
            try:
                return await self.client.get_scheduler_status()
            except Exception as e:
                logger.error(f"Microservice call failed: {e}")
                if self.mode == DataMode.AUTO:
                    logger.info("Falling back to local mode")
                    self._service_available = False
                else:
                    raise
        
        # 本地模式或降级
        try:
            # 这里需要实现本地调度器状态获取逻辑
            return {"status": "local_mode", "message": "Running in local mode"}
        except Exception as e:
            logger.error(f"Local mode failed: {e}")
            return {}
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        if self._should_use_microservice():
            try:
                return await self.client.health_check()
            except Exception as e:
                logger.error(f"Microservice health check failed: {e}")
                if self.mode == DataMode.AUTO:
                    self._service_available = False
                return {"status": "unhealthy", "error": str(e)}
        
        # 本地模式
        return {"status": "healthy", "mode": "local"}
    
    async def close(self):
        """关闭适配器"""
        if self.client:
            await self.client.close()
        logger.info("DataAdapter closed")

# 全局适配器实例
_global_adapter: Optional[DataAdapter] = None

def get_data_adapter(mode: DataMode = DataMode.AUTO) -> DataAdapter:
    """获取全局数据适配器实例"""
    global _global_adapter
    if _global_adapter is None:
        _global_adapter = DataAdapter(mode)
    return _global_adapter

async def close_data_adapter():
    """关闭全局数据适配器"""
    global _global_adapter
    if _global_adapter:
        await _global_adapter.close()
        _global_adapter = None

# 便捷函数
async def get_stock_data(stock_code: str, **kwargs) -> List[Dict[str, Any]]:
    """便捷函数：获取股票历史数据"""
    adapter = get_data_adapter()
    if not adapter.client and not adapter._service_available:
        await adapter.initialize()
    
    return await adapter.get_historical_data(stock_code, **kwargs)

async def get_stock_fundamentals(stock_code: str) -> Optional[Dict[str, Any]]:
    """便捷函数：获取股票基本面数据"""
    adapter = get_data_adapter()
    if not adapter.client and not adapter._service_available:
        await adapter.initialize()
    
    return await adapter.get_fundamental_data(stock_code)

async def get_stock_realtime(stock_code: str) -> Optional[Dict[str, Any]]:
    """便捷函数：获取股票实时数据"""
    adapter = get_data_adapter()
    if not adapter.client and not adapter._service_available:
        await adapter.initialize()
    
    return await adapter.get_realtime_data(stock_code)
