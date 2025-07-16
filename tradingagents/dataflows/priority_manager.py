#!/usr/bin/env python3
"""
数据源优先级管理系统
支持用户自定义数据源优先级，动态配置和A/B测试
"""

import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

from ..utils.logging_manager import get_logger
from .mongodb_storage import MongoDBDataStorage
from .cache_manager import CacheManager

logger = get_logger(__name__)

class DataType(Enum):
    """数据类型枚举"""
    HISTORICAL = "historical"
    REALTIME = "realtime"
    FUNDAMENTAL = "fundamental"
    NEWS = "news"
    COMPANY_INFO = "company_info"

class Market(Enum):
    """市场类型枚举"""
    CN = "cn"  # A股
    HK = "hk"  # 港股
    US = "us"  # 美股

@dataclass
class DataSourceConfig:
    """数据源配置"""
    source_name: str
    priority: int  # 优先级，数字越小优先级越高
    enabled: bool = True
    weight: float = 1.0  # 权重，用于负载均衡
    max_requests_per_minute: int = 60
    timeout_seconds: int = 30
    retry_count: int = 3
    
    # A/B测试相关
    ab_test_group: Optional[str] = None
    ab_test_ratio: float = 0.0  # 0.0-1.0，分配给此数据源的流量比例

@dataclass
class PriorityRule:
    """优先级规则"""
    market: Market
    data_type: DataType
    sources: List[DataSourceConfig]
    created_at: datetime
    updated_at: datetime
    created_by: str = "system"
    description: str = ""

class DataSourcePriorityManager:
    """数据源优先级管理器"""
    
    def __init__(self):
        self.mongodb = MongoDBDataStorage()
        self.cache = CacheManager()
        self.config_cache: Dict[str, PriorityRule] = {}
        self.ab_test_configs: Dict[str, Dict] = {}
        
        # 配置变更回调
        self.config_change_callbacks = []
    
    async def initialize(self):
        """初始化优先级管理器"""
        try:
            await self.mongodb.initialize()
            await self.load_priority_configs()
            await self.load_ab_test_configs()
            logger.info("DataSourcePriorityManager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize DataSourcePriorityManager: {e}")
            raise
    
    async def load_priority_configs(self):
        """加载优先级配置"""
        try:
            configs = await self.mongodb.get_priority_configs()
            
            if not configs:
                # 如果没有配置，创建默认配置
                await self.create_default_configs()
                configs = await self.mongodb.get_priority_configs()
            
            self.config_cache = {}
            for config_data in configs:
                rule = self._dict_to_priority_rule(config_data)
                key = self._get_config_key(rule.market, rule.data_type)
                self.config_cache[key] = rule
            
            logger.info(f"Loaded {len(self.config_cache)} priority configurations")
            
        except Exception as e:
            logger.error(f"Failed to load priority configs: {e}")
            raise
    
    async def create_default_configs(self):
        """创建默认优先级配置"""
        default_configs = [
            # A股配置
            PriorityRule(
                market=Market.CN,
                data_type=DataType.HISTORICAL,
                sources=[
                    DataSourceConfig("baostock", 1, True, 1.0, 60, 30, 3),
                    DataSourceConfig("akshare", 2, True, 1.0, 60, 30, 3),
                    DataSourceConfig("tushare", 3, True, 0.8, 30, 30, 2)
                ],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                description="A股历史数据默认配置"
            ),
            PriorityRule(
                market=Market.CN,
                data_type=DataType.REALTIME,
                sources=[
                    DataSourceConfig("akshare", 1, True, 1.0, 120, 15, 3),
                    DataSourceConfig("tushare", 2, True, 0.8, 60, 15, 2),
                    DataSourceConfig("baostock", 3, True, 0.5, 60, 30, 2)
                ],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                description="A股实时数据默认配置"
            ),
            PriorityRule(
                market=Market.CN,
                data_type=DataType.FUNDAMENTAL,
                sources=[
                    DataSourceConfig("tushare", 1, True, 1.0, 30, 30, 3),
                    DataSourceConfig("akshare", 2, True, 0.8, 60, 30, 2),
                    DataSourceConfig("baostock", 3, True, 0.5, 60, 30, 2)
                ],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                description="A股基本面数据默认配置"
            ),
            
            # 港股配置
            PriorityRule(
                market=Market.HK,
                data_type=DataType.HISTORICAL,
                sources=[
                    DataSourceConfig("akshare", 1, True, 1.0, 60, 30, 3),
                    DataSourceConfig("yahoo", 2, True, 0.8, 60, 30, 2)
                ],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                description="港股历史数据默认配置"
            ),
            PriorityRule(
                market=Market.HK,
                data_type=DataType.REALTIME,
                sources=[
                    DataSourceConfig("akshare", 1, True, 1.0, 120, 15, 3),
                    DataSourceConfig("yahoo", 2, True, 0.8, 60, 15, 2)
                ],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                description="港股实时数据默认配置"
            ),
            
            # 美股配置
            PriorityRule(
                market=Market.US,
                data_type=DataType.HISTORICAL,
                sources=[
                    DataSourceConfig("yahoo", 1, True, 1.0, 60, 30, 3),
                    DataSourceConfig("finnhub", 2, True, 0.8, 30, 30, 2)
                ],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                description="美股历史数据默认配置"
            ),
            PriorityRule(
                market=Market.US,
                data_type=DataType.FUNDAMENTAL,
                sources=[
                    DataSourceConfig("finnhub", 1, True, 1.0, 30, 30, 3),
                    DataSourceConfig("yahoo", 2, True, 0.8, 60, 30, 2)
                ],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                description="美股基本面数据默认配置"
            )
        ]
        
        # 保存默认配置
        for config in default_configs:
            await self.save_priority_config(config)
        
        logger.info("Created default priority configurations")
    
    def _get_config_key(self, market: Market, data_type: DataType) -> str:
        """生成配置键"""
        return f"{market.value}:{data_type.value}"
    
    def _dict_to_priority_rule(self, data: Dict) -> PriorityRule:
        """字典转换为优先级规则"""
        sources = [
            DataSourceConfig(**source_data) 
            for source_data in data.get('sources', [])
        ]
        
        return PriorityRule(
            market=Market(data['market']),
            data_type=DataType(data['data_type']),
            sources=sources,
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            created_by=data.get('created_by', 'system'),
            description=data.get('description', '')
        )
    
    def _priority_rule_to_dict(self, rule: PriorityRule) -> Dict:
        """优先级规则转换为字典"""
        return {
            'market': rule.market.value,
            'data_type': rule.data_type.value,
            'sources': [asdict(source) for source in rule.sources],
            'created_at': rule.created_at.isoformat(),
            'updated_at': rule.updated_at.isoformat(),
            'created_by': rule.created_by,
            'description': rule.description
        }
    
    async def get_priority_list(self, market: str, data_type: str) -> List[DataSourceConfig]:
        """获取优先级列表"""
        try:
            market_enum = Market(market)
            data_type_enum = DataType(data_type)
            key = self._get_config_key(market_enum, data_type_enum)
            
            rule = self.config_cache.get(key)
            if not rule:
                logger.warning(f"No priority config found for {key}")
                return []
            
            # 过滤启用的数据源并按优先级排序
            enabled_sources = [s for s in rule.sources if s.enabled]
            enabled_sources.sort(key=lambda x: x.priority)
            
            return enabled_sources
            
        except Exception as e:
            logger.error(f"Failed to get priority list for {market}:{data_type}: {e}")
            return []
    
    async def update_priority_config(
        self, 
        market: str, 
        data_type: str, 
        sources: List[Dict],
        updated_by: str = "user"
    ):
        """更新优先级配置"""
        try:
            market_enum = Market(market)
            data_type_enum = DataType(data_type)
            
            # 创建新的配置
            source_configs = [DataSourceConfig(**source) for source in sources]
            
            rule = PriorityRule(
                market=market_enum,
                data_type=data_type_enum,
                sources=source_configs,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                created_by=updated_by,
                description=f"Updated by {updated_by}"
            )
            
            # 保存配置
            await self.save_priority_config(rule)
            
            # 更新缓存
            key = self._get_config_key(market_enum, data_type_enum)
            self.config_cache[key] = rule
            
            # 清除相关缓存
            await self.cache.delete_pattern(f"priority:{market}:{data_type}:*")
            
            # 通知配置变更
            await self.notify_config_change(market, data_type, rule)
            
            logger.info(f"Updated priority config for {market}:{data_type}")
            
        except Exception as e:
            logger.error(f"Failed to update priority config: {e}")
            raise
    
    async def save_priority_config(self, rule: PriorityRule):
        """保存优先级配置到数据库"""
        config_data = self._priority_rule_to_dict(rule)
        await self.mongodb.save_priority_config(config_data)
    
    async def get_all_configs(self) -> Dict[str, Dict]:
        """获取所有配置"""
        result = {}
        for key, rule in self.config_cache.items():
            market, data_type = key.split(':')
            if market not in result:
                result[market] = {}
            result[market][data_type] = {
                'sources': [asdict(source) for source in rule.sources],
                'description': rule.description,
                'updated_at': rule.updated_at.isoformat()
            }
        return result
    
    async def load_ab_test_configs(self):
        """加载A/B测试配置"""
        try:
            configs = await self.mongodb.get_ab_test_configs()
            self.ab_test_configs = configs or {}
            logger.info(f"Loaded {len(self.ab_test_configs)} A/B test configurations")
        except Exception as e:
            logger.error(f"Failed to load A/B test configs: {e}")
    
    async def create_ab_test(
        self, 
        test_name: str, 
        market: str, 
        data_type: str,
        test_config: Dict
    ):
        """创建A/B测试"""
        try:
            ab_test = {
                'test_name': test_name,
                'market': market,
                'data_type': data_type,
                'config': test_config,
                'created_at': datetime.now().isoformat(),
                'status': 'active'
            }
            
            await self.mongodb.save_ab_test_config(test_name, ab_test)
            self.ab_test_configs[test_name] = ab_test
            
            logger.info(f"Created A/B test: {test_name}")
            
        except Exception as e:
            logger.error(f"Failed to create A/B test: {e}")
            raise
    
    def select_data_source_for_ab_test(
        self, 
        market: str, 
        data_type: str, 
        user_id: str
    ) -> Optional[str]:
        """为A/B测试选择数据源"""
        # 简化的A/B测试逻辑
        # 实际实现可以更复杂，考虑用户分组、流量分配等
        import hashlib
        
        hash_input = f"{market}:{data_type}:{user_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        
        # 基于哈希值选择测试组
        if hash_value % 100 < 10:  # 10%的用户参与A/B测试
            return "test_group"
        else:
            return "control_group"
    
    async def notify_config_change(self, market: str, data_type: str, rule: PriorityRule):
        """通知配置变更"""
        for callback in self.config_change_callbacks:
            try:
                await callback(market, data_type, rule)
            except Exception as e:
                logger.error(f"Config change callback failed: {e}")
    
    def add_config_change_callback(self, callback):
        """添加配置变更回调"""
        self.config_change_callbacks.append(callback)

# 全局实例
priority_manager = DataSourcePriorityManager()
