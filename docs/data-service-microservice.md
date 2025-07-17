# 数据源微服务部署指南

## 🚀 概述

数据源微服务是TradingAgents项目的核心组件，提供独立的数据获取、存储、缓存和管理功能。支持多种部署方式，包括Docker、Docker Compose和Kubernetes。

## 📋 功能特性

### 🔧 核心功能
- **数据获取**: 支持多数据源（AKShare、Tushare、BaoStock、yfinance）
- **智能缓存**: Redis + 内存多层次缓存
- **数据存储**: MongoDB持久化存储
- **优先级配置**: 用户自定义数据源优先级
- **定时任务**: 自动化数据更新
- **A/B测试**: 数据源效果对比
- **健康监控**: 完整的健康检查和监控

### 🌐 API接口
- **RESTful API**: 标准化REST接口
- **OpenAPI文档**: 自动生成API文档
- **健康检查**: `/health` 端点
- **实时监控**: 服务状态和统计信息

## 🐳 Docker部署

### 1. 单容器部署

```bash
# 构建镜像
docker build -f Dockerfile.data-service -t tradingagents/data-service:latest .

# 运行容器
docker run -d \
  --name tradingagents-data-service \
  -p 8001:8001 \
  -e MONGODB_ENABLED=false \
  -e REDIS_ENABLED=false \
  tradingagents/data-service:latest
```

### 2. Docker Compose部署（推荐）

```bash
# 启动完整服务栈
python manage_data_service.py start --build

# 或者直接使用docker-compose
docker-compose -f docker-compose.data-service.yml up -d --build
```

#### 服务组件
- **data-service**: 数据源微服务 (端口8001)
- **mongodb**: MongoDB数据库 (端口27017)
- **redis**: Redis缓存 (端口6379)
- **nginx**: 反向代理 (端口80/443)

## ☸️ Kubernetes部署

### 1. 部署到Kubernetes

```bash
# 应用配置
kubectl apply -f k8s/data-service-deployment.yaml

# 检查部署状态
kubectl get pods -n tradingagents
kubectl get services -n tradingagents
```

### 2. 扩缩容

```bash
# 扩容到3个实例
kubectl scale deployment data-service --replicas=3 -n tradingagents

# 查看状态
kubectl get deployment data-service -n tradingagents
```

### 3. 访问服务

```bash
# 端口转发
kubectl port-forward service/data-service 8001:8001 -n tradingagents

# 或者配置Ingress访问
# http://data-api.tradingagents.local
```

## 🔧 管理工具

### 使用管理脚本

```bash
# 启动服务
python manage_data_service.py start

# 重新构建并启动
python manage_data_service.py start --build

# 查看状态
python manage_data_service.py status

# 查看日志
python manage_data_service.py logs

# 实时跟踪日志
python manage_data_service.py logs --follow

# 测试API
python manage_data_service.py test

# 停止服务
python manage_data_service.py stop

# 重启服务
python manage_data_service.py restart
```

### 扩缩容

```bash
# 扩容数据服务到3个实例
python manage_data_service.py scale --service data-service --replicas 3
```

## 📊 监控和健康检查

### 健康检查端点

```bash
# 基本健康检查
curl http://localhost:8001/health

# 详细组件状态
curl http://localhost:8001/api/v1/status/scheduler
```

### 监控指标

- **服务状态**: 运行状态、响应时间
- **数据库连接**: MongoDB连接状态
- **缓存状态**: Redis连接和命中率
- **任务调度**: 定时任务执行状态
- **数据源健康**: 各数据源可用性

## 🔐 安全配置

### 环境变量配置

```bash
# 数据库认证
MONGODB_USERNAME=admin
MONGODB_PASSWORD=your-secure-password

# Redis认证
REDIS_PASSWORD=your-redis-password

# API密钥
TUSHARE_TOKEN=your-tushare-token
FINNHUB_API_KEY=your-finnhub-key
```

### 网络安全

- **内部通信**: 容器间使用内部网络
- **SSL/TLS**: 支持HTTPS配置
- **防火墙**: 只暴露必要端口
- **认证**: API密钥和数据库认证

## 📈 性能优化

### 资源配置

```yaml
# Kubernetes资源限制
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

### 缓存优化

- **Redis缓存**: 热数据缓存
- **内存缓存**: 实时数据缓存
- **TTL策略**: 差异化过期时间
- **缓存预热**: 启动时预加载热数据

### 数据库优化

- **索引优化**: 查询性能优化
- **连接池**: 数据库连接管理
- **批量操作**: 减少数据库访问次数

## 🔄 CI/CD集成

### GitHub Actions示例

```yaml
name: Deploy Data Service
on:
  push:
    branches: [main]
    paths: ['tradingagents/api/**', 'tradingagents/dataflows/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Build and Push Docker Image
      run: |
        docker build -f Dockerfile.data-service -t ${{ secrets.REGISTRY }}/data-service:${{ github.sha }} .
        docker push ${{ secrets.REGISTRY }}/data-service:${{ github.sha }}
    
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/data-service data-service=${{ secrets.REGISTRY }}/data-service:${{ github.sha }} -n tradingagents
```

## 🧪 测试

### API测试

```bash
# 基本功能测试
python manage_data_service.py test

# 手动API测试
curl http://localhost:8001/api/v1/stocks?limit=5
curl http://localhost:8001/api/v1/stocks/600036/historical
```

### 负载测试

```bash
# 使用Apache Bench
ab -n 1000 -c 10 http://localhost:8001/health

# 使用wrk
wrk -t12 -c400 -d30s http://localhost:8001/api/v1/stocks
```

## 📚 API文档

### 访问文档

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **OpenAPI JSON**: http://localhost:8001/openapi.json

### 主要端点

- `GET /health` - 健康检查
- `GET /api/v1/stocks` - 获取股票列表
- `GET /api/v1/stocks/{code}/historical` - 获取历史数据
- `GET /api/v1/stocks/{code}/fundamental` - 获取基本面数据
- `POST /api/v1/data/refresh` - 触发数据刷新
- `GET /api/v1/config/priority` - 获取优先级配置

## 🚨 故障排除

### 常见问题

1. **服务启动失败**
   - 检查端口占用: `netstat -tlnp | grep 8001`
   - 查看日志: `python manage_data_service.py logs`

2. **数据库连接失败**
   - 检查MongoDB状态: `docker ps | grep mongo`
   - 验证连接字符串和认证信息

3. **缓存不可用**
   - 检查Redis状态: `docker ps | grep redis`
   - 系统会自动降级到内存缓存

4. **API响应慢**
   - 检查数据源网络连接
   - 查看缓存命中率
   - 监控资源使用情况

### 日志分析

```bash
# 查看错误日志
python manage_data_service.py logs | grep ERROR

# 查看特定服务日志
python manage_data_service.py logs --service data-service

# 实时监控
python manage_data_service.py logs --follow
```

## 📞 支持

如有问题，请：
1. 查看日志文件
2. 检查健康状态
3. 参考故障排除指南
4. 提交Issue到GitHub仓库

---

**数据源微服务为TradingAgents提供了强大的数据基础设施，支持高可用、高性能的金融数据服务。**
