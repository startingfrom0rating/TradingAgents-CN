@echo off
echo 🏗️ TradingAgents-CN 分层构建
echo ========================================

REM 检查Docker是否运行
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker未运行，请启动Docker Desktop
    pause
    exit /b 1
)

echo ✅ Docker运行正常

REM 第一步：构建基础镜像
echo.
echo 📦 第一步：构建基础镜像...
echo ----------------------------------------
docker build -t tradingagents-cn-base:0.1.8-base -f Dockerfile.base .

if errorlevel 1 (
    echo ❌ 基础镜像构建失败
    pause
    exit /b 1
)

echo ✅ 基础镜像构建成功

REM 第二步：构建应用镜像
echo.
echo 🚀 第二步：构建应用镜像...
echo ----------------------------------------
docker build -t tradingagents-cn:0.1.8-layered -f Dockerfile.app .

if errorlevel 1 (
    echo ❌ 应用镜像构建失败
    pause
    exit /b 1
)

echo ✅ 应用镜像构建成功

REM 显示镜像信息
echo.
echo 📊 构建完成的镜像:
echo ----------------------------------------
docker images | findstr tradingagents-cn

echo.
echo 🎉 分层构建完成！
echo.
echo 📋 下一步操作:
echo 1. 启动应用: docker-compose -f docker-compose.layered.yml up -d
echo 2. 查看日志: docker-compose -f docker-compose.layered.yml logs -f web
echo 3. 访问应用: http://localhost:8501

pause
