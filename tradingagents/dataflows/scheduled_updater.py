#!/usr/bin/env python3
"""
定时数据更新系统
支持历史数据、基本面数据的定时更新和增量同步
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from ..utils.logging_manager import get_logger
from .data_source_manager import DataSourceManager
from ..config.mongodb_storage import MongoDBStorage
from .cache_manager import CacheManager

logger = get_logger(__name__)

class ScheduledDataUpdater:
    """定时数据更新器"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.mongodb = MongoDBStorage()
        self.data_sources = DataSourceManager()
        self.cache = CacheManager()
        self.is_running = False
        
        # 更新统计
        self.update_stats = {
            "last_historical_update": None,
            "last_fundamental_update": None,
            "last_company_update": None,
            "total_updates": 0,
            "failed_updates": 0
        }
    
    async def initialize(self):
        """初始化定时任务"""
        try:
            await self.mongodb.initialize()
            await self.setup_scheduled_tasks()
            logger.info("ScheduledDataUpdater initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ScheduledDataUpdater: {e}")
            raise
    
    async def setup_scheduled_tasks(self):
        """设置定时任务"""
        
        # 每日历史数据更新 (交易日收盘后)
        self.scheduler.add_job(
            func=self.update_historical_data,
            trigger=CronTrigger(hour=18, minute=0),  # 每天18:00
            id='daily_historical_update',
            name='Daily Historical Data Update',
            max_instances=1,
            coalesce=True
        )
        
        # 每周基本面数据更新
        self.scheduler.add_job(
            func=self.update_fundamental_data,
            trigger=CronTrigger(day_of_week='sun', hour=2, minute=0),  # 每周日2:00
            id='weekly_fundamental_update',
            name='Weekly Fundamental Data Update',
            max_instances=1,
            coalesce=True
        )
        
        # 每月公司信息更新
        self.scheduler.add_job(
            func=self.update_company_info,
            trigger=CronTrigger(day=1, hour=3, minute=0),  # 每月1号3:00
            id='monthly_company_update',
            name='Monthly Company Info Update',
            max_instances=1,
            coalesce=True
        )
        
        # 实时数据缓存刷新 (交易时间内每5分钟)
        self.scheduler.add_job(
            func=self.refresh_realtime_cache,
            trigger=CronTrigger(
                day_of_week='mon-fri',
                hour='9-15',
                minute='*/5'
            ),
            id='realtime_cache_refresh',
            name='Realtime Cache Refresh',
            max_instances=1
        )
        
        logger.info("Scheduled tasks configured successfully")
    
    async def start(self):
        """启动定时任务调度器"""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            logger.info("ScheduledDataUpdater started")
    
    async def stop(self):
        """停止定时任务调度器"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("ScheduledDataUpdater stopped")
    
    async def update_historical_data(self):
        """更新历史数据"""
        logger.info("Starting historical data update")
        start_time = datetime.now()
        
        try:
            # 获取活跃股票列表
            stock_list = await self.mongodb.get_active_stocks()
            logger.info(f"Found {len(stock_list)} active stocks to update")
            
            success_count = 0
            failed_count = 0
            
            for stock in stock_list:
                try:
                    await self._update_single_stock_historical(stock)
                    success_count += 1
                    
                    # 避免API限制，添加延迟
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"Failed to update historical data for {stock['code']}: {e}")
                    failed_count += 1
            
            # 更新统计信息
            self.update_stats["last_historical_update"] = datetime.now()
            self.update_stats["total_updates"] += success_count
            self.update_stats["failed_updates"] += failed_count
            
            duration = datetime.now() - start_time
            logger.info(
                f"Historical data update completed: "
                f"{success_count} success, {failed_count} failed, "
                f"duration: {duration.total_seconds():.2f}s"
            )
            
        except Exception as e:
            logger.error(f"Historical data update failed: {e}")
            raise
    
    async def _update_single_stock_historical(self, stock: Dict[str, Any]):
        """更新单只股票的历史数据"""
        stock_code = stock['code']
        market = stock.get('market', 'cn')
        
        # 获取最新数据日期
        last_date = await self.mongodb.get_last_data_date(stock_code)
        
        # 如果没有历史数据，从30天前开始
        if not last_date:
            start_date = datetime.now() - timedelta(days=30)
        else:
            start_date = last_date + timedelta(days=1)
        
        # 如果已经是最新数据，跳过
        if start_date.date() >= datetime.now().date():
            return
        
        # 获取新数据
        new_data = await self.data_sources.fetch_historical_data(
            stock_code=stock_code,
            market=market,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=datetime.now().strftime('%Y-%m-%d')
        )
        
        if new_data and len(new_data) > 0:
            # 保存到MongoDB
            await self.mongodb.save_historical_data(stock_code, new_data)
            
            # 清除相关缓存
            await self.cache.delete_pattern(f"historical:{stock_code}:*")
            
            logger.debug(f"Updated {len(new_data)} records for {stock_code}")
    
    async def update_fundamental_data(self):
        """更新基本面数据"""
        logger.info("Starting fundamental data update")
        start_time = datetime.now()
        
        try:
            stock_list = await self.mongodb.get_active_stocks()
            success_count = 0
            failed_count = 0
            
            for stock in stock_list:
                try:
                    await self._update_single_stock_fundamental(stock)
                    success_count += 1
                    await asyncio.sleep(0.2)  # 基本面数据更新间隔稍长
                    
                except Exception as e:
                    logger.error(f"Failed to update fundamental data for {stock['code']}: {e}")
                    failed_count += 1
            
            self.update_stats["last_fundamental_update"] = datetime.now()
            duration = datetime.now() - start_time
            
            logger.info(
                f"Fundamental data update completed: "
                f"{success_count} success, {failed_count} failed, "
                f"duration: {duration.total_seconds():.2f}s"
            )
            
        except Exception as e:
            logger.error(f"Fundamental data update failed: {e}")
            raise
    
    async def _update_single_stock_fundamental(self, stock: Dict[str, Any]):
        """更新单只股票的基本面数据"""
        stock_code = stock['code']
        market = stock.get('market', 'cn')
        
        # 获取基本面数据
        fundamental_data = await self.data_sources.fetch_fundamental_data(
            stock_code=stock_code,
            market=market
        )
        
        if fundamental_data:
            # 保存到MongoDB
            await self.mongodb.save_fundamental_data(stock_code, fundamental_data)
            
            # 清除相关缓存
            await self.cache.delete_pattern(f"fundamental:{stock_code}:*")
            
            logger.debug(f"Updated fundamental data for {stock_code}")
    
    async def update_company_info(self):
        """更新公司信息"""
        logger.info("Starting company info update")
        
        try:
            stock_list = await self.mongodb.get_active_stocks()
            
            for stock in stock_list:
                try:
                    company_info = await self.data_sources.fetch_company_info(
                        stock_code=stock['code'],
                        market=stock.get('market', 'cn')
                    )
                    
                    if company_info:
                        await self.mongodb.save_company_info(stock['code'], company_info)
                        await asyncio.sleep(0.1)
                        
                except Exception as e:
                    logger.error(f"Failed to update company info for {stock['code']}: {e}")
            
            self.update_stats["last_company_update"] = datetime.now()
            logger.info("Company info update completed")
            
        except Exception as e:
            logger.error(f"Company info update failed: {e}")
            raise
    
    async def refresh_realtime_cache(self):
        """刷新实时数据缓存"""
        try:
            # 获取热门股票列表
            hot_stocks = await self.mongodb.get_hot_stocks(limit=50)
            
            for stock in hot_stocks:
                try:
                    # 预加载实时数据到缓存
                    realtime_data = await self.data_sources.fetch_realtime_data(
                        stock_code=stock['code'],
                        market=stock.get('market', 'cn')
                    )
                    
                    if realtime_data:
                        cache_key = f"realtime:{stock['code']}"
                        await self.cache.set(cache_key, realtime_data, ttl=300)  # 5分钟缓存
                        
                except Exception as e:
                    logger.debug(f"Failed to refresh cache for {stock['code']}: {e}")
            
            logger.debug(f"Refreshed realtime cache for {len(hot_stocks)} stocks")
            
        except Exception as e:
            logger.error(f"Realtime cache refresh failed: {e}")
    
    async def trigger_manual_update(self, update_type: str, stock_codes: Optional[List[str]] = None):
        """手动触发数据更新"""
        logger.info(f"Manual {update_type} update triggered")
        
        if update_type == "historical":
            if stock_codes:
                for code in stock_codes:
                    stock = {"code": code, "market": "cn"}  # 简化处理
                    await self._update_single_stock_historical(stock)
            else:
                await self.update_historical_data()
                
        elif update_type == "fundamental":
            if stock_codes:
                for code in stock_codes:
                    stock = {"code": code, "market": "cn"}
                    await self._update_single_stock_fundamental(stock)
            else:
                await self.update_fundamental_data()
                
        elif update_type == "company":
            await self.update_company_info()
            
        else:
            raise ValueError(f"Unknown update type: {update_type}")
    
    def get_update_status(self) -> Dict[str, Any]:
        """获取更新状态"""
        return {
            "is_running": self.is_running,
            "stats": self.update_stats.copy(),
            "next_runs": {
                job.id: job.next_run_time.isoformat() if job.next_run_time else None
                for job in self.scheduler.get_jobs()
            }
        }

# 全局实例
scheduled_updater = ScheduledDataUpdater()
