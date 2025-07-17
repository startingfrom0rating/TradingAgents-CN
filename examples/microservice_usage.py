#!/usr/bin/env python3
"""
微服务使用示例
展示如何在TradingAgents中使用数据源微服务
"""

import os
import sys
import asyncio
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 加载环境变量
def load_env():
    env_file = os.path.join(project_root, '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env()

from tradingagents.adapters.data_adapter import DataAdapter, DataMode, get_stock_data, get_stock_fundamentals
from tradingagents.clients.data_service_client import DataServiceClient
from tradingagents.config.service_config import get_service_config

async def example_1_basic_usage():
    """示例1: 基础使用 - 使用便捷函数"""
    print("📋 示例1: 基础使用")
    print("=" * 50)
    
    try:
        # 使用便捷函数获取数据，自动选择最佳模式
        print("📊 获取招商银行历史数据...")
        hist_data = await get_stock_data("600036")
        print(f"   获取到 {len(hist_data)} 条历史数据")
        
        if hist_data:
            latest = hist_data[-1]
            print(f"   最新数据: 日期={latest.get('date')}, 收盘价={latest.get('close')}")
        
        print("\n💰 获取招商银行基本面数据...")
        fund_data = await get_stock_fundamentals("600036")
        if fund_data:
            print(f"   PE比率: {fund_data.get('pe_ratio')}")
            print(f"   PB比率: {fund_data.get('pb_ratio')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 示例1失败: {e}")
        return False

async def example_2_explicit_microservice():
    """示例2: 显式使用微服务模式"""
    print("\n📋 示例2: 显式使用微服务模式")
    print("=" * 50)
    
    try:
        # 创建微服务模式的数据适配器
        adapter = DataAdapter(mode=DataMode.MICROSERVICE)
        await adapter.initialize()
        
        print("🌐 使用微服务模式获取数据...")
        
        # 获取股票列表
        stocks = await adapter.get_stocks(market="cn", limit=5)
        print(f"   A股列表: {len(stocks)} 只股票")
        
        for stock in stocks[:3]:
            code = stock.get('code')
            name = stock.get('name')
            print(f"   - {code}: {name}")
        
        # 获取特定股票的详细数据
        if stocks:
            test_stock = stocks[0]['code']
            print(f"\n📊 获取 {test_stock} 的详细数据...")
            
            # 历史数据
            hist_data = await adapter.get_historical_data(test_stock)
            print(f"   历史数据: {len(hist_data)} 条")
            
            # 基本面数据
            fund_data = await adapter.get_fundamental_data(test_stock)
            if fund_data:
                print(f"   基本面数据: PE={fund_data.get('pe_ratio')}")
            
            # 实时数据
            realtime_data = await adapter.get_realtime_data(test_stock)
            if realtime_data:
                print(f"   实时价格: {realtime_data.get('price')}")
        
        await adapter.close()
        return True
        
    except Exception as e:
        print(f"❌ 示例2失败: {e}")
        return False

async def example_3_local_fallback():
    """示例3: 本地降级模式"""
    print("\n📋 示例3: 本地降级模式")
    print("=" * 50)
    
    try:
        # 创建本地模式的数据适配器
        adapter = DataAdapter(mode=DataMode.LOCAL)
        await adapter.initialize()
        
        print("🏠 使用本地模式获取数据...")
        
        # 获取股票列表
        stocks = await adapter.get_stocks(limit=3)
        print(f"   股票列表: {len(stocks)} 只股票")
        
        # 获取历史数据
        hist_data = await adapter.get_historical_data("600036")
        print(f"   600036历史数据: {len(hist_data)} 条")
        
        # 获取基本面数据
        fund_data = await adapter.get_fundamental_data("600036")
        if fund_data:
            print(f"   600036基本面: PE={fund_data.get('pe_ratio')}")
        
        await adapter.close()
        return True
        
    except Exception as e:
        print(f"❌ 示例3失败: {e}")
        return False

async def example_4_auto_mode_with_fallback():
    """示例4: 自动模式与智能降级"""
    print("\n📋 示例4: 自动模式与智能降级")
    print("=" * 50)
    
    try:
        # 创建自动模式的数据适配器
        adapter = DataAdapter(mode=DataMode.AUTO)
        await adapter.initialize()
        
        print(f"🤖 自动模式初始化完成")
        print(f"   微服务可用: {adapter._service_available}")
        print(f"   当前使用: {'微服务' if adapter._should_use_microservice() else '本地模式'}")
        
        # 第一次获取数据
        print("\n📊 第一次获取数据...")
        stocks = await adapter.get_stocks(limit=3)
        print(f"   获取股票: {len(stocks)} 只")
        
        # 模拟微服务故障
        if adapter._service_available:
            print("\n🔧 模拟微服务故障...")
            adapter._service_available = False
            print(f"   强制降级到本地模式")
            
            # 再次获取数据，应该自动降级
            print("\n📊 降级后获取数据...")
            stocks_fallback = await adapter.get_stocks(limit=3)
            print(f"   降级获取股票: {len(stocks_fallback)} 只")
            print("   ✅ 自动降级机制正常工作")
        else:
            print("\n⚠️ 微服务本来就不可用，已在本地模式运行")
        
        await adapter.close()
        return True
        
    except Exception as e:
        print(f"❌ 示例4失败: {e}")
        return False

async def example_5_direct_client_usage():
    """示例5: 直接使用微服务客户端"""
    print("\n📋 示例5: 直接使用微服务客户端")
    print("=" * 50)
    
    try:
        # 直接使用微服务客户端
        async with DataServiceClient() as client:
            print("📡 直接使用微服务客户端...")
            
            # 健康检查
            health = await client.health_check()
            print(f"   服务状态: {health.get('status')}")
            
            if health.get('status') == 'healthy':
                # 获取股票列表
                stocks = await client.get_stocks(limit=3)
                print(f"   股票列表: {len(stocks)} 只")
                
                # 获取历史数据
                hist_data = await client.get_historical_data("600036")
                print(f"   历史数据: {len(hist_data)} 条")
                
                # 触发数据刷新
                refresh_result = await client.trigger_data_refresh("historical", ["600036"])
                print(f"   数据刷新: {'成功' if refresh_result else '失败'}")
                
                # 获取优先级配置
                priority_config = await client.get_priority_config()
                print(f"   优先级配置: {len(priority_config)} 个市场")
                
                # 获取调度器状态
                scheduler_status = await client.get_scheduler_status()
                print(f"   调度器状态: {scheduler_status.get('is_running', 'unknown')}")
            else:
                print("   ⚠️ 微服务不可用")
        
        return True
        
    except Exception as e:
        print(f"❌ 示例5失败: {e}")
        return False

async def example_6_configuration_management():
    """示例6: 配置管理"""
    print("\n📋 示例6: 配置管理")
    print("=" * 50)
    
    try:
        # 获取服务配置
        config = get_service_config()
        
        print(f"🔧 当前环境: {config.environment.value}")
        
        # 数据服务配置
        data_service = config.get_service_endpoint("data_service")
        if data_service:
            print(f"   数据服务URL: {data_service.url}")
            print(f"   超时时间: {data_service.timeout}秒")
        
        # 数据库配置
        mongodb_config = config.get_database_config("mongodb")
        if mongodb_config:
            print(f"   MongoDB: {mongodb_config.host}:{mongodb_config.port}")
            print(f"   数据库: {mongodb_config.database}")
            print(f"   启用状态: {mongodb_config.enabled}")
        
        # 功能开关
        print(f"   微服务启用: {config.is_feature_enabled('enable_microservices')}")
        print(f"   缓存启用: {config.is_feature_enabled('enable_caching')}")
        print(f"   自动降级: {config.is_feature_enabled('auto_fallback')}")
        
        # 连接字符串
        mongodb_url = config.get_mongodb_connection_string()
        if mongodb_url:
            print(f"   MongoDB连接: {mongodb_url[:50]}...")
        
        redis_url = config.get_redis_connection_string()
        if redis_url:
            print(f"   Redis连接: {redis_url[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 示例6失败: {e}")
        return False

async def example_7_batch_operations():
    """示例7: 批量操作"""
    print("\n📋 示例7: 批量操作")
    print("=" * 50)
    
    try:
        adapter = DataAdapter(mode=DataMode.AUTO)
        await adapter.initialize()
        
        # 批量获取多只股票的数据
        stock_codes = ["600036", "000001", "000002"]
        
        print(f"📊 批量获取 {len(stock_codes)} 只股票的数据...")
        
        # 并发获取历史数据
        tasks = [adapter.get_historical_data(code) for code in stock_codes]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, (code, result) in enumerate(zip(stock_codes, results)):
            if isinstance(result, Exception):
                print(f"   {code}: 获取失败 - {result}")
            else:
                print(f"   {code}: 获取到 {len(result)} 条历史数据")
        
        # 并发获取基本面数据
        print(f"\n💰 批量获取基本面数据...")
        tasks = [adapter.get_fundamental_data(code) for code in stock_codes]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, (code, result) in enumerate(zip(stock_codes, results)):
            if isinstance(result, Exception):
                print(f"   {code}: 获取失败 - {result}")
            elif result:
                print(f"   {code}: PE={result.get('pe_ratio', 'N/A')}")
            else:
                print(f"   {code}: 暂无基本面数据")
        
        await adapter.close()
        return True
        
    except Exception as e:
        print(f"❌ 示例7失败: {e}")
        return False

async def main():
    """主函数"""
    print("🚀 TradingAgents 微服务使用示例")
    print("=" * 80)
    
    examples = [
        ("基础使用", example_1_basic_usage),
        ("显式微服务模式", example_2_explicit_microservice),
        ("本地降级模式", example_3_local_fallback),
        ("自动模式与智能降级", example_4_auto_mode_with_fallback),
        ("直接客户端使用", example_5_direct_client_usage),
        ("配置管理", example_6_configuration_management),
        ("批量操作", example_7_batch_operations)
    ]
    
    results = []
    
    for example_name, example_func in examples:
        try:
            result = await example_func()
            results.append((example_name, result))
        except Exception as e:
            print(f"❌ {example_name} 异常: {e}")
            results.append((example_name, False))
    
    # 总结结果
    print("\n" + "=" * 80)
    print("📋 示例运行结果总结")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for example_name, result in results:
        status = "✅ 成功" if result else "❌ 失败"
        print(f"{example_name}: {status}")
    
    print(f"\n📊 总体结果: {passed}/{total} 示例成功")
    
    if passed >= total * 0.8:
        print("\n🎉 微服务使用示例运行成功！")
        print("\n💡 关键特性:")
        print("🔄 智能模式切换: 自动选择微服务或本地模式")
        print("🛡️ 故障降级: 微服务不可用时自动切换到本地")
        print("⚡ 高性能: 客户端缓存和并发处理")
        print("🔧 灵活配置: 支持多环境配置管理")
        print("📡 标准接口: 统一的数据访问接口")
        
        print("\n🎯 使用建议:")
        print("- 生产环境推荐使用AUTO模式，获得最佳可用性")
        print("- 开发环境可以使用LOCAL模式，简化部署")
        print("- 使用便捷函数可以简化代码，自动处理模式选择")
        print("- 批量操作时使用并发可以显著提升性能")
    else:
        print("⚠️ 部分示例失败，请检查微服务状态和配置")

if __name__ == "__main__":
    asyncio.run(main())
