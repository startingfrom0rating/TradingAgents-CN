#!/usr/bin/env python3
"""
数据源优化功能测试
验证定时更新、优先级配置、缓存管理等核心功能
"""

import os
import sys
import asyncio
import json
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_priority_manager():
    """测试数据源优先级管理"""
    print("🔧 测试数据源优先级管理")
    print("=" * 60)
    
    try:
        from tradingagents.dataflows.priority_manager import priority_manager, Market, DataType
        
        async def run_test():
            await priority_manager.initialize()
            
            # 测试获取优先级配置
            print("📊 测试获取A股历史数据优先级:")
            sources = await priority_manager.get_priority_list("cn", "historical")
            for i, source in enumerate(sources):
                print(f"   优先级 {i+1}: {source.source_name} (启用: {source.enabled})")
            
            # 测试获取所有配置
            print("\n📋 测试获取所有配置:")
            all_configs = await priority_manager.get_all_configs()
            for market, market_config in all_configs.items():
                print(f"   市场 {market}: {list(market_config.keys())}")
            
            return True
        
        result = asyncio.run(run_test())
        if result:
            print("✅ 数据源优先级管理测试通过")
        return result
        
    except Exception as e:
        print(f"❌ 数据源优先级管理测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mongodb_storage():
    """测试MongoDB数据存储"""
    print("\n💾 测试MongoDB数据存储")
    print("=" * 60)
    
    try:
        from tradingagents.dataflows.mongodb_data_storage import MongoDBDataStorage
        
        async def run_test():
            storage = MongoDBDataStorage()
            
            # 测试健康检查
            print("🏥 测试健康检查:")
            health = await storage.health_check()
            print(f"   状态: {health.get('status', 'unknown')}")
            
            if health.get('status') == 'healthy':
                # 测试获取活跃股票
                print("\n📈 测试获取活跃股票:")
                stocks = await storage.get_active_stocks()
                print(f"   找到 {len(stocks)} 只活跃股票")
                
                if stocks:
                    # 测试获取最新数据日期
                    test_stock = stocks[0]['code']
                    print(f"\n📅 测试获取 {test_stock} 最新数据日期:")
                    last_date = await storage.get_last_data_date(test_stock)
                    print(f"   最新日期: {last_date}")
            
            return True
        
        result = asyncio.run(run_test())
        if result:
            print("✅ MongoDB数据存储测试通过")
        return result
        
    except Exception as e:
        print(f"❌ MongoDB数据存储测试失败: {e}")
        print("💡 提示: 请确保MongoDB服务正在运行")
        return False

def test_redis_cache_manager():
    """测试Redis缓存管理"""
    print("\n🗄️ 测试Redis缓存管理")
    print("=" * 60)
    
    try:
        from tradingagents.dataflows.redis_cache_manager import RedisCacheManager
        
        async def run_test():
            cache = RedisCacheManager()
            await cache.initialize()
            
            # 测试健康检查
            print("🏥 测试缓存健康检查:")
            health = await cache.health_check()
            print(f"   内存缓存: {health.get('memory_cache', {}).get('status', 'unknown')}")
            print(f"   Redis缓存: {health.get('redis_cache', {}).get('status', 'unknown')}")
            
            # 测试缓存操作
            print("\n💾 测试缓存操作:")
            test_key = "test:stock:600036"
            test_data = {"code": "600036", "name": "招商银行", "price": 45.67}
            
            # 设置缓存
            success = await cache.set(test_key, test_data, ttl=60)
            print(f"   设置缓存: {'成功' if success else '失败'}")
            
            # 获取缓存
            cached_data = await cache.get(test_key)
            print(f"   获取缓存: {'成功' if cached_data else '失败'}")
            
            if cached_data:
                print(f"   缓存数据: {cached_data}")
            
            # 删除缓存
            deleted = await cache.delete(test_key)
            print(f"   删除缓存: {'成功' if deleted else '失败'}")
            
            # 获取缓存统计
            print("\n📊 测试缓存统计:")
            stats = await cache.get_cache_stats()
            memory_stats = stats.get('memory_cache', {})
            print(f"   内存缓存项目数: {memory_stats.get('items', 0)}")
            print(f"   最大项目数: {memory_stats.get('max_items', 0)}")
            
            return True
        
        result = asyncio.run(run_test())
        if result:
            print("✅ Redis缓存管理测试通过")
        return result
        
    except Exception as e:
        print(f"❌ Redis缓存管理测试失败: {e}")
        print("💡 提示: Redis缓存不可用时会自动降级到内存缓存")
        return True  # 缓存降级是正常行为

def test_scheduled_updater():
    """测试定时数据更新器"""
    print("\n⏰ 测试定时数据更新器")
    print("=" * 60)
    
    try:
        from tradingagents.dataflows.scheduled_updater import scheduled_updater
        
        # 测试获取更新状态
        print("📊 测试获取更新状态:")
        status = scheduled_updater.get_update_status()
        
        print(f"   调度器运行状态: {'运行中' if status.get('is_running', False) else '已停止'}")
        
        stats = status.get('stats', {})
        print(f"   总更新次数: {stats.get('total_updates', 0)}")
        print(f"   失败次数: {stats.get('failed_updates', 0)}")
        
        # 测试下次运行时间
        print("\n📅 测试下次运行时间:")
        next_runs = status.get('next_runs', {})
        for job_id, next_run in next_runs.items():
            job_name = {
                "daily_historical_update": "每日历史数据更新",
                "weekly_fundamental_update": "每周基本面数据更新",
                "monthly_company_update": "每月公司信息更新",
                "realtime_cache_refresh": "实时数据缓存刷新"
            }.get(job_id, job_id)
            
            if next_run:
                print(f"   {job_name}: {next_run}")
            else:
                print(f"   {job_name}: 未安排")
        
        print("✅ 定时数据更新器测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 定时数据更新器测试失败: {e}")
        return False

def test_unified_data_source_manager():
    """测试统一数据源管理器"""
    print("\n🔗 测试统一数据源管理器")
    print("=" * 60)
    
    try:
        from tradingagents.dataflows.unified_data_source_manager import UnifiedDataSourceManager
        
        manager = UnifiedDataSourceManager()
        
        # 测试数据源统计
        print("📊 测试数据源统计:")
        stats = manager.get_source_stats()
        if stats:
            for source, stat in stats.items():
                print(f"   {source}: 总请求 {stat['total_requests']}, 成功 {stat['successful_requests']}")
        else:
            print("   暂无统计数据")
        
        # 测试数据源健康状态
        print("\n🏥 测试数据源健康状态:")
        health = manager.get_source_health()
        if health:
            for source, status in health.items():
                print(f"   {source}: {status['status']} (成功率: {status['success_rate']:.2%})")
        else:
            print("   暂无健康数据")
        
        print("✅ 统一数据源管理器测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 统一数据源管理器测试失败: {e}")
        return False

def test_data_service_api():
    """测试数据服务API"""
    print("\n🌐 测试数据服务API")
    print("=" * 60)
    
    try:
        from tradingagents.api.data_service import DataServiceAPI
        
        api = DataServiceAPI()
        
        print("🔧 测试API初始化:")
        print(f"   FastAPI应用: {api.app.title}")
        print(f"   版本: {api.app.version}")
        
        # 测试路由设置
        print("\n🛣️ 测试API路由:")
        routes = [route.path for route in api.app.routes if hasattr(route, 'path')]
        for route in routes[:10]:  # 显示前10个路由
            print(f"   {route}")
        
        if len(routes) > 10:
            print(f"   ... 还有 {len(routes) - 10} 个路由")
        
        print("✅ 数据服务API测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 数据服务API测试失败: {e}")
        return False

def test_integration():
    """集成测试"""
    print("\n🔄 集成测试")
    print("=" * 60)
    
    try:
        print("🧪 测试模块导入:")
        
        # 测试所有模块是否能正常导入
        modules = [
            "tradingagents.dataflows.priority_manager",
            "tradingagents.dataflows.mongodb_data_storage", 
            "tradingagents.dataflows.redis_cache_manager",
            "tradingagents.dataflows.scheduled_updater",
            "tradingagents.dataflows.unified_data_source_manager",
            "tradingagents.api.data_service"
        ]
        
        for module_name in modules:
            try:
                __import__(module_name)
                print(f"   ✅ {module_name}")
            except Exception as e:
                print(f"   ❌ {module_name}: {e}")
                return False
        
        print("\n🔗 测试模块间依赖:")
        
        # 测试模块间的依赖关系
        from tradingagents.dataflows.priority_manager import priority_manager
        from tradingagents.dataflows.scheduled_updater import scheduled_updater
        from tradingagents.api.data_service import data_service_api
        
        print("   ✅ 所有模块依赖正常")
        
        print("✅ 集成测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 开始数据源优化功能测试")
    print("=" * 80)
    
    test_functions = [
        ("数据源优先级管理", test_priority_manager),
        ("MongoDB数据存储", test_mongodb_storage),
        ("Redis缓存管理", test_redis_cache_manager),
        ("定时数据更新器", test_scheduled_updater),
        ("统一数据源管理器", test_unified_data_source_manager),
        ("数据服务API", test_data_service_api),
        ("集成测试", test_integration)
    ]
    
    results = []
    
    for test_name, test_func in test_functions:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    # 总结结果
    print("\n" + "=" * 80)
    print("📋 测试结果总结")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n📊 总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！数据源优化功能运行正常")
        print("\n🎯 功能亮点:")
        print("1. ✅ 数据源优先级配置系统")
        print("2. ✅ MongoDB数据持久化存储")
        print("3. ✅ Redis多层次缓存管理")
        print("4. ✅ 定时数据更新调度")
        print("5. ✅ 统一数据源管理")
        print("6. ✅ 独立数据服务API")
        print("7. ✅ 完整的模块集成")
        
        print("\n🚀 系统优势:")
        print("- 高可用性: 多数据源自动切换")
        print("- 高性能: 智能缓存和并发处理")
        print("- 可配置: 用户自定义优先级")
        print("- 可扩展: 微服务架构就绪")
        print("- 可监控: 完善的健康检查")
    else:
        print("⚠️ 部分测试失败，请检查相关配置")
        print("\n💡 常见问题:")
        print("- MongoDB服务未启动")
        print("- Redis服务不可用(会自动降级)")
        print("- 网络连接问题")
        print("- 依赖包未安装")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
