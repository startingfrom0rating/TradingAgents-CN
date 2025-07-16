#!/usr/bin/env python3
"""
Redis存储配置
提供Redis连接和基础操作功能
"""

import os
import json
import asyncio
from typing import Optional, Any, List, Dict
import aioredis
from aioredis import Redis

from ..utils.logging_manager import get_logger

logger = get_logger(__name__)

class RedisStorage:
    """Redis存储类"""
    
    def __init__(self, connection_string: Optional[str] = None):
        self.connection_string = connection_string or self._get_connection_string()
        self.redis: Optional[Redis] = None
        self.is_connected = False
    
    def _get_connection_string(self) -> str:
        """获取Redis连接字符串"""
        # 从环境变量获取
        redis_url = os.getenv('REDIS_URL')
        if redis_url:
            return redis_url

        # 从环境变量组合
        host = os.getenv('REDIS_HOST', 'localhost')
        port = int(os.getenv('REDIS_PORT', 6379))
        password = os.getenv('REDIS_PASSWORD')
        db = int(os.getenv('REDIS_DB', 0))

        # 检查Redis是否启用
        redis_enabled = os.getenv('REDIS_ENABLED', 'false').lower() == 'true'
        if not redis_enabled:
            # 如果Redis未启用，返回一个无效的连接字符串，让连接失败并降级
            return "redis://disabled:6379/0"

        if password:
            return f"redis://:{password}@{host}:{port}/{db}"
        else:
            return f"redis://{host}:{port}/{db}"
    
    async def initialize(self):
        """初始化Redis连接"""
        try:
            self.redis = await aioredis.from_url(
                self.connection_string,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5
            )
            
            # 测试连接
            await self.redis.ping()
            self.is_connected = True
            logger.info("Redis连接成功")
            
        except Exception as e:
            logger.warning(f"Redis连接失败: {e}")
            self.is_connected = False
            self.redis = None
    
    async def get(self, key: str) -> Optional[str]:
        """获取值"""
        if not self.is_connected or not self.redis:
            return None
        
        try:
            return await self.redis.get(key)
        except Exception as e:
            logger.error(f"Redis GET失败 {key}: {e}")
            return None
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """设置值"""
        if not self.is_connected or not self.redis:
            return False
        
        try:
            if ttl:
                await self.redis.setex(key, ttl, value)
            else:
                await self.redis.set(key, value)
            return True
        except Exception as e:
            logger.error(f"Redis SET失败 {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """删除键"""
        if not self.is_connected or not self.redis:
            return False
        
        try:
            result = await self.redis.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis DELETE失败 {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        if not self.is_connected or not self.redis:
            return False
        
        try:
            result = await self.redis.exists(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis EXISTS失败 {key}: {e}")
            return False
    
    async def get_keys_by_pattern(self, pattern: str) -> List[str]:
        """根据模式获取键列表"""
        if not self.is_connected or not self.redis:
            return []
        
        try:
            keys = await self.redis.keys(pattern)
            return keys if keys else []
        except Exception as e:
            logger.error(f"Redis KEYS失败 {pattern}: {e}")
            return []
    
    async def clear_all(self) -> bool:
        """清空所有数据"""
        if not self.is_connected or not self.redis:
            return False
        
        try:
            await self.redis.flushdb()
            return True
        except Exception as e:
            logger.error(f"Redis FLUSHDB失败: {e}")
            return False
    
    async def ping(self) -> bool:
        """测试连接"""
        if not self.is_connected or not self.redis:
            return False
        
        try:
            await self.redis.ping()
            return True
        except Exception as e:
            logger.error(f"Redis PING失败: {e}")
            return False
    
    async def get_info(self) -> Dict[str, Any]:
        """获取Redis信息"""
        if not self.is_connected or not self.redis:
            return {}
        
        try:
            info = await self.redis.info()
            return {
                "version": info.get("redis_version", "unknown"),
                "used_memory": info.get("used_memory_human", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0)
            }
        except Exception as e:
            logger.error(f"Redis INFO失败: {e}")
            return {}
    
    async def close(self):
        """关闭连接"""
        if self.redis:
            try:
                await self.redis.close()
                self.is_connected = False
                logger.info("Redis连接已关闭")
            except Exception as e:
                logger.error(f"关闭Redis连接失败: {e}")

# 全局实例
redis_storage = RedisStorage()
