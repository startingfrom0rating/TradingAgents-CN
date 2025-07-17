#!/usr/bin/env python3
"""
微服务配置管理
处理服务发现、配置管理、环境切换等
"""

import os
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

from ..utils.logging_manager import get_logger

logger = get_logger(__name__)

class Environment(Enum):
    """环境类型"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class ServiceEndpoint:
    """服务端点配置"""
    name: str
    url: str
    timeout: int = 30
    max_retries: int = 3
    health_check_path: str = "/health"
    enabled: bool = True

@dataclass
class DatabaseConfig:
    """数据库配置"""
    host: str
    port: int
    database: str
    username: Optional[str] = None
    password: Optional[str] = None
    auth_source: str = "admin"
    enabled: bool = True

@dataclass
class CacheConfig:
    """缓存配置"""
    host: str
    port: int
    password: Optional[str] = None
    db: int = 0
    enabled: bool = True

class ServiceConfig:
    """微服务配置管理器"""
    
    def __init__(self, environment: Optional[Environment] = None):
        self.environment = environment or self._detect_environment()
        self.config = self._load_config()
        
        logger.info(f"ServiceConfig initialized for environment: {self.environment.value}")
    
    def _detect_environment(self) -> Environment:
        """自动检测环境"""
        env_name = os.getenv('TRADINGAGENTS_ENV', 'development').lower()
        
        try:
            return Environment(env_name)
        except ValueError:
            logger.warning(f"Unknown environment '{env_name}', defaulting to development")
            return Environment.DEVELOPMENT
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        config = {
            "services": {},
            "databases": {},
            "caches": {},
            "features": {}
        }
        
        # 加载基础配置
        config.update(self._get_base_config())
        
        # 加载环境特定配置
        config.update(self._get_environment_config())
        
        # 加载环境变量覆盖
        config.update(self._get_env_overrides())
        
        return config
    
    def _get_base_config(self) -> Dict[str, Any]:
        """获取基础配置"""
        return {
            "services": {
                "data_service": ServiceEndpoint(
                    name="data_service",
                    url="http://localhost:8001",
                    timeout=30,
                    max_retries=3
                )
            },
            "databases": {
                "mongodb": DatabaseConfig(
                    host="localhost",
                    port=27017,
                    database="tradingagents",
                    username="admin",
                    password="tradingagents123"
                )
            },
            "caches": {
                "redis": CacheConfig(
                    host="localhost",
                    port=6379,
                    password="tradingagents123",
                    db=0
                )
            },
            "features": {
                "enable_microservices": True,
                "enable_caching": True,
                "enable_monitoring": True,
                "auto_fallback": True
            }
        }
    
    def _get_environment_config(self) -> Dict[str, Any]:
        """获取环境特定配置"""
        env_configs = {
            Environment.DEVELOPMENT: {
                "services": {
                    "data_service": ServiceEndpoint(
                        name="data_service",
                        url="http://localhost:8001",
                        timeout=30
                    )
                }
            },
            Environment.TESTING: {
                "services": {
                    "data_service": ServiceEndpoint(
                        name="data_service",
                        url="http://localhost:8001",
                        timeout=10
                    )
                },
                "features": {
                    "enable_caching": False
                }
            },
            Environment.STAGING: {
                "services": {
                    "data_service": ServiceEndpoint(
                        name="data_service",
                        url="http://data-service:8001",
                        timeout=30
                    )
                },
                "databases": {
                    "mongodb": DatabaseConfig(
                        host="mongodb-service",
                        port=27017,
                        database="tradingagents_staging"
                    )
                },
                "caches": {
                    "redis": CacheConfig(
                        host="redis-service",
                        port=6379
                    )
                }
            },
            Environment.PRODUCTION: {
                "services": {
                    "data_service": ServiceEndpoint(
                        name="data_service",
                        url="http://data-service:8001",
                        timeout=60,
                        max_retries=5
                    )
                },
                "databases": {
                    "mongodb": DatabaseConfig(
                        host="mongodb-service",
                        port=27017,
                        database="tradingagents_prod"
                    )
                },
                "caches": {
                    "redis": CacheConfig(
                        host="redis-service",
                        port=6379
                    )
                }
            }
        }
        
        return env_configs.get(self.environment, {})
    
    def _get_env_overrides(self) -> Dict[str, Any]:
        """获取环境变量覆盖配置"""
        overrides = {}
        
        # 数据服务配置
        data_service_url = os.getenv('DATA_SERVICE_URL')
        if data_service_url:
            overrides.setdefault("services", {})
            overrides["services"]["data_service"] = ServiceEndpoint(
                name="data_service",
                url=data_service_url,
                timeout=int(os.getenv('DATA_SERVICE_TIMEOUT', 30)),
                max_retries=int(os.getenv('DATA_SERVICE_MAX_RETRIES', 3))
            )
        
        # MongoDB配置
        mongodb_host = os.getenv('MONGODB_HOST')
        if mongodb_host:
            overrides.setdefault("databases", {})
            overrides["databases"]["mongodb"] = DatabaseConfig(
                host=mongodb_host,
                port=int(os.getenv('MONGODB_PORT', 27017)),
                database=os.getenv('MONGODB_DATABASE', 'tradingagents'),
                username=os.getenv('MONGODB_USERNAME'),
                password=os.getenv('MONGODB_PASSWORD'),
                enabled=os.getenv('MONGODB_ENABLED', 'true').lower() == 'true'
            )
        
        # Redis配置
        redis_host = os.getenv('REDIS_HOST')
        if redis_host:
            overrides.setdefault("caches", {})
            overrides["caches"]["redis"] = CacheConfig(
                host=redis_host,
                port=int(os.getenv('REDIS_PORT', 6379)),
                password=os.getenv('REDIS_PASSWORD'),
                db=int(os.getenv('REDIS_DB', 0)),
                enabled=os.getenv('REDIS_ENABLED', 'true').lower() == 'true'
            )
        
        # 功能开关
        features = {}
        if os.getenv('ENABLE_MICROSERVICES') is not None:
            features['enable_microservices'] = os.getenv('ENABLE_MICROSERVICES', 'true').lower() == 'true'
        if os.getenv('ENABLE_CACHING') is not None:
            features['enable_caching'] = os.getenv('ENABLE_CACHING', 'true').lower() == 'true'
        if os.getenv('AUTO_FALLBACK') is not None:
            features['auto_fallback'] = os.getenv('AUTO_FALLBACK', 'true').lower() == 'true'
        
        if features:
            overrides["features"] = features
        
        return overrides
    
    def get_service_endpoint(self, service_name: str) -> Optional[ServiceEndpoint]:
        """获取服务端点配置"""
        services = self.config.get("services", {})
        service_config = services.get(service_name)
        
        if isinstance(service_config, dict):
            return ServiceEndpoint(**service_config)
        elif isinstance(service_config, ServiceEndpoint):
            return service_config
        
        return None
    
    def get_database_config(self, db_name: str) -> Optional[DatabaseConfig]:
        """获取数据库配置"""
        databases = self.config.get("databases", {})
        db_config = databases.get(db_name)
        
        if isinstance(db_config, dict):
            return DatabaseConfig(**db_config)
        elif isinstance(db_config, DatabaseConfig):
            return db_config
        
        return None
    
    def get_cache_config(self, cache_name: str) -> Optional[CacheConfig]:
        """获取缓存配置"""
        caches = self.config.get("caches", {})
        cache_config = caches.get(cache_name)
        
        if isinstance(cache_config, dict):
            return CacheConfig(**cache_config)
        elif isinstance(cache_config, CacheConfig):
            return cache_config
        
        return None
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """检查功能是否启用"""
        features = self.config.get("features", {})
        return features.get(feature_name, False)
    
    def get_mongodb_connection_string(self) -> Optional[str]:
        """获取MongoDB连接字符串"""
        db_config = self.get_database_config("mongodb")
        if not db_config or not db_config.enabled:
            return None
        
        if db_config.username and db_config.password:
            return f"mongodb://{db_config.username}:{db_config.password}@{db_config.host}:{db_config.port}/{db_config.database}?authSource={db_config.auth_source}"
        else:
            return f"mongodb://{db_config.host}:{db_config.port}/{db_config.database}"
    
    def get_redis_connection_string(self) -> Optional[str]:
        """获取Redis连接字符串"""
        cache_config = self.get_cache_config("redis")
        if not cache_config or not cache_config.enabled:
            return None
        
        if cache_config.password:
            return f"redis://:{cache_config.password}@{cache_config.host}:{cache_config.port}/{cache_config.db}"
        else:
            return f"redis://{cache_config.host}:{cache_config.port}/{cache_config.db}"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "environment": self.environment.value,
            "config": self.config
        }
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), indent=2, default=str)

# 全局配置实例
_global_config: Optional[ServiceConfig] = None

def get_service_config() -> ServiceConfig:
    """获取全局服务配置实例"""
    global _global_config
    if _global_config is None:
        _global_config = ServiceConfig()
    return _global_config

def reload_service_config():
    """重新加载服务配置"""
    global _global_config
    _global_config = None
    return get_service_config()
