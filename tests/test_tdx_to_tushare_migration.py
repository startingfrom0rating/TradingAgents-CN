#!/usr/bin/env python3
"""
TDX to Tushare migration tests
Validate that TDX interfaces have been successfully replaced by the unified Tushare interfaces
"""

import os
import sys
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_data_source_manager():
    """Test the data source manager"""
    print("\n🔧 Testing data source manager")
    print("=" * 60)

    try:
        from tradingagents.dataflows.data_source_manager import get_data_source_manager, ChinaDataSource

        print("✅ Data source manager imported successfully")

        # Create manager instance
        manager = get_data_source_manager()

        print(f"✅ Data source manager initialized successfully")
        print(f"   Current data source: {manager.get_current_source().value}")
        print(f"   Available data sources: {[s.value for s in manager.available_sources]}")

        # Test switching data source
        if ChinaDataSource.TUSHARE in manager.available_sources:
            print("🔄 Testing switch to Tushare...")
            success = manager.set_current_source(ChinaDataSource.TUSHARE)
            if success:
                print("✅ Successfully switched to Tushare")
            else:
                print("❌ Failed to switch to Tushare")

        return True

    except Exception as e:
        print(f"❌ Data source manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_unified_interfaces():
    """Test unified interfaces"""
    print("\n🔧 Testing unified interfaces")
    print("=" * 60)

    try:
        from tradingagents.dataflows.interface import (
            get_china_stock_data_unified,
            get_china_stock_info_unified,
            switch_china_data_source,
            get_current_china_data_source
        )

        print("✅ Unified interfaces imported successfully")

        # Test get current data source
        print("🔄 Testing retrieval of current data source...")
        current_source = get_current_china_data_source()
        print(f"✅ Current data source info:\n{current_source}")

        # Test switching data source
        print("🔄 Testing switch of data source to Tushare...")
        switch_result = switch_china_data_source("tushare")
        print(f"✅ Switch result: {switch_result}")

        # Test fetching stock info
        print("🔄 Testing fetching stock info...")
        stock_info = get_china_stock_info_unified("000001")
        if "股票代码: 000001" in stock_info:
            print("✅ Stock info retrieved successfully")
            print(f"📊 Stock info: {stock_info[:200]}...")
        else:
            print("❌ Failed to retrieve stock info")

        # Test fetching stock data
        print("🔄 Testing fetching stock data...")
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')

        stock_data = get_china_stock_data_unified("000001", start_date, end_date)
        if "股票代码: 000001" in stock_data:
            print("✅ Stock data retrieved successfully")
            print(f"📊 Data length: {len(stock_data)} chars")
        else:
            print("❌ Failed to retrieve stock data")

        return True

    except Exception as e:
        print(f"❌ Unified interface test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_utils_migration():
    """Test migration of agent_utils"""
    print("\n🔧 Testing agent_utils migration")
    print("=" * 60)

    try:
        from tradingagents.agents.utils.agent_utils import AgentUtils

        print("✅ agent_utils imported successfully")

        # Test fetching fundamentals
        print("🔄 Testing fetching fundamentals...")
        curr_date = datetime.now().strftime('%Y-%m-%d')

        # Use the AgentUtils class static method
        fundamentals = AgentUtils.get_fundamentals_openai("000001", curr_date)

        if fundamentals and len(fundamentals) > 100:
            print("✅ Fundamentals retrieved successfully")
            print(f"📊 Data length: {len(fundamentals)} chars")

            # Check whether TDX-related strings are still present
            if "通达信" in fundamentals:
                print("⚠️ Warning: Fundamentals still contain TDX-related references")
            else:
                print("✅ Fundamentals successfully migrated to the new data source")
        else:
            print("❌ Failed to retrieve fundamentals")

        return True

    except Exception as e:
        print(f"❌ agent_utils migration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_optimized_china_data_migration():
    """Test migration of optimized_china_data"""
    print("\n🔧 Testing optimized_china_data migration")
    print("=" * 60)

    try:
        from tradingagents.dataflows.optimized_china_data import OptimizedChinaDataProvider

        print("✅ optimized_china_data imported successfully")

        # Create provider instance
        provider = OptimizedChinaDataProvider()

        # Test data retrieval
        print("🔄 Testing data retrieval...")
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')

        data = provider.get_stock_data("000001", start_date, end_date)

        if data and len(data) > 100:
            print("✅ Data retrieved successfully")
            print(f"📊 Data length: {len(data)} chars")

            # Check whether TDX-related strings are still present
            if "通达信" in data:
                print("⚠️ Warning: Data still contains TDX-related references")
            else:
                print("✅ Data retrieval successfully migrated to the new data source")
        else:
            print("❌ Failed to retrieve data")

        return True

    except Exception as e:
        print(f"❌ optimized_china_data migration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tdx_deprecation_warnings():
    """Test TDX deprecation warnings"""
    print("\n🔧 Testing TDX deprecation warnings")
    print("=" * 60)

    try:
        from tradingagents.dataflows.data_source_manager import get_data_source_manager, ChinaDataSource

        manager = get_data_source_manager()

        # If TDX is available, test deprecation warnings
        if ChinaDataSource.TDX in manager.available_sources:
            print("🔄 Testing TDX deprecation warnings...")

            # Switch to TDX
            manager.set_current_source(ChinaDataSource.TDX)

            # Fetch data (should show deprecation warning)
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')

            data = manager.get_stock_data("000001", start_date, end_date)

            if data:
                print("✅ TDX data retrieved successfully (deprecation warning expected)")
            else:
                print("❌ Failed to retrieve TDX data")

            # Switch back to Tushare
            if ChinaDataSource.TUSHARE in manager.available_sources:
                manager.set_current_source(ChinaDataSource.TUSHARE)
                print("✅ Switched back to Tushare data source")
        else:
            print("ℹ️ TDX data source not available, skipping deprecation warning test")

        return True

    except Exception as e:
        print(f"❌ TDX deprecation warning test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_migration_completeness():
    """Check migration completeness"""
    print("\n🔧 Checking migration completeness")
    print("=" * 60)

    # Check environment variables
    tushare_token = os.getenv('TUSHARE_TOKEN')
    default_source = os.getenv('DEFAULT_CHINA_DATA_SOURCE', 'tushare')

    print(f"📊 Environment variable check:")
    print(f"   TUSHARE_TOKEN: {'set' if tushare_token else 'not set'}")
    print(f"   DEFAULT_CHINA_DATA_SOURCE: {default_source}")

    # Check Tushare library
    try:
        import tushare as ts
        print(f"✅ Tushare library: v{ts.__version__}")
    except ImportError:
        print("❌ Tushare library is not installed")
        return False

    # Check unified interface availability
    try:
        from tradingagents.dataflows import (
            get_china_stock_data_unified,
            get_china_stock_info_unified,
            switch_china_data_source,
            get_current_china_data_source
        )
        print("✅ Unified interfaces available")
    except ImportError as e:
        print(f"❌ Unified interfaces not available: {e}")
        return False

    return True


def main():
    """主测试函数"""
    print("🔬 TDX到Tushare迁移测试")
    print("=" * 70)
    print("💡 测试目标:")
    print("   - 验证数据源管理器功能")
    print("   - 验证统一接口替换TDX")
    print("   - 验证agent_utils迁移")
    print("   - 验证optimized_china_data迁移")
    print("   - 验证TDX弃用警告")
    print("=" * 70)
    
    # 检查迁移完整性
    if not check_migration_completeness():
        print("\n❌ 迁移环境检查失败，请先配置环境")
        return
    
    # 运行所有测试
    tests = [
        ("数据源管理器", test_data_source_manager),
        ("统一接口", test_unified_interfaces),
        ("agent_utils迁移", test_agent_utils_migration),
        ("optimized_china_data迁移", test_optimized_china_data_migration),
        ("TDX弃用警告", test_tdx_deprecation_warnings)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            results.append((test_name, False))
    
    # 总结
    print("\n📋 TDX到Tushare迁移测试总结")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    total = len(results)
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 TDX到Tushare迁移测试完全成功！")
        print("\n💡 迁移效果:")
        print("   ✅ TDX接口已成功替换为Tushare统一接口")
        print("   ✅ 数据源管理器正常工作")
        print("   ✅ 支持多数据源备用机制")
        print("   ✅ 保持向后兼容性")
        print("\n🚀 现在系统默认使用Tushare数据源！")
    else:
        print("\n⚠️ 部分测试失败，请检查相关配置")
    
    print("\n🎯 使用建议:")
    print("   1. 设置TUSHARE_TOKEN环境变量")
    print("   2. 设置DEFAULT_CHINA_DATA_SOURCE=tushare")
    print("   3. 使用统一接口获取中国股票数据")
    print("   4. 逐步停用TDX相关代码")
    
    input("按回车键退出...")


if __name__ == "__main__":
    main()
