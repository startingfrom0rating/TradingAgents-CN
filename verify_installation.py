#!/usr/bin/env python3
"""
TradingAgents 数据源微服务安装验证脚本
快速验证系统安装和配置是否正确
"""

import os
import sys
import asyncio
import subprocess
import platform
from datetime import datetime

def print_header(title):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"🔍 {title}")
    print("=" * 60)

def print_step(step, description):
    """打印步骤"""
    print(f"\n{step}. {description}")
    print("-" * 40)

def check_python_version():
    """检查Python版本"""
    print_step("1", "检查Python版本")
    
    version = sys.version_info
    print(f"   Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version >= (3, 10):
        print("   ✅ Python版本符合要求 (3.10+)")
        return True
    else:
        print("   ❌ Python版本过低，需要3.10或更高版本")
        return False

def check_system_info():
    """检查系统信息"""
    print_step("2", "检查系统信息")
    
    system = platform.system()
    machine = platform.machine()
    print(f"   操作系统: {system}")
    print(f"   架构: {machine}")
    print(f"   平台: {platform.platform()}")
    
    return True

def check_project_structure():
    """检查项目结构"""
    print_step("3", "检查项目结构")
    
    required_files = [
        "tradingagents/__init__.py",
        "tradingagents/adapters/data_adapter.py",
        "tradingagents/clients/data_service_client.py",
        "tradingagents/dataflows/unified_data_source_manager.py",
        "tradingagents/api/data_service.py",
        "run_data_service.py",
        "manage_data_service.py",
        "requirements.txt",
        ".env.example"
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} (缺失)")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n   ⚠️ 缺失 {len(missing_files)} 个必要文件")
        return False
    else:
        print(f"\n   ✅ 所有必要文件都存在")
        return True

def check_dependencies():
    """检查依赖包"""
    print_step("4", "检查Python依赖包")
    
    required_packages = [
        "fastapi",
        "uvicorn", 
        "aiohttp",
        "motor",
        "aioredis",
        "apscheduler",
        "akshare",
        "tushare",
        "baostock",
        "yfinance"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} (未安装)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n   ⚠️ 缺失 {len(missing_packages)} 个依赖包")
        print("   💡 运行以下命令安装:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    else:
        print(f"\n   ✅ 所有依赖包都已安装")
        return True

def check_environment_config():
    """检查环境配置"""
    print_step("5", "检查环境配置")
    
    if os.path.exists(".env"):
        print("   ✅ .env 配置文件存在")
        
        # 检查关键配置项
        with open(".env", "r", encoding="utf-8") as f:
            content = f.read()
            
        config_items = [
            "TUSHARE_TOKEN",
            "DATA_SERVICE_PORT",
            "MONGODB_ENABLED",
            "REDIS_ENABLED"
        ]
        
        for item in config_items:
            if item in content:
                print(f"   ✅ {item} 已配置")
            else:
                print(f"   ⚠️ {item} 未配置")
        
        return True
    else:
        print("   ❌ .env 配置文件不存在")
        print("   💡 运行: cp .env.example .env")
        return False

def check_docker():
    """检查Docker环境"""
    print_step("6", "检查Docker环境 (可选)")
    
    try:
        result = subprocess.run(["docker", "--version"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"   ✅ Docker: {result.stdout.strip()}")
            docker_available = True
        else:
            print("   ❌ Docker命令执行失败")
            docker_available = False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("   ❌ Docker未安装或不可用")
        docker_available = False
    
    try:
        result = subprocess.run(["docker-compose", "--version"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"   ✅ Docker Compose: {result.stdout.strip()}")
        else:
            print("   ❌ Docker Compose不可用")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("   ❌ Docker Compose未安装")
    
    if not docker_available:
        print("   💡 Docker是可选的，可以使用本地模式运行")
    
    return True

async def test_local_mode():
    """测试本地模式"""
    print_step("7", "测试本地模式功能")
    
    try:
        # 加载环境变量
        if os.path.exists(".env"):
            with open(".env", "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
        
        # 测试导入
        from tradingagents.adapters.data_adapter import DataAdapter, DataMode
        print("   ✅ 模块导入成功")
        
        # 测试本地模式
        adapter = DataAdapter(mode=DataMode.LOCAL)
        await adapter.initialize()
        print("   ✅ 本地模式初始化成功")
        
        # 测试数据获取
        stocks = await adapter.get_stocks(limit=3)
        print(f"   ✅ 获取股票列表: {len(stocks)} 只")
        
        hist_data = await adapter.get_historical_data("600036")
        print(f"   ✅ 获取历史数据: {len(hist_data)} 条")
        
        fund_data = await adapter.get_fundamental_data("600036")
        if fund_data:
            print(f"   ✅ 获取基本面数据: PE={fund_data.get('pe_ratio')}")
        
        await adapter.close()
        print("   ✅ 本地模式测试完成")
        return True
        
    except Exception as e:
        print(f"   ❌ 本地模式测试失败: {e}")
        return False

async def test_microservice_mode():
    """测试微服务模式"""
    print_step("8", "测试微服务模式 (可选)")
    
    try:
        from tradingagents.clients.data_service_client import DataServiceClient
        
        async with DataServiceClient() as client:
            health = await client.health_check()
            
            if health.get('status') == 'healthy':
                print("   ✅ 微服务健康检查通过")
                
                # 测试API调用
                stocks = await client.get_stocks(limit=3)
                print(f"   ✅ 微服务API调用成功: {len(stocks)} 只股票")
                
                return True
            else:
                print("   ⚠️ 微服务不健康或未启动")
                return False
                
    except Exception as e:
        print(f"   ⚠️ 微服务连接失败: {e}")
        print("   💡 这是正常的，如果未启动微服务")
        return False

def generate_report(results):
    """生成测试报告"""
    print_header("安装验证报告")
    
    total_checks = len(results)
    passed_checks = sum(1 for result in results if result[1])
    
    print(f"📊 总检查项: {total_checks}")
    print(f"✅ 通过项: {passed_checks}")
    print(f"❌ 失败项: {total_checks - passed_checks}")
    print(f"📈 通过率: {passed_checks/total_checks*100:.1f}%")
    
    print("\n📋 详细结果:")
    for check_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {check_name}: {status}")
    
    # 给出建议
    if passed_checks == total_checks:
        print("\n🎉 恭喜！所有检查都通过了")
        print("✨ 您可以开始使用TradingAgents数据源微服务了")
        print("\n🚀 快速开始:")
        print("   # 本地模式")
        print("   python -c \"import asyncio; from tradingagents.adapters.data_adapter import get_stock_data; print(asyncio.run(get_stock_data('600036')))\"")
        print("\n   # 微服务模式")
        print("   python manage_data_service.py start")
        
    elif passed_checks >= total_checks * 0.8:
        print("\n✅ 基本功能可用")
        print("⚠️ 部分可选功能需要配置")
        print("\n💡 建议:")
        print("   - 配置API密钥以获得更好的数据质量")
        print("   - 安装Docker以使用完整微服务功能")
        
    else:
        print("\n⚠️ 安装不完整，需要解决以下问题:")
        for check_name, result in results:
            if not result:
                print(f"   - {check_name}")
        
        print("\n📚 参考文档:")
        print("   - 部署指南: docs/DEPLOYMENT_GUIDE.md")
        print("   - API参考: docs/API_REFERENCE.md")

async def main():
    """主函数"""
    print("🚀 TradingAgents 数据源微服务安装验证")
    print(f"⏰ 验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 执行所有检查
    results = []
    
    results.append(("Python版本", check_python_version()))
    results.append(("系统信息", check_system_info()))
    results.append(("项目结构", check_project_structure()))
    results.append(("Python依赖", check_dependencies()))
    results.append(("环境配置", check_environment_config()))
    results.append(("Docker环境", check_docker()))
    results.append(("本地模式", await test_local_mode()))
    results.append(("微服务模式", await test_microservice_mode()))
    
    # 生成报告
    generate_report(results)
    
    # 返回结果
    passed = sum(1 for _, result in results if result)
    return passed >= len(results) * 0.8

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 验证被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 验证过程发生错误: {e}")
        sys.exit(1)
