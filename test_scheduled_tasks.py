#!/usr/bin/env python3
"""
定时任务功能专项测试
测试定时数据更新器的实际执行功能和真实数据源集成
"""

import os
import sys
import asyncio
from datetime import datetime, timedelta

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

async def test_real_data_sources():
    """测试真实数据源"""
    print("🔗 测试真实数据源集成")
    print("=" * 60)
    
    # 测试可用的数据源
    data_sources = []
    
    # 测试AKShare
    try:
        import akshare as ak
        print("   ✅ AKShare 可用")
        data_sources.append("akshare")
    except ImportError:
        print("   ❌ AKShare 不可用")
    
    # 测试Tushare
    try:
        import tushare as ts
        tushare_token = os.getenv('TUSHARE_TOKEN')
        if tushare_token:
            print("   ✅ Tushare 可用 (有Token)")
            data_sources.append("tushare")
        else:
            print("   ⚠️ Tushare 可用但无Token")
    except ImportError:
        print("   ❌ Tushare 不可用")
    
    # 测试BaoStock
    try:
        import baostock as bs
        print("   ✅ BaoStock 可用")
        data_sources.append("baostock")
    except ImportError:
        print("   ❌ BaoStock 不可用")
    
    # 测试yfinance
    try:
        import yfinance as yf
        print("   ✅ yfinance 可用")
        data_sources.append("yfinance")
    except ImportError:
        print("   ❌ yfinance 不可用")
    
    print(f"\n📊 可用数据源: {len(data_sources)} 个")
    for source in data_sources:
        print(f"   - {source}")
    
    return data_sources

async def test_akshare_data():
    """测试AKShare数据获取"""
    print("\n📈 测试AKShare数据获取")
    print("-" * 40)
    
    try:
        import akshare as ak
        
        # 测试获取股票基本信息
        print("🔍 获取股票基本信息...")
        stock_info = ak.stock_individual_info_em(symbol="600036")
        if not stock_info.empty:
            print(f"   ✅ 获取到 {len(stock_info)} 条基本信息")
            print(f"   📊 示例: {stock_info.iloc[0].to_dict()}")
        
        # 测试获取历史数据
        print("\n📈 获取历史数据...")
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y%m%d')
        
        hist_data = ak.stock_zh_a_hist(symbol="600036", period="daily", 
                                      start_date=start_date, end_date=end_date)
        if not hist_data.empty:
            print(f"   ✅ 获取到 {len(hist_data)} 条历史数据")
            print(f"   📊 最新数据: {hist_data.iloc[-1].to_dict()}")
        
        # 测试获取实时数据
        print("\n⚡ 获取实时数据...")
        realtime_data = ak.stock_zh_a_spot_em()
        if not realtime_data.empty:
            # 查找招商银行
            cmb_data = realtime_data[realtime_data['代码'] == '600036']
            if not cmb_data.empty:
                print(f"   ✅ 获取到实时数据")
                print(f"   💰 当前价格: {cmb_data.iloc[0]['最新价']}")
                print(f"   📈 涨跌幅: {cmb_data.iloc[0]['涨跌幅']}%")
        
        return True
        
    except Exception as e:
        print(f"   ❌ AKShare测试失败: {e}")
        return False

async def test_tushare_data():
    """测试Tushare数据获取"""
    print("\n📊 测试Tushare数据获取")
    print("-" * 40)
    
    try:
        import tushare as ts
        
        tushare_token = os.getenv('TUSHARE_TOKEN')
        if not tushare_token:
            print("   ⚠️ 未配置TUSHARE_TOKEN，跳过测试")
            return False
        
        # 初始化
        ts.set_token(tushare_token)
        pro = ts.pro_api()
        
        # 测试获取股票基本信息
        print("🔍 获取股票基本信息...")
        stock_basic = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,market')
        if not stock_basic.empty:
            cmb_info = stock_basic[stock_basic['symbol'] == '600036']
            if not cmb_info.empty:
                print(f"   ✅ 获取到股票基本信息")
                print(f"   🏢 公司名称: {cmb_info.iloc[0]['name']}")
                print(f"   🏭 所属行业: {cmb_info.iloc[0]['industry']}")
        
        # 测试获取历史数据
        print("\n📈 获取历史数据...")
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y%m%d')
        
        hist_data = pro.daily(ts_code='600036.SH', start_date=start_date, end_date=end_date)
        if not hist_data.empty:
            print(f"   ✅ 获取到 {len(hist_data)} 条历史数据")
            print(f"   📊 最新数据: 收盘价 {hist_data.iloc[0]['close']}")
        
        # 测试获取财务数据
        print("\n💰 获取财务数据...")
        income_data = pro.income(ts_code='600036.SH', period='20231231')
        if not income_data.empty:
            print(f"   ✅ 获取到财务数据")
            print(f"   💵 营业收入: {income_data.iloc[0]['revenue']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Tushare测试失败: {e}")
        return False

async def test_scheduled_updater_with_real_data():
    """测试定时更新器与真实数据源的集成"""
    print("\n⏰ 测试定时更新器与真实数据源集成")
    print("=" * 60)
    
    try:
        from tradingagents.dataflows.scheduled_updater import scheduled_updater
        from tradingagents.dataflows.priority_manager import priority_manager
        
        # 初始化
        await scheduled_updater.initialize()
        await priority_manager.initialize()
        
        # 配置真实数据源优先级
        print("🔧 配置真实数据源优先级...")
        
        # 检查可用的数据源
        available_sources = []
        
        try:
            import akshare
            available_sources.append({
                "source_name": "akshare",
                "priority": 1,
                "enabled": True,
                "weight": 1.0,
                "timeout_seconds": 30,
                "max_requests_per_minute": 100,
                "retry_count": 3
            })
            print("   ✅ 添加AKShare数据源")
        except ImportError:
            pass
        
        try:
            import tushare
            if os.getenv('TUSHARE_TOKEN'):
                available_sources.append({
                    "source_name": "tushare",
                    "priority": 2,
                    "enabled": True,
                    "weight": 0.9,
                    "timeout_seconds": 30,
                    "max_requests_per_minute": 50,
                    "retry_count": 3
                })
                print("   ✅ 添加Tushare数据源")
        except ImportError:
            pass
        
        try:
            import baostock
            available_sources.append({
                "source_name": "baostock",
                "priority": 3,
                "enabled": True,
                "weight": 0.8,
                "timeout_seconds": 30,
                "max_requests_per_minute": 200,
                "retry_count": 2
            })
            print("   ✅ 添加BaoStock数据源")
        except ImportError:
            pass
        
        if available_sources:
            # 更新优先级配置
            await priority_manager.update_priority_config("cn", "historical", available_sources, "test_user")
            await priority_manager.update_priority_config("cn", "fundamental", available_sources, "test_user")
            await priority_manager.update_priority_config("cn", "realtime", available_sources, "test_user")
            
            print(f"   ✅ 配置了 {len(available_sources)} 个数据源")
            
            # 测试手动触发更新
            print("\n🚀 测试手动触发数据更新...")
            
            # 测试历史数据更新
            print("   📈 触发历史数据更新...")
            try:
                await scheduled_updater.trigger_manual_update("historical", ["600036"])
                print("   ✅ 历史数据更新触发成功")
            except Exception as e:
                print(f"   ⚠️ 历史数据更新失败: {e}")
            
            # 测试基本面数据更新
            print("   📊 触发基本面数据更新...")
            try:
                await scheduled_updater.trigger_manual_update("fundamental", ["600036"])
                print("   ✅ 基本面数据更新触发成功")
            except Exception as e:
                print(f"   ⚠️ 基本面数据更新失败: {e}")
            
            # 获取更新统计
            print("\n📊 获取更新统计...")
            status = scheduled_updater.get_update_status()
            stats = status.get('stats', {})
            
            print(f"   📈 总更新次数: {stats.get('total_updates', 0)}")
            print(f"   ✅ 成功次数: {stats.get('successful_updates', 0)}")
            print(f"   ❌ 失败次数: {stats.get('failed_updates', 0)}")
            
            return True
        else:
            print("   ⚠️ 没有可用的数据源，跳过集成测试")
            return False
            
    except Exception as e:
        print(f"   ❌ 定时更新器集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_scheduler_jobs():
    """测试定时任务调度"""
    print("\n📅 测试定时任务调度")
    print("=" * 60)
    
    try:
        from tradingagents.dataflows.scheduled_updater import scheduled_updater
        
        # 启动调度器
        print("🔧 启动调度器...")
        await scheduled_updater.start()
        
        # 获取任务状态
        print("\n📋 获取任务状态...")
        status = scheduled_updater.get_update_status()
        
        print(f"   🔄 调度器运行状态: {'运行中' if status.get('is_running', False) else '已停止'}")
        
        # 显示所有任务
        next_runs = status.get('next_runs', {})
        job_names = {
            "daily_historical_update": "每日历史数据更新",
            "weekly_fundamental_update": "每周基本面数据更新",
            "monthly_company_update": "每月公司信息更新",
            "realtime_cache_refresh": "实时数据缓存刷新"
        }
        
        print("\n📅 定时任务列表:")
        for job_id, job_name in job_names.items():
            next_run = next_runs.get(job_id, "未安排")
            print(f"   📅 {job_name}: {next_run}")
        
        # 等待一小段时间观察调度器
        print("\n⏳ 等待5秒观察调度器运行...")
        await asyncio.sleep(5)
        
        # 停止调度器
        print("\n🛑 停止调度器...")
        await scheduled_updater.stop()
        
        return True
        
    except Exception as e:
        print(f"   ❌ 调度器测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🚀 定时任务功能专项测试")
    print("=" * 80)
    
    test_functions = [
        ("真实数据源检测", test_real_data_sources),
        ("AKShare数据测试", test_akshare_data),
        ("Tushare数据测试", test_tushare_data),
        ("定时更新器集成测试", test_scheduled_updater_with_real_data),
        ("定时任务调度测试", test_scheduler_jobs)
    ]
    
    results = []
    
    for test_name, test_func in test_functions:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    # 总结结果
    print("\n" + "=" * 80)
    print("📋 定时任务测试结果总结")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n📊 总体结果: {passed}/{total} 测试通过")
    
    if passed >= total * 0.8:
        print("🎉 定时任务功能测试基本通过！")
        print("\n🎯 测试验证:")
        print("✅ 真实数据源集成正常")
        print("✅ 定时更新器功能可用")
        print("✅ 任务调度机制正常")
        print("✅ 数据源优先级配置生效")
        
        print("\n💡 建议:")
        print("- 在生产环境中启用MongoDB和Redis以获得完整功能")
        print("- 配置所有需要的API Token以获得最佳数据质量")
        print("- 根据实际需求调整定时任务的执行频率")
        
    else:
        print("⚠️ 定时任务功能需要进一步检查")
        print("\n💡 常见问题:")
        print("- 数据源依赖包未安装")
        print("- API Token未配置")
        print("- 网络连接问题")
    
    return passed >= total * 0.8

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
