#!/usr/bin/env python3
"""
微服务集成测试
测试数据适配器的微服务调用和本地降级功能
"""

import os
import sys
import asyncio
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 加载环境变量
def load_env():
    """加载.env文件中的环境变量"""
    env_file = os.path.join(project_root, '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print("✅ 已加载.env文件")
    else:
        print("⚠️ 未找到.env文件")

# 在导入其他模块前加载环境变量
load_env()

from tradingagents.adapters.data_adapter import DataAdapter, DataMode
from tradingagents.clients.data_service_client import DataServiceClient
from tradingagents.config.service_config import get_service_config

async def test_service_config():
    """测试服务配置"""
    print("🔧 测试服务配置")
    print("=" * 50)
    
    try:
        config = get_service_config()
        
        print(f"   🌍 环境: {config.environment.value}")
        
        # 测试数据服务配置
        data_service = config.get_service_endpoint("data_service")
        if data_service:
            print(f"   🌐 数据服务URL: {data_service.url}")
            print(f"   ⏱️ 超时时间: {data_service.timeout}秒")
            print(f"   🔄 最大重试: {data_service.max_retries}次")
        
        # 测试数据库配置
        mongodb_config = config.get_database_config("mongodb")
        if mongodb_config:
            print(f"   🗄️ MongoDB: {mongodb_config.host}:{mongodb_config.port}")
            print(f"   📊 数据库: {mongodb_config.database}")
            print(f"   ✅ 启用状态: {mongodb_config.enabled}")
        
        # 测试缓存配置
        redis_config = config.get_cache_config("redis")
        if redis_config:
            print(f"   🗄️ Redis: {redis_config.host}:{redis_config.port}")
            print(f"   📊 数据库: {redis_config.db}")
            print(f"   ✅ 启用状态: {redis_config.enabled}")
        
        # 测试功能开关
        print(f"   🔧 微服务启用: {config.is_feature_enabled('enable_microservices')}")
        print(f"   💾 缓存启用: {config.is_feature_enabled('enable_caching')}")
        print(f"   🔄 自动降级: {config.is_feature_enabled('auto_fallback')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return False

async def test_data_service_client():
    """测试数据服务客户端"""
    print("\n📡 测试数据服务客户端")
    print("=" * 50)
    
    try:
        async with DataServiceClient() as client:
            # 测试健康检查
            print("🏥 测试健康检查:")
            health = await client.health_check()
            print(f"   状态: {health.get('status', 'unknown')}")
            
            if health.get('status') == 'healthy':
                # 测试获取股票列表
                print("\n📈 测试获取股票列表:")
                stocks = await client.get_stocks(limit=3)
                print(f"   获取到 {len(stocks)} 只股票")
                for stock in stocks:
                    print(f"   - {stock.get('code', 'N/A')}: {stock.get('name', 'N/A')}")
                
                # 测试获取历史数据
                print("\n📊 测试获取历史数据:")
                if stocks:
                    test_stock = stocks[0]['code']
                    hist_data = await client.get_historical_data(test_stock)
                    print(f"   {test_stock} 历史数据: {len(hist_data)} 条")
                    if hist_data:
                        print(f"   最新数据: {hist_data[-1]}")
                
                # 测试获取基本面数据
                print("\n💰 测试获取基本面数据:")
                if stocks:
                    test_stock = stocks[0]['code']
                    fund_data = await client.get_fundamental_data(test_stock)
                    if fund_data:
                        print(f"   {test_stock} 基本面数据: {fund_data}")
                    else:
                        print(f"   {test_stock} 暂无基本面数据")
                
                # 测试获取实时数据
                print("\n⚡ 测试获取实时数据:")
                if stocks:
                    test_stock = stocks[0]['code']
                    realtime_data = await client.get_realtime_data(test_stock)
                    if realtime_data:
                        print(f"   {test_stock} 实时数据: {realtime_data}")
                    else:
                        print(f"   {test_stock} 暂无实时数据")
                
                return True
            else:
                print("   ⚠️ 数据服务不健康，跳过详细测试")
                return False
        
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return False

async def test_data_adapter_microservice_mode():
    """测试数据适配器微服务模式"""
    print("\n🔗 测试数据适配器微服务模式")
    print("=" * 50)
    
    try:
        adapter = DataAdapter(mode=DataMode.MICROSERVICE)
        await adapter.initialize()
        
        # 测试健康检查
        print("🏥 测试健康检查:")
        health = await adapter.health_check()
        print(f"   状态: {health.get('status', 'unknown')}")
        
        # 测试获取股票列表
        print("\n📈 测试获取股票列表:")
        stocks = await adapter.get_stocks(limit=3)
        print(f"   获取到 {len(stocks)} 只股票")
        
        # 测试获取历史数据
        print("\n📊 测试获取历史数据:")
        hist_data = await adapter.get_historical_data("600036")
        print(f"   600036 历史数据: {len(hist_data)} 条")
        
        # 测试获取基本面数据
        print("\n💰 测试获取基本面数据:")
        fund_data = await adapter.get_fundamental_data("600036")
        if fund_data:
            print(f"   600036 基本面数据: PE={fund_data.get('pe_ratio', 'N/A')}")
        
        await adapter.close()
        return True
        
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return False

async def test_data_adapter_local_mode():
    """测试数据适配器本地模式"""
    print("\n🏠 测试数据适配器本地模式")
    print("=" * 50)
    
    try:
        adapter = DataAdapter(mode=DataMode.LOCAL)
        await adapter.initialize()
        
        # 测试健康检查
        print("🏥 测试健康检查:")
        health = await adapter.health_check()
        print(f"   状态: {health.get('status', 'unknown')}")
        print(f"   模式: {health.get('mode', 'unknown')}")
        
        # 测试获取股票列表
        print("\n📈 测试获取股票列表:")
        stocks = await adapter.get_stocks(limit=3)
        print(f"   获取到 {len(stocks)} 只股票")
        for stock in stocks:
            print(f"   - {stock.get('code', 'N/A')}: {stock.get('name', 'N/A')}")
        
        # 测试获取历史数据
        print("\n📊 测试获取历史数据:")
        hist_data = await adapter.get_historical_data("600036")
        print(f"   600036 历史数据: {len(hist_data)} 条")
        if hist_data:
            print(f"   示例数据: {hist_data[0]}")
        
        # 测试获取基本面数据
        print("\n💰 测试获取基本面数据:")
        fund_data = await adapter.get_fundamental_data("600036")
        if fund_data:
            print(f"   600036 基本面数据: PE={fund_data.get('pe_ratio', 'N/A')}")
        
        await adapter.close()
        return True
        
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return False

async def test_data_adapter_auto_mode():
    """测试数据适配器自动模式"""
    print("\n🤖 测试数据适配器自动模式")
    print("=" * 50)
    
    try:
        adapter = DataAdapter(mode=DataMode.AUTO)
        await adapter.initialize()
        
        print(f"   🔍 服务可用性: {adapter._service_available}")
        print(f"   📡 使用微服务: {adapter._should_use_microservice()}")
        
        # 测试健康检查
        print("\n🏥 测试健康检查:")
        health = await adapter.health_check()
        print(f"   状态: {health.get('status', 'unknown')}")
        
        # 测试获取股票列表
        print("\n📈 测试获取股票列表:")
        stocks = await adapter.get_stocks(limit=3)
        print(f"   获取到 {len(stocks)} 只股票")
        
        # 测试获取历史数据
        print("\n📊 测试获取历史数据:")
        hist_data = await adapter.get_historical_data("600036")
        print(f"   600036 历史数据: {len(hist_data)} 条")
        
        # 测试获取基本面数据
        print("\n💰 测试获取基本面数据:")
        fund_data = await adapter.get_fundamental_data("600036")
        if fund_data:
            print(f"   600036 基本面数据: PE={fund_data.get('pe_ratio', 'N/A')}")
        
        # 测试降级机制
        print("\n🔄 测试降级机制:")
        if adapter._service_available:
            print("   微服务可用，测试手动降级...")
            adapter._service_available = False
            
            # 再次测试数据获取
            stocks_fallback = await adapter.get_stocks(limit=2)
            print(f"   降级后获取股票: {len(stocks_fallback)} 只")
        else:
            print("   微服务不可用，已自动降级到本地模式")
        
        await adapter.close()
        return True
        
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return False

async def test_convenience_functions():
    """测试便捷函数"""
    print("\n🛠️ 测试便捷函数")
    print("=" * 50)
    
    try:
        from tradingagents.adapters.data_adapter import get_stock_data, get_stock_fundamentals, get_stock_realtime
        
        # 测试获取历史数据
        print("📊 测试get_stock_data:")
        hist_data = await get_stock_data("600036")
        print(f"   600036 历史数据: {len(hist_data)} 条")
        
        # 测试获取基本面数据
        print("\n💰 测试get_stock_fundamentals:")
        fund_data = await get_stock_fundamentals("600036")
        if fund_data:
            print(f"   600036 基本面数据: PE={fund_data.get('pe_ratio', 'N/A')}")
        
        # 测试获取实时数据
        print("\n⚡ 测试get_stock_realtime:")
        realtime_data = await get_stock_realtime("600036")
        if realtime_data:
            print(f"   600036 实时数据: 价格={realtime_data.get('price', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🚀 微服务集成测试")
    print("=" * 80)
    
    test_functions = [
        ("服务配置", test_service_config),
        ("数据服务客户端", test_data_service_client),
        ("数据适配器微服务模式", test_data_adapter_microservice_mode),
        ("数据适配器本地模式", test_data_adapter_local_mode),
        ("数据适配器自动模式", test_data_adapter_auto_mode),
        ("便捷函数", test_convenience_functions)
    ]
    
    results = []
    
    for test_name, test_func in test_functions:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    # 总结结果
    print("\n" + "=" * 80)
    print("📋 微服务集成测试结果总结")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n📊 总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 微服务集成测试全部通过！")
        print("\n🎯 验证功能:")
        print("✅ 服务配置管理正常")
        print("✅ 微服务客户端可用")
        print("✅ 数据适配器多模式支持")
        print("✅ 自动降级机制正常")
        print("✅ 便捷函数接口可用")
        
        print("\n🔧 架构特性:")
        print("🌐 微服务模式: 通过HTTP API调用数据服务")
        print("🏠 本地模式: 直接调用本地数据源管理器")
        print("🤖 自动模式: 智能选择微服务或本地模式")
        print("🔄 降级机制: 微服务不可用时自动切换到本地")
        print("⚡ 客户端缓存: 减少重复请求，提升性能")
        
    elif passed >= total * 0.8:
        print("✅ 微服务集成测试基本通过！")
        print(f"⚠️ {total - passed} 个功能需要进一步检查")
    else:
        print("⚠️ 微服务集成测试失败较多，需要检查配置")
    
    return passed >= total * 0.8

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
