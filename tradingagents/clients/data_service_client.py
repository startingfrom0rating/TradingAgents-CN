#!/usr/bin/env python3
"""
数据源微服务客户端
提供对数据源微服务的统一访问接口
"""

import os
import asyncio
import aiohttp
import json
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
import time

from ..utils.logging_manager import get_logger

logger = get_logger(__name__)

class DataServiceClient:
    """数据源微服务客户端"""
    
    def __init__(self, base_url: Optional[str] = None, timeout: int = 30):
        self.base_url = base_url or os.getenv('DATA_SERVICE_URL', 'http://localhost:8001')
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None
        
        # 重试配置
        self.max_retries = 3
        self.retry_delay = 1.0
        
        # 缓存配置
        self.enable_local_cache = True
        self.local_cache = {}
        self.cache_ttl = {
            'stocks': 3600,      # 1小时
            'historical': 1800,  # 30分钟
            'fundamental': 7200, # 2小时
            'realtime': 60,      # 1分钟
            'company': 86400     # 24小时
        }
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()
    
    async def initialize(self):
        """初始化客户端"""
        if not self.session:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
            logger.debug(f"DataServiceClient initialized with base_url: {self.base_url}")
    
    async def close(self):
        """关闭客户端"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.debug("DataServiceClient closed")
    
    def _get_cache_key(self, endpoint: str, params: Dict = None) -> str:
        """生成缓存键"""
        if params:
            param_str = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
            return f"{endpoint}?{param_str}"
        return endpoint
    
    def _is_cache_valid(self, cache_entry: Dict, ttl: int) -> bool:
        """检查缓存是否有效"""
        if not cache_entry:
            return False
        
        cache_time = cache_entry.get('timestamp', 0)
        return (time.time() - cache_time) < ttl
    
    def _set_cache(self, key: str, data: Any, data_type: str = 'default'):
        """设置本地缓存"""
        if not self.enable_local_cache:
            return
        
        self.local_cache[key] = {
            'data': data,
            'timestamp': time.time(),
            'type': data_type
        }
    
    def _get_cache(self, key: str, data_type: str = 'default') -> Optional[Any]:
        """获取本地缓存"""
        if not self.enable_local_cache:
            return None
        
        cache_entry = self.local_cache.get(key)
        ttl = self.cache_ttl.get(data_type, 3600)
        
        if self._is_cache_valid(cache_entry, ttl):
            logger.debug(f"Cache hit for key: {key}")
            return cache_entry['data']
        
        # 清理过期缓存
        if cache_entry:
            del self.local_cache[key]
        
        return None
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发起HTTP请求"""
        if not self.session:
            await self.initialize()
        
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                async with self.session.request(method, url, **kwargs) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        error_text = await response.text()
                        logger.warning(f"Request failed with status {response.status}: {error_text}")
                        
                        if response.status >= 500 and attempt < self.max_retries - 1:
                            # 服务器错误，重试
                            await asyncio.sleep(self.retry_delay * (attempt + 1))
                            continue
                        else:
                            raise aiohttp.ClientResponseError(
                                request_info=response.request_info,
                                history=response.history,
                                status=response.status,
                                message=error_text
                            )
            
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                else:
                    raise
        
        raise Exception(f"All {self.max_retries} attempts failed")
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            return await self._make_request('GET', '/health')
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    async def get_stocks(self, market: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """获取股票列表"""
        params = {'limit': limit, 'offset': offset}
        if market:
            params['market'] = market
        
        cache_key = self._get_cache_key('/api/v1/stocks', params)
        cached_data = self._get_cache(cache_key, 'stocks')
        if cached_data:
            return cached_data.get('data', [])
        
        try:
            response = await self._make_request('GET', '/api/v1/stocks', params=params)
            if response.get('success'):
                data = response.get('data', [])
                self._set_cache(cache_key, response, 'stocks')
                return data
            else:
                logger.error(f"Get stocks failed: {response.get('message', 'Unknown error')}")
                return []
        except Exception as e:
            logger.error(f"Failed to get stocks: {e}")
            return []
    
    async def get_historical_data(
        self, 
        stock_code: str, 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """获取历史数据"""
        params = {}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        if fields:
            params['fields'] = ','.join(fields)
        
        endpoint = f'/api/v1/stocks/{stock_code}/historical'
        cache_key = self._get_cache_key(endpoint, params)
        cached_data = self._get_cache(cache_key, 'historical')
        if cached_data:
            return cached_data.get('data', [])
        
        try:
            response = await self._make_request('GET', endpoint, params=params)
            if response.get('success'):
                data = response.get('data', [])
                self._set_cache(cache_key, response, 'historical')
                return data
            else:
                logger.error(f"Get historical data failed: {response.get('message', 'Unknown error')}")
                return []
        except Exception as e:
            logger.error(f"Failed to get historical data for {stock_code}: {e}")
            return []
    
    async def get_fundamental_data(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """获取基本面数据"""
        endpoint = f'/api/v1/stocks/{stock_code}/fundamental'
        cache_key = self._get_cache_key(endpoint)
        cached_data = self._get_cache(cache_key, 'fundamental')
        if cached_data:
            return cached_data.get('data')
        
        try:
            response = await self._make_request('GET', endpoint)
            if response.get('success'):
                data = response.get('data')
                self._set_cache(cache_key, response, 'fundamental')
                return data
            else:
                logger.error(f"Get fundamental data failed: {response.get('message', 'Unknown error')}")
                return None
        except Exception as e:
            logger.error(f"Failed to get fundamental data for {stock_code}: {e}")
            return None
    
    async def get_realtime_data(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """获取实时数据"""
        endpoint = f'/api/v1/stocks/{stock_code}/realtime'
        cache_key = self._get_cache_key(endpoint)
        cached_data = self._get_cache(cache_key, 'realtime')
        if cached_data:
            return cached_data.get('data')
        
        try:
            response = await self._make_request('GET', endpoint)
            if response.get('success'):
                data = response.get('data')
                self._set_cache(cache_key, response, 'realtime')
                return data
            else:
                logger.error(f"Get realtime data failed: {response.get('message', 'Unknown error')}")
                return None
        except Exception as e:
            logger.error(f"Failed to get realtime data for {stock_code}: {e}")
            return None
    
    async def trigger_data_refresh(
        self, 
        update_type: str, 
        stock_codes: Optional[List[str]] = None,
        force: bool = False
    ) -> bool:
        """触发数据刷新"""
        payload = {
            'update_type': update_type,
            'force': force
        }
        if stock_codes:
            payload['stock_codes'] = stock_codes
        
        try:
            response = await self._make_request('POST', '/api/v1/data/refresh', json=payload)
            if response.get('success'):
                logger.info(f"Data refresh triggered: {update_type}")
                return True
            else:
                logger.error(f"Trigger data refresh failed: {response.get('message', 'Unknown error')}")
                return False
        except Exception as e:
            logger.error(f"Failed to trigger data refresh: {e}")
            return False
    
    async def get_priority_config(self) -> Dict[str, Any]:
        """获取优先级配置"""
        cache_key = self._get_cache_key('/api/v1/config/priority')
        cached_data = self._get_cache(cache_key, 'config')
        if cached_data:
            return cached_data.get('data', {})
        
        try:
            response = await self._make_request('GET', '/api/v1/config/priority')
            if response.get('success'):
                data = response.get('data', {})
                self._set_cache(cache_key, response, 'config')
                return data
            else:
                logger.error(f"Get priority config failed: {response.get('message', 'Unknown error')}")
                return {}
        except Exception as e:
            logger.error(f"Failed to get priority config: {e}")
            return {}
    
    async def update_priority_config(
        self, 
        market: str, 
        data_type: str, 
        sources: List[Dict[str, Any]]
    ) -> bool:
        """更新优先级配置"""
        payload = {
            'market': market,
            'data_type': data_type,
            'sources': sources
        }
        
        try:
            response = await self._make_request('POST', '/api/v1/config/priority', json=payload)
            if response.get('success'):
                logger.info(f"Priority config updated: {market}:{data_type}")
                # 清理相关缓存
                self._clear_cache_by_pattern('/api/v1/config/priority')
                return True
            else:
                logger.error(f"Update priority config failed: {response.get('message', 'Unknown error')}")
                return False
        except Exception as e:
            logger.error(f"Failed to update priority config: {e}")
            return False
    
    async def get_scheduler_status(self) -> Dict[str, Any]:
        """获取调度器状态"""
        try:
            response = await self._make_request('GET', '/api/v1/status/scheduler')
            if response.get('success'):
                return response.get('data', {})
            else:
                logger.error(f"Get scheduler status failed: {response.get('message', 'Unknown error')}")
                return {}
        except Exception as e:
            logger.error(f"Failed to get scheduler status: {e}")
            return {}
    
    def _clear_cache_by_pattern(self, pattern: str):
        """根据模式清理缓存"""
        keys_to_remove = [key for key in self.local_cache.keys() if pattern in key]
        for key in keys_to_remove:
            del self.local_cache[key]
        logger.debug(f"Cleared {len(keys_to_remove)} cache entries matching pattern: {pattern}")
    
    def clear_cache(self):
        """清空所有缓存"""
        self.local_cache.clear()
        logger.debug("All local cache cleared")

# 全局客户端实例
_global_client: Optional[DataServiceClient] = None

def get_data_service_client() -> DataServiceClient:
    """获取全局数据服务客户端实例"""
    global _global_client
    if _global_client is None:
        _global_client = DataServiceClient()
    return _global_client

async def close_data_service_client():
    """关闭全局数据服务客户端"""
    global _global_client
    if _global_client:
        await _global_client.close()
        _global_client = None
