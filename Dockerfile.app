# TradingAgents-CN 应用镜像
# 基于基础镜像，添加字体和项目文件
FROM tradingagents-cn-base:0.1.8-base

LABEL maintainer="TradingAgents-CN Team"
LABEL description="TradingAgents-CN应用镜像，包含完整功能"
LABEL version="0.1.8"

# 安装中文字体和时区数据（在应用层安装确保生效）
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
    fonts-liberation \
    tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && fc-cache -fv

# 设置中国时区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 创建Streamlit配置目录和配置文件
RUN mkdir -p /app/.streamlit

# 创建Streamlit配置文件，禁用邮箱收集
RUN echo '[server]\n\
port = 8501\n\
address = "0.0.0.0"\n\
headless = true\n\
enableCORS = false\n\
enableXsrfProtection = false\n\
\n\
[browser]\n\
gatherUsageStats = false\n\
serverAddress = "0.0.0.0"\n\
serverPort = 8501\n\
\n\
[logger]\n\
level = "info"\n\
\n\
[global]\n\
developmentMode = false\n\
showWarningOnDirectExecution = false\n\
disableWatchdogWarning = true\n\
suppressDeprecationWarnings = true\n\
\n\
[theme]\n\
base = "light"\n\
primaryColor = "#1f77b4"\n\
backgroundColor = "#ffffff"\n\
secondaryBackgroundColor = "#f0f2f6"\n\
textColor = "#262730"\n\
\n\
[ui]\n\
hideTopBar = true\n\
hideSidebarNav = false' > /app/.streamlit/config.toml

# 创建credentials文件，禁用邮箱收集
RUN echo '[general]\n\
email = ""' > /app/.streamlit/credentials.toml

# 复制项目文件
COPY . .

# 使用Xvfb启动脚本运行Streamlit，禁用邮箱收集
CMD ["/usr/local/bin/start-xvfb.sh", "python", "-m", "streamlit", "run", "web/app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true", "--browser.gatherUsageStats=false"]
