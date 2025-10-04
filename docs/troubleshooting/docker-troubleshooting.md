# Docker Container Startup Troubleshooting Guide

## 🔍 Quick checklist

### 1. Basic checks

```bash
# List container states
docker-compose ps -a

# Docker version
docker version

# Disk usage summary
docker system df
```

### 2. View logs

```bash
# Show all service logs
docker-compose logs

# Service specific logs
docker-compose logs web
docker-compose logs mongodb
docker-compose logs redis

# Follow logs for web
docker-compose logs -f web

# Tail recent logs
docker-compose logs --tail=50 web
```

### 3. Common problems and fixes

#### 🔴 Port conflicts

```bash
# Windows: check port usage
netstat -an | findstr :8501
netstat -an | findstr :27017
netstat -an | findstr :6379

# Kill a process by PID (Windows)
taskkill /PID <PID> /F
```

#### 🔴 Volume & data issues

```bash
# List volumes related to tradingagents
docker volume ls | findstr tradingagents

# Remove problematic volume (will lose data)
docker volume rm tradingagents_mongodb_data
docker volume rm tradingagents_redis_data

# Recreate volumes
docker volume create tradingagents_mongodb_data
docker volume create tradingagents_redis_data
```

#### 🔴 Network issues

```bash
# List networks related to tradingagents
docker network ls | findstr tradingagents

# Remove a network
docker network rm tradingagents-network

# Recreate network
docker network create tradingagents-network
```

#### 🔴 Image issues

```bash
# List images related to the project
docker images | findstr tradingagents

# Force rebuild without cache
docker-compose build --no-cache

# Remove and rebuild image
docker rmi tradingagents-cn:latest
docker-compose up -d --build
```

### 4. Environment / .env checks

```bash
# Ensure .env exists
ls .env

# Validate docker-compose config
docker-compose config
```

### 5. Disk space checks

```bash
# Check Docker disk usage
docker system df

# Clean unused resources
docker system prune -f

# Aggressively remove unused resources (be careful)
docker system prune -a -f
```

## 🛠️ Service-specific troubleshooting

### Web (Streamlit)

```bash
# View web logs
docker-compose logs web

# Enter web container for debugging
docker-compose exec web bash

# Check Python environment
docker-compose exec web python --version
docker-compose exec web pip list
```

### MongoDB

```bash
# View MongoDB logs
docker-compose logs mongodb

# Connect interactively
docker-compose exec mongodb mongo -u admin -p tradingagents123

# Ping the DB
docker-compose exec mongodb mongo --eval "db.adminCommand('ping')"
```

### Redis

```bash
# View Redis logs
docker-compose logs redis

# Connect with redis-cli
docker-compose exec redis redis-cli -a tradingagents123

# Ping Redis
docker-compose exec redis redis-cli -a tradingagents123 ping
```

## ⚠️ Emergency recovery commands

### Full reset (will remove data)

```bash
# Stop containers
docker-compose down

# Remove volumes and orphans
docker-compose down -v --remove-orphans

# Clean Docker system
docker system prune -f

# Rebuild and start
docker-compose up -d --build
```

### Keep data but restart

```bash
# Stop containers
docker-compose down

# Start again
docker-compose up -d
```

## 🧾 Log analysis tips

### Frequent error patterns

1. Port already in use: `bind: address already in use`
2. Permission denied: `permission denied`
3. Disk full: `no space left on device`
4. Out of memory: `out of memory`
5. Network errors: `network not found`
6. Image missing: `image not found`

### Filtering logs

```bash
# Show only errors
docker-compose logs | grep ERROR

# Show warnings
docker-compose logs | grep WARN

# Show logs since a specific date
docker-compose logs --since="2025-01-01T00:00:00"
```

## 🛡️ Preventative measures

1. Regular cleanup: `docker system prune -f`
2. Monitor resources: `docker stats`
3. Backup volumes periodically
4. Use versioned images and CI/CD

---

*Last updated: 2025-07-13*
*Version: cn-0.1.7*