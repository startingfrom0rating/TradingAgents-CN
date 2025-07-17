#!/usr/bin/env python3
"""
数据源微服务管理脚本
提供启动、停止、状态检查、日志查看等管理功能
"""

import os
import sys
import subprocess
import time
import requests
import argparse
from pathlib import Path

class DataServiceManager:
    """数据源微服务管理器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.compose_file = self.project_root / "docker-compose.data-service.yml"
        self.service_url = "http://localhost:8001"
    
    def start(self, build=False):
        """启动微服务"""
        print("🚀 启动数据源微服务...")
        
        cmd = ["docker-compose", "-f", str(self.compose_file), "up", "-d"]
        if build:
            cmd.append("--build")
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("✅ 微服务启动成功")
            
            # 等待服务就绪
            print("⏳ 等待服务就绪...")
            self.wait_for_service()
            
            # 显示服务信息
            self.status()
            
        except subprocess.CalledProcessError as e:
            print(f"❌ 启动失败: {e}")
            print(f"错误输出: {e.stderr}")
            return False
        
        return True
    
    def stop(self):
        """停止微服务"""
        print("🛑 停止数据源微服务...")
        
        cmd = ["docker-compose", "-f", str(self.compose_file), "down"]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("✅ 微服务停止成功")
        except subprocess.CalledProcessError as e:
            print(f"❌ 停止失败: {e}")
            return False
        
        return True
    
    def restart(self, build=False):
        """重启微服务"""
        print("🔄 重启数据源微服务...")
        self.stop()
        time.sleep(2)
        return self.start(build)
    
    def status(self):
        """检查服务状态"""
        print("📊 检查服务状态...")
        
        # 检查Docker容器状态
        cmd = ["docker-compose", "-f", str(self.compose_file), "ps"]
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("\n🐳 Docker容器状态:")
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"❌ 无法获取容器状态: {e}")
        
        # 检查服务健康状态
        try:
            response = requests.get(f"{self.service_url}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                print("🏥 服务健康检查:")
                print(f"   状态: {health_data.get('status', 'unknown')}")
                print(f"   时间: {health_data.get('timestamp', 'unknown')}")
                
                components = health_data.get('components', {})
                for name, status in components.items():
                    print(f"   {name}: {status}")
            else:
                print(f"⚠️ 健康检查失败: HTTP {response.status_code}")
        except requests.RequestException as e:
            print(f"❌ 无法连接到服务: {e}")
        
        # 检查API端点
        try:
            response = requests.get(f"{self.service_url}/", timeout=5)
            if response.status_code == 200:
                print("✅ API服务正常")
                print(f"📚 API文档: {self.service_url}/docs")
            else:
                print(f"⚠️ API服务异常: HTTP {response.status_code}")
        except requests.RequestException as e:
            print(f"❌ API服务不可用: {e}")
    
    def logs(self, service=None, follow=False):
        """查看服务日志"""
        print("📋 查看服务日志...")
        
        cmd = ["docker-compose", "-f", str(self.compose_file), "logs"]
        if follow:
            cmd.append("-f")
        if service:
            cmd.append(service)
        
        try:
            if follow:
                # 实时跟踪日志
                subprocess.run(cmd, check=True)
            else:
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"❌ 获取日志失败: {e}")
    
    def build(self):
        """构建服务镜像"""
        print("🔨 构建服务镜像...")
        
        cmd = ["docker-compose", "-f", str(self.compose_file), "build"]
        
        try:
            subprocess.run(cmd, check=True)
            print("✅ 镜像构建成功")
        except subprocess.CalledProcessError as e:
            print(f"❌ 构建失败: {e}")
            return False
        
        return True
    
    def wait_for_service(self, timeout=60):
        """等待服务就绪"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.service_url}/health", timeout=5)
                if response.status_code == 200:
                    print("✅ 服务已就绪")
                    return True
            except requests.RequestException:
                pass
            
            print("⏳ 等待服务启动...", end="\r")
            time.sleep(2)
        
        print("⚠️ 服务启动超时")
        return False
    
    def test_api(self):
        """测试API功能"""
        print("🧪 测试API功能...")
        
        test_cases = [
            ("根路径", "/"),
            ("健康检查", "/health"),
            ("股票列表", "/api/v1/stocks?limit=5"),
            ("配置信息", "/api/v1/config/priority"),
            ("调度器状态", "/api/v1/status/scheduler")
        ]
        
        for name, endpoint in test_cases:
            try:
                response = requests.get(f"{self.service_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    print(f"   ✅ {name}: 正常")
                else:
                    print(f"   ⚠️ {name}: HTTP {response.status_code}")
            except requests.RequestException as e:
                print(f"   ❌ {name}: {e}")
    
    def scale(self, service, replicas):
        """扩缩容服务"""
        print(f"📈 扩缩容 {service} 到 {replicas} 个实例...")
        
        cmd = ["docker-compose", "-f", str(self.compose_file), "up", "-d", "--scale", f"{service}={replicas}"]
        
        try:
            subprocess.run(cmd, check=True)
            print(f"✅ {service} 已扩缩容到 {replicas} 个实例")
        except subprocess.CalledProcessError as e:
            print(f"❌ 扩缩容失败: {e}")
            return False
        
        return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="数据源微服务管理工具")
    parser.add_argument("command", choices=[
        "start", "stop", "restart", "status", "logs", "build", "test", "scale"
    ], help="管理命令")
    
    parser.add_argument("--build", action="store_true", help="启动时重新构建镜像")
    parser.add_argument("--follow", "-f", action="store_true", help="实时跟踪日志")
    parser.add_argument("--service", "-s", help="指定服务名称")
    parser.add_argument("--replicas", "-r", type=int, help="副本数量")
    
    args = parser.parse_args()
    
    manager = DataServiceManager()
    
    if args.command == "start":
        manager.start(build=args.build)
    elif args.command == "stop":
        manager.stop()
    elif args.command == "restart":
        manager.restart(build=args.build)
    elif args.command == "status":
        manager.status()
    elif args.command == "logs":
        manager.logs(service=args.service, follow=args.follow)
    elif args.command == "build":
        manager.build()
    elif args.command == "test":
        manager.test_api()
    elif args.command == "scale":
        if not args.service or not args.replicas:
            print("❌ 扩缩容需要指定 --service 和 --replicas 参数")
            sys.exit(1)
        manager.scale(args.service, args.replicas)

if __name__ == "__main__":
    main()
