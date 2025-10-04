# 🐳 Docker Image Build Guide

## 📋 Overview

This document describes how TradingAgents-CN builds Docker images locally rather than providing pre-built images. It explains the Dockerfile, build stages, optimization tips, and common issues.

## 🔧 Why build locally?

Design considerations:

1. Deterministic customization — users may require different runtime options and dependencies.
2. Security — avoid shipping sensitive information inside shared images.
3. Flexibility — allow users to patch or extend the image for their environment.
4. Dependency optimization — only install required system packages.

## 🧱 Dockerfile structure (example)

```dockerfile
# Base image
FROM python:3.10-slim

# Install system packages
RUN apt-get update && apt-get install -y \
    pandoc \
    wkhtmltopdf \
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app
WORKDIR /app

# Expose Streamlit
EXPOSE 8501
CMD ["streamlit", "run", "web/app.py"]
```

## 🔁 Build stages and costs

Stage 1: Pull base image

- Image size: ~200MB
- Time: 1–3 minutes (network dependent)

Stage 2: Install system dependencies

- Adds packages like pandoc and fonts
- Size estimate: +~300MB
- Time: 2–4 minutes

Stage 3: Install Python dependencies

- Based on `requirements.txt`
- Size: varies (approx. 500MB on average)
- Time: 2–5 minutes

Stage 4: Copy source code

- Size: small (~50MB)
- Time: <1 minute

## ⚡ Build optimizations

1. Leverage Docker layer caching

```dockerfile
# Put stable dependencies early
COPY requirements.txt .
RUN pip install -r requirements.txt
# Copy changing source later
COPY . /app
```

2. Multi-stage build (advanced)

```dockerfile
FROM python:3.10-slim as builder
RUN pip install --user -r requirements.txt

FROM python:3.10-slim
COPY --from=builder /root/.local /root/.local
COPY . /app
```

3. Use local mirrors for faster installs

```dockerfile
# Configure pip to use TUNA mirror
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# Speed up apt installs by using local mirrors (example)
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list
```

4. Optimize `.dockerignore`

Example `.dockerignore` contents:

```
.git
.gitignore
README.md
Dockerfile
.dockerignore
.env
.env.*
node_modules
.pytest_cache
.coverage
.vscode
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
.tox
.cache
*.log
.DS_Store
.mypy_cache
```

## 🚀 Build commands

```bash
# Standard build
docker-compose build

# Force rebuild without cache
docker-compose build --no-cache

# Build and run
docker-compose up --build

# Detached build and run
docker-compose up -d --build
```

## 🔍 Troubleshooting build issues

1. Network failures — use local mirrors for pip and apt.
2. Out of memory — increase Docker daemon memory (Docker Desktop settings).
3. File permission problems — ensure scripts have executable bits, e.g. `RUN chmod +x /app/scripts/*.sh`.
4. Slow builds — build only necessary layers and use parallel builds when possible.

## 📈 Best practices

- Use a CI pipeline and tag images with semantic versions.
- Minimize image size with multi-stage builds.
- Keep `.dockerignore` updated to reduce context size.
- Consider building and publishing images for reproducible deployments.

---

*Last updated: 2025-07-13*
