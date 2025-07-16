#!/usr/bin/env python3
"""
Redis缓存管理器
支持多层次缓存策略，提升数据访问性能
"""

import json
import pickle
import asyncio
from datetime import datetime, timedelta
from typing import Any, Optional, List, Dict, Union
import aioredis
from dataclasses import dataclass

from ..utils.logging_manager import get_logger
from ..config.redis_storage import RedisStorage

logger = get_logger(__name__)

@dataclass
class CacheConfig:
    """缓存配置"""
    ttl: int = 3600  # 默认1小时
    storage_type: str = "redis"  # redis, memory, file
    compression: bool = False
    serialization: str = "json"  # json, pickle

class RedisCacheManager:
    """Redis缓存管理器"""
    
    def __init__(self):
        self.redis_storage = RedisStorage()
        self.memory_cache: Dict[str, Dict] = {}
        self.cache_configs: Dict[str, CacheConfig] = {}
        
        # 内存缓存大小限制
        self.max_memory_items = 1000
        self.memory_access_order = []
        
        # 默认缓存配置
        self.setup_default_configs()
    
    def setup_default_configs(self):
        """设置默认缓存配置"""
        self.cache_configs = {
            "realtime": CacheConfig(ttl=60, storage_type="memory"),
            "historical": CacheConfig(ttl=3600, storage_type="redis"),
            "fundamental": CacheConfig(ttl=7200, storage_type="redis"),
            "company": CacheConfig(ttl=86400, storage_type="redis"),
            "priority": CacheConfig(ttl=1800, storage_type="memory"),
            "news": CacheConfig(ttl=900, storage_type="redis")
        }
    
    async def initialize(self):
        """初始化缓存管理器"""
        try:
            await self.redis_storage.initialize()
            logger.info("RedisCacheManager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RedisCacheManager: {e}")
            # 如果Redis不可用，只使用内存缓存
            logger.warning("Redis unavailable, using memory cache only")
    
    def get_cache_config(self, key: str) -> CacheConfig:
        """获取缓存配置"""
        # 从key中提取数据类型
        data_type = key.split(':')[0] if ':' in key else 'default'
        return self.cache_configs.get(data_type, CacheConfig())
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        try:
            config = self.get_cache_config(key)
            
            if config.storage_type == "memory":
                return await self._get_from_memory(key)
            elif config.storage_type == "redis":
                return await self._get_from_redis(key, config)
            else:
                return await self._get_from_file(key, config)
                
        except Exception as e:
            logger.error(f"Failed to get cache for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存数据"""
        try:
            config = self.get_cache_config(key)
            if ttl is not None:
                config.ttl = ttl
            
            if config.storage_type == "memory":
                return await self._set_to_memory(key, value, config)
            elif config.storage_type == "redis":
                return await self._set_to_redis(key, value, config)
            else:
                return await self._set_to_file(key, value, config)
                
        except Exception as e:
            logger.error(f"Failed to set cache for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存数据"""
        try:
            config = self.get_cache_config(key)
            
            if config.storage_type == "memory":
                return await self._delete_from_memory(key)
            elif config.storage_type == "redis":
                return await self._delete_from_redis(key)
            else:
                return await self._delete_from_file(key)
                
        except Exception as e:
            logger.error(f"Failed to delete cache for key {key}: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """删除匹配模式的缓存"""
        try:
            deleted_count = 0
            
            # 删除内存缓存
            memory_keys = [k for k in self.memory_cache.keys() if self._match_pattern(k, pattern)]
            for key in memory_keys:
                await self._delete_from_memory(key)
                deleted_count += 1
            
            # 删除Redis缓存
            try:
                redis_keys = await self.redis_storage.get_keys_by_pattern(pattern)
                for key in redis_keys:
                    await self._delete_from_redis(key)
                    deleted_count += 1
            except Exception as e:
                logger.debug(f"Redis pattern delete failed: {e}")
            
            logger.debug(f"Deleted {deleted_count} cache entries matching pattern: {pattern}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to delete cache pattern {pattern}: {e}")
            return 0
    
    def _match_pattern(self, key: str, pattern: str) -> bool:
        """简单的模式匹配"""
        if pattern.endswith('*'):
            return key.startswith(pattern[:-1])
        return key == pattern
    
    async def _get_from_memory(self, key: str) -> Optional[Any]:
        """从内存缓存获取"""
        if key in self.memory_cache:
            cache_item = self.memory_cache[key]
            
            # 检查是否过期
            if datetime.now() > cache_item['expires_at']:
                await self._delete_from_memory(key)
                return None
            
            # 更新访问顺序
            if key in self.memory_access_order:
                self.memory_access_order.remove(key)
            self.memory_access_order.append(key)
            
            return cache_item['value']
        
        return None
    
    async def _set_to_memory(self, key: str, value: Any, config: CacheConfig) -> bool:
        """设置内存缓存"""
        # 检查内存缓存大小限制
        if len(self.memory_cache) >= self.max_memory_items:
            # 删除最久未访问的项
            if self.memory_access_order:
                oldest_key = self.memory_access_order.pop(0)
                self.memory_cache.pop(oldest_key, None)
        
        expires_at = datetime.now() + timedelta(seconds=config.ttl)
        self.memory_cache[key] = {
            'value': value,
            'expires_at': expires_at,
            'created_at': datetime.now()
        }
        
        # 更新访问顺序
        if key in self.memory_access_order:
            self.memory_access_order.remove(key)
        self.memory_access_order.append(key)
        
        return True
    
    async def _delete_from_memory(self, key: str) -> bool:
        """从内存缓存删除"""
        if key in self.memory_cache:
            del self.memory_cache[key]
            if key in self.memory_access_order:
                self.memory_access_order.remove(key)
            return True
        return False
    
    async def _get_from_redis(self, key: str, config: CacheConfig) -> Optional[Any]:
        """从Redis缓存获取"""
        try:
            data = await self.redis_storage.get(key)
            if data is None:
                return None
            
            # 反序列化
            if config.serialization == "pickle":
                return pickle.loads(data)
            else:
                return json.loads(data)
                
        except Exception as e:
            logger.debug(f"Redis get failed for key {key}: {e}")
            return None
    
    async def _set_to_redis(self, key: str, value: Any, config: CacheConfig) -> bool:
        """设置Redis缓存"""
        try:
            # 序列化
            if config.serialization == "pickle":
                data = pickle.dumps(value)
            else:
                data = json.dumps(value, default=str)
            
            await self.redis_storage.set(key, data, ttl=config.ttl)
            return True
            
        except Exception as e:
            logger.debug(f"Redis set failed for key {key}: {e}")
            return False
    
    async def _delete_from_redis(self, key: str) -> bool:
        """从Redis缓存删除"""
        try:
            await self.redis_storage.delete(key)
            return True
        except Exception as e:
            logger.debug(f"Redis delete failed for key {key}: {e}")
            return False
    
    async def _get_from_file(self, key: str, config: CacheConfig) -> Optional[Any]:
        """从文件缓存获取"""
        # 简化实现，实际可以使用磁盘缓存
        return None
    
    async def _set_to_file(self, key: str, value: Any, config: CacheConfig) -> bool:
        """设置文件缓存"""
        # 简化实现，实际可以使用磁盘缓存
        return False
    
    async def _delete_from_file(self, key: str) -> bool:
        """从文件缓存删除"""
        # 简化实现，实际可以使用磁盘缓存
        return False
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        try:
            stats = {
                "memory_cache": {
                    "items": len(self.memory_cache),
                    "max_items": self.max_memory_items,
                    "hit_rate": 0.0  # 需要实现命中率统计
                },
                "redis_cache": {
                    "available": False,
                    "info": {}
                }
            }
            
            # 获取Redis统计信息
            try:
                redis_info = await self.redis_storage.get_info()
                stats["redis_cache"]["available"] = True
                stats["redis_cache"]["info"] = redis_info
            except Exception as e:
                logger.debug(f"Failed to get Redis info: {e}")
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {}
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            health = {
                "memory_cache": {
                    "status": "healthy",
                    "items": len(self.memory_cache)
                },
                "redis_cache": {
                    "status": "unknown"
                }
            }
            
            # 检查Redis连接
            try:
                await self.redis_storage.ping()
                health["redis_cache"]["status"] = "healthy"
            except Exception as e:
                health["redis_cache"]["status"] = "unhealthy"
                health["redis_cache"]["error"] = str(e)
            
            return health
            
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}

# 全局实例
redis_cache_manager = RedisCacheManager()
