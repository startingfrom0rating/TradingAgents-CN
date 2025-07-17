#!/usr/bin/env python3
"""
数据源微服务启动脚本
独立运行数据源优化服务，提供REST API接口
"""

import os
import sys
import asyncio
import uvicorn
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 加载环境变量
def load_env():
    """加载.env文件中的环境变量"""
    env_file = project_root / '.env'
    if env_file.exists():
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

from tradingagents.api.data_service import data_service_api

async def initialize_service():
    """初始化数据服务"""
    try:
        print("🔧 正在初始化数据源微服务...")
        await data_service_api.initialize()
        print("✅ 数据源微服务初始化成功")
        return True
    except Exception as e:
        print(f"❌ 数据源微服务初始化失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 启动数据源微服务")
    print("=" * 60)
    
    # 检查初始化
    success = asyncio.run(initialize_service())
    if not success:
        print("❌ 服务初始化失败，退出")
        sys.exit(1)
    
    # 配置参数
    host = os.getenv('DATA_SERVICE_HOST', '0.0.0.0')
    port = int(os.getenv('DATA_SERVICE_PORT', 8001))
    workers = int(os.getenv('DATA_SERVICE_WORKERS', 1))
    
    print(f"🌐 服务地址: http://{host}:{port}")
    print(f"👥 工作进程: {workers}")
    print(f"📚 API文档: http://{host}:{port}/docs")
    print(f"🔧 健康检查: http://{host}:{port}/health")
    print("=" * 60)
    
    # 启动服务
    try:
        uvicorn.run(
            data_service_api.app,
            host=host,
            port=port,
            workers=workers,
            log_level="info",
            access_log=True,
            reload=False
        )
    except KeyboardInterrupt:
        print("\n🛑 收到停止信号，正在关闭服务...")
    except Exception as e:
        print(f"❌ 服务运行错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
