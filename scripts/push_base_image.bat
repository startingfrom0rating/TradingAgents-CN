@echo off
echo 🚀 推送TradingAgents-CN基础镜像到阿里云
echo ==========================================

REM 检查Docker是否运行
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker未运行，请启动Docker Desktop
    pause
    exit /b 1
)

echo ✅ Docker运行正常

REM 设置变量
set BASE_IMAGE_NAME=tradingagents-cn-base
set VERSION=0.1.8-base
set ALIYUN_REGISTRY=crpi-zd2o9zyvvkhu08ke.cn-guangzhou.personal.cr.aliyuncs.com
set ALIYUN_NAMESPACE=tradingagents-cn

echo.
echo 📋 镜像信息:
echo   本地镜像: %BASE_IMAGE_NAME%:%VERSION%
echo   阿里云地址: %ALIYUN_REGISTRY%/%ALIYUN_NAMESPACE%/%BASE_IMAGE_NAME%
echo.

REM 检查本地镜像是否存在
docker images %BASE_IMAGE_NAME%:%VERSION% | findstr %VERSION% >nul
if errorlevel 1 (
    echo ❌ 本地基础镜像不存在，请先构建基础镜像
    echo    构建命令: docker build -t %BASE_IMAGE_NAME%:%VERSION% -f Dockerfile.base .
    pause
    exit /b 1
)

echo ✅ 本地基础镜像存在

REM 登录阿里云镜像服务
echo.
echo 🔑 登录阿里云镜像服务...
docker login --username=tb324166351 %ALIYUN_REGISTRY%

if errorlevel 1 (
    echo ❌ 登录失败
    pause
    exit /b 1
)

echo ✅ 登录成功

REM 标记镜像
echo.
echo 🏷️ 标记镜像...
set ALIYUN_IMAGE=%ALIYUN_REGISTRY%/%ALIYUN_NAMESPACE%/%BASE_IMAGE_NAME%

docker tag %BASE_IMAGE_NAME%:%VERSION% %ALIYUN_IMAGE%:%VERSION%
docker tag %BASE_IMAGE_NAME%:%VERSION% %ALIYUN_IMAGE%:latest

echo ✅ 镜像标记完成

REM 推送镜像
echo.
echo 📤 推送镜像到阿里云...
echo 推送版本镜像: %ALIYUN_IMAGE%:%VERSION%
docker push %ALIYUN_IMAGE%:%VERSION%

if errorlevel 1 (
    echo ❌ 版本镜像推送失败
    pause
    exit /b 1
)

echo 推送latest镜像: %ALIYUN_IMAGE%:latest
docker push %ALIYUN_IMAGE%:latest

if errorlevel 1 (
    echo ❌ latest镜像推送失败
    pause
    exit /b 1
)

echo.
echo ✅ 基础镜像推送成功！
echo.
echo 📋 阿里云镜像地址:
echo   %ALIYUN_IMAGE%:%VERSION%
echo   %ALIYUN_IMAGE%:latest
echo.
echo 🎯 使用方法:
echo   1. 使用阿里云基础镜像构建: docker-compose -f docker-compose.cloud.yml build
echo   2. 启动应用: docker-compose -f docker-compose.cloud.yml up -d
echo.

pause
