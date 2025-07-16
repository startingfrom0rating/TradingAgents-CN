#!/usr/bin/env python3
"""
MongoDB数据存储扩展
专门为数据源优化功能提供的MongoDB存储接口
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import pymongo

from ..utils.logging_manager import get_logger
from ..config.mongodb_storage import MongoDBStorage

logger = get_logger(__name__)

class MongoDBDataStorage(MongoDBStorage):
    """扩展的MongoDB数据存储类"""
    
    def __init__(self):
        super().__init__()
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        
        # 集合名称
        self.collections = {
            'stocks': 'stocks',
            'historical_data': 'historical_data',
            'fundamental_data': 'fundamental_data',
            'company_info': 'company_info',
            'realtime_data': 'realtime_data',
            'priority_configs': 'priority_configs',
            'ab_test_configs': 'ab_test_configs',
            'update_logs': 'update_logs',
            'data_quality': 'data_quality'
        }
    
    async def initialize(self):
        """初始化MongoDB连接和索引"""
        try:
            await super().initialize()
            self.client = self.get_client()
            self.db = self.get_database()
            
            # 创建索引
            await self.create_indexes()
            
            logger.info("MongoDBDataStorage initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MongoDBDataStorage: {e}")
            raise
    
    async def create_indexes(self):
        """创建数据库索引"""
        try:
            # 股票信息索引
            await self.db[self.collections['stocks']].create_index([
                ("code", pymongo.ASCENDING),
                ("market", pymongo.ASCENDING)
            ], unique=True)
            
            # 历史数据索引
            await self.db[self.collections['historical_data']].create_index([
                ("stock_code", pymongo.ASCENDING),
                ("date", pymongo.DESCENDING)
            ])
            await self.db[self.collections['historical_data']].create_index([
                ("stock_code", pymongo.ASCENDING),
                ("date", pymongo.ASCENDING)
            ])
            
            # 基本面数据索引
            await self.db[self.collections['fundamental_data']].create_index([
                ("stock_code", pymongo.ASCENDING),
                ("updated_at", pymongo.DESCENDING)
            ])
            
            # 公司信息索引
            await self.db[self.collections['company_info']].create_index([
                ("stock_code", pymongo.ASCENDING)
            ], unique=True)
            
            # 实时数据索引
            await self.db[self.collections['realtime_data']].create_index([
                ("stock_code", pymongo.ASCENDING),
                ("timestamp", pymongo.DESCENDING)
            ])
            
            # 优先级配置索引
            await self.db[self.collections['priority_configs']].create_index([
                ("market", pymongo.ASCENDING),
                ("data_type", pymongo.ASCENDING)
            ], unique=True)
            
            # 更新日志索引
            await self.db[self.collections['update_logs']].create_index([
                ("update_type", pymongo.ASCENDING),
                ("timestamp", pymongo.DESCENDING)
            ])
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
            raise
    
    async def get_active_stocks(self) -> List[Dict[str, Any]]:
        """获取活跃股票列表"""
        try:
            cursor = self.db[self.collections['stocks']].find(
                {"status": "active"},
                {"code": 1, "name": 1, "market": 1, "industry": 1}
            )
            stocks = await cursor.to_list(length=None)
            return stocks
        except Exception as e:
            logger.error(f"Failed to get active stocks: {e}")
            return []
    
    async def get_hot_stocks(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取热门股票列表"""
        try:
            # 基于最近访问频率或交易量排序
            cursor = self.db[self.collections['stocks']].find(
                {"status": "active"},
                {"code": 1, "name": 1, "market": 1}
            ).sort("access_count", -1).limit(limit)
            
            stocks = await cursor.to_list(length=None)
            return stocks
        except Exception as e:
            logger.error(f"Failed to get hot stocks: {e}")
            return []
    
    async def get_last_data_date(self, stock_code: str) -> Optional[datetime]:
        """获取股票最新数据日期"""
        try:
            result = await self.db[self.collections['historical_data']].find_one(
                {"stock_code": stock_code},
                sort=[("date", -1)]
            )
            
            if result and "date" in result:
                if isinstance(result["date"], str):
                    return datetime.strptime(result["date"], "%Y-%m-%d")
                return result["date"]
            
            return None
        except Exception as e:
            logger.error(f"Failed to get last data date for {stock_code}: {e}")
            return None
    
    async def save_historical_data(self, stock_code: str, data: List[Dict[str, Any]]):
        """保存历史数据"""
        try:
            if not data:
                return
            
            # 准备批量操作
            operations = []
            for record in data:
                # 确保数据格式正确
                record["stock_code"] = stock_code
                record["updated_at"] = datetime.now()
                
                # 使用upsert避免重复数据
                filter_doc = {
                    "stock_code": stock_code,
                    "date": record["date"]
                }
                
                operations.append(
                    pymongo.UpdateOne(
                        filter_doc,
                        {"$set": record},
                        upsert=True
                    )
                )
            
            # 批量执行
            if operations:
                result = await self.db[self.collections['historical_data']].bulk_write(operations)
                logger.debug(f"Saved {result.upserted_count + result.modified_count} historical records for {stock_code}")
                
                # 记录更新日志
                await self.log_data_update("historical", stock_code, len(data))
                
        except Exception as e:
            logger.error(f"Failed to save historical data for {stock_code}: {e}")
            raise
    
    async def get_historical_data(
        self, 
        stock_code: str, 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """获取历史数据"""
        try:
            # 构建查询条件
            query = {"stock_code": stock_code}
            
            if start_date or end_date:
                date_filter = {}
                if start_date:
                    date_filter["$gte"] = start_date
                if end_date:
                    date_filter["$lte"] = end_date
                query["date"] = date_filter
            
            # 构建投影
            projection = None
            if fields:
                projection = {field: 1 for field in fields}
                projection["_id"] = 0
            
            # 执行查询
            cursor = self.db[self.collections['historical_data']].find(
                query, projection
            ).sort("date", 1)
            
            data = await cursor.to_list(length=None)
            return data
            
        except Exception as e:
            logger.error(f"Failed to get historical data for {stock_code}: {e}")
            return []
    
    async def save_fundamental_data(self, stock_code: str, data: Dict[str, Any]):
        """保存基本面数据"""
        try:
            data["stock_code"] = stock_code
            data["updated_at"] = datetime.now()
            
            # 使用upsert更新或插入
            await self.db[self.collections['fundamental_data']].update_one(
                {"stock_code": stock_code},
                {"$set": data},
                upsert=True
            )
            
            logger.debug(f"Saved fundamental data for {stock_code}")
            await self.log_data_update("fundamental", stock_code, 1)
            
        except Exception as e:
            logger.error(f"Failed to save fundamental data for {stock_code}: {e}")
            raise
    
    async def get_fundamental_data(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """获取基本面数据"""
        try:
            data = await self.db[self.collections['fundamental_data']].find_one(
                {"stock_code": stock_code},
                {"_id": 0}
            )
            return data
        except Exception as e:
            logger.error(f"Failed to get fundamental data for {stock_code}: {e}")
            return None
    
    async def save_company_info(self, stock_code: str, data: Dict[str, Any]):
        """保存公司信息"""
        try:
            data["stock_code"] = stock_code
            data["updated_at"] = datetime.now()
            
            await self.db[self.collections['company_info']].update_one(
                {"stock_code": stock_code},
                {"$set": data},
                upsert=True
            )
            
            logger.debug(f"Saved company info for {stock_code}")
            await self.log_data_update("company", stock_code, 1)
            
        except Exception as e:
            logger.error(f"Failed to save company info for {stock_code}: {e}")
            raise
    
    async def get_priority_configs(self) -> List[Dict[str, Any]]:
        """获取优先级配置"""
        try:
            cursor = self.db[self.collections['priority_configs']].find({}, {"_id": 0})
            configs = await cursor.to_list(length=None)
            return configs
        except Exception as e:
            logger.error(f"Failed to get priority configs: {e}")
            return []
    
    async def save_priority_config(self, config: Dict[str, Any]):
        """保存优先级配置"""
        try:
            await self.db[self.collections['priority_configs']].update_one(
                {
                    "market": config["market"],
                    "data_type": config["data_type"]
                },
                {"$set": config},
                upsert=True
            )
            
            logger.debug(f"Saved priority config for {config['market']}:{config['data_type']}")
            
        except Exception as e:
            logger.error(f"Failed to save priority config: {e}")
            raise
    
    async def get_ab_test_configs(self) -> Dict[str, Any]:
        """获取A/B测试配置"""
        try:
            cursor = self.db[self.collections['ab_test_configs']].find({}, {"_id": 0})
            configs = await cursor.to_list(length=None)
            return {config["test_name"]: config for config in configs}
        except Exception as e:
            logger.error(f"Failed to get A/B test configs: {e}")
            return {}
    
    async def save_ab_test_config(self, test_name: str, config: Dict[str, Any]):
        """保存A/B测试配置"""
        try:
            await self.db[self.collections['ab_test_configs']].update_one(
                {"test_name": test_name},
                {"$set": config},
                upsert=True
            )
            
            logger.debug(f"Saved A/B test config: {test_name}")
            
        except Exception as e:
            logger.error(f"Failed to save A/B test config: {e}")
            raise
    
    async def log_data_update(self, update_type: str, stock_code: str, record_count: int):
        """记录数据更新日志"""
        try:
            log_entry = {
                "update_type": update_type,
                "stock_code": stock_code,
                "record_count": record_count,
                "timestamp": datetime.now(),
                "status": "success"
            }
            
            await self.db[self.collections['update_logs']].insert_one(log_entry)
            
        except Exception as e:
            logger.error(f"Failed to log data update: {e}")
    
    async def get_stocks(self, market: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """获取股票列表"""
        try:
            query = {}
            if market:
                query["market"] = market
            
            cursor = self.db[self.collections['stocks']].find(
                query, {"_id": 0}
            ).skip(offset).limit(limit)
            
            stocks = await cursor.to_list(length=None)
            return stocks
            
        except Exception as e:
            logger.error(f"Failed to get stocks: {e}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 检查数据库连接
            await self.db.command("ping")
            
            # 获取集合统计信息
            stats = {}
            for name, collection in self.collections.items():
                count = await self.db[collection].count_documents({})
                stats[name] = count
            
            return {
                "status": "healthy",
                "collections": stats,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
