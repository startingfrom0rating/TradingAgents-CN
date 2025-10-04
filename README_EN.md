# TradingAgents (Chinese Enhanced Edition) - English Documentation

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/Version-cn--0.1.15-green.svg)](./VERSION)
[![Documentation](https://img.shields.io/badge/docs-Chinese-green.svg)](./docs/)
[![Original](https://img.shields.io/badge/Based%20on-TauricResearch/TradingAgents-orange.svg)](https://github.com/TauricResearch/TradingAgents)

> 🚀 **Latest Version cn-0.1.15**: Major upgrade for developer experience & LLM ecosystem! Added Baidu Qianfan (ERNIE) support, complete developer tooling, academic research resources, and enterprise-grade workflow standards.
>
> 🎯 **Core Features**: Native OpenAI support | Full Google AI integration | Custom endpoint configuration | Intelligent model selection | Multi-LLM provider support | Persistent model selection | Dockerized deployment | Professional report export | Full A-share support | Chinese localization

A **Chinese-focused multi-agent LLM trading & investment decision framework**. Optimized for Chinese users with complete A-share/HK/US market analysis capabilities.

## 🙏 Acknowledgment of the Upstream Project

Thanks to the [Tauric Research](https://github.com/TauricResearch) team for creating the revolutionary multi-agent trading framework: [TradingAgents](https://github.com/TauricResearch/TradingAgents)!

**🎯 Our Mission**: Provide a fully localized Chinese experience, support A-share & HK markets, integrate domestic LLMs, and accelerate AI finance adoption in the Chinese developer & research community.

---

## 🆕 v0.1.15 Highlights

### 🤖 LLM Ecosystem Upgrade

- **Baidu Qianfan (ERNIE) Support**: Full integration of Baidu Qianfan large models
- **Adapter Refactor**: Unified OpenAI-compatible adapter architecture
- **More Providers**: Broader domestic LLM coverage
- **Integration Guides**: Complete LLM integration + testing documentation

### 📚 Academic Research Support

- **TradingAgents Paper**: Full Chinese translation + deep analysis
- **Technical Blogs**: Architecture & implementation deep dives
- **Research Assets**: PDF paper + reference materials
- **Citation Support**: Standard academic citation formats

### 🛠️ Developer Experience

- **Workflow Standards**: Structured branching & contribution guidelines
- **Installation Verification**: Automated validation scripts
- **Documentation Restructure**: Layered doc system & quick start guides
- **PR Templates**: Standardized review & contribution format

### 🔧 Enterprise Tooling

- **Branch Protection**: GitHub protection & governance policies
- **Emergency Procedures**: Incident recovery & safety playbooks
- **Testing Enhancements**: Broader coverage & validation harnesses
- **Deployment Guides**: Enterprise deployment & config governance

---

## 📋 v0.1.14 Recap

### 👥 User Authentication & Role System

- **Full User Management**: Registration (pre-seeded), login, permissions
- **Role-Based Access**: Multi-level role & permission framework
- **Session Management**: Secure session lifecycle
- **User Activity Logs**: Auditable interactions

### 🔐 Web Authentication

- **Modern Login UI**
- **Central Auth Manager**
- **Security Enhancements**: Password hashing, session security
- **User Dashboard**: Personalized analytics view

### 🗄️ Data Management Improvements

- **MongoDB Enhancements**: Improved connection & persistence layer
- **Data Directory Refactor**: Better structured storage hierarchy
- **Migration Scripts**: Backup + migration automation
- **Cache Optimization**: Faster loading & result caching

### 🧪 Testing Expansion

- **Feature Scripts**: +6 functional test utilities
- **Tool Handler Tests**: Google tool reliability patches
- **Auto-hide Guide Test**: UI interaction validation
- **Online Tool Config Tests**: Selection logic verification
- **E2E Scenarios**: Realistic usage workflows
- **US Market Independence**: Isolation validation

---

## 🆕 v0.1.13 Highlights

### 🤖 Native OpenAI Endpoint Support

- **Custom Endpoints**: Any OpenAI-compatible API host
- **Flexible Model Usage**: Use arbitrary OpenAI-format models
- **Smart Adapter**: Optimized native OpenAI adapter
- **Unified Config Management**

### 🧠 Full Google AI Ecosystem Integration

- **Three Packages Supported**: langchain-google-genai, google-generativeai, google-genai
- **9 Verified Models**: gemini-2.5-pro, gemini-2.5-flash, gemini-2.0-flash, etc.
- **Google Tool Processor**: Dedicated tool handler
- **Graceful Degradation**: Auto fallback on failure

### 🔧 LLM Adapter Improvements

- **GoogleOpenAIAdapter**: OpenAI-compatible interface for Google AI
- **Unified Calling Interface** across providers
- **Better Error Handling** + auto-retry
- **Performance Monitoring**

### 🎨 Web UI Optimization

- **Intelligent Model Selection** with availability awareness
- **KeyError Fixes** in model switching logic
- **Faster UI Responsiveness** for provider switching
- **Improved Error Messaging**

---

## 🆕 v0.1.12 Highlights

### 🧠 Intelligent News Analysis Module

- **AI-Powered News Filter**: Relevance + quality scoring
- **Multi-Layer Filtering**: Basic / Enhanced / Integrated stages
- **Quality Evaluation**: Deduplication + noise suppression
- **Unified News Tool**: Aggregated multi-source interface

### 🔧 Technical Fixes & Optimizations

- **DashScope Adapter Fixes**
- **DeepSeek Infinite Loop Patch** for news analyst
- **Tool Call Reliability Enhancements**
- **Improved News Retriever** performance & normalization

### 📚 Tests & Docs

- **15+ New Test Files**
- **8 Technical Analysis & Fix Reports**
- **User Guides**: News filtering manual & best practices
- **Demo Scripts**: Full news filtering showcase

### 🗂️ Project Structure Optimization

- **Categorized Docs** under `docs/`
- **Examples Organized** under `examples/`
- **Clean Root Layout** for professional structure

---

## 🎯 Core Capabilities

### 🤖 Multi-Agent Collaboration Architecture

- **Specialized Roles**: Fundamentals / Technical / News / Sentiment
- **Structured Debate**: Bull vs Bear analysts
- **Trader Decision Fusion** across all signals
- **Risk Management Layering**

### 🖥️ Web UI Overview

Modern Streamlit-powered responsive web interface with real-time progress, structured output, and export-ready reports.

### 🎯 Feature Highlights

#### 📋 Smart Analysis Configuration

- **🌍 Multi-Market**: US / CN A-share / HK
- **🎯 Five Research Depth Levels**: From 2-min quick scan to 25-min full research
- **🤖 Agent Selection**: Choose specialized analyst set
- **📅 Historical Timepoint Analysis**

#### 🚀 Real-Time Progress Tracking

- **📊 Visual Progress** & ETA prediction
- **🔄 Stage Identification**
- **⏱️ Historical Time Calibration**
- **💾 Persistent State** across refreshes

#### 📈 Professional Output

- **🎯 Investment Action**: Buy / Hold / Sell
- **📊 Multidimensional Evaluation**: Technical + Fundamentals + News
- **🔢 Quantitative Metrics**: Confidence, risk score, target price
- **📄 Exportable Reports**: Markdown / Word / PDF

#### 🤖 Multi-LLM Management

- **🌐 4 Providers**: DashScope, DeepSeek, Google AI, OpenRouter (OpenAI-native optional)
- **🎯 60+ Models** from budget to flagship
- **💾 Persistent Selection** via URL parameters
- **⚡ Quick Switch** buttons for top 5 models

### 🎮 Web Usage Quick Steps

1. Start app: `python start_web.py` or `docker-compose up -d`
2. Open: `http://localhost:8501`
3. Select provider & model
4. Enter stock symbol (e.g. AAPL / 000001 / 0700.HK)
5. Choose depth level (1–5)
6. Click "🚀 Start Analysis"
7. Watch real-time progress
8. Export report if needed

### 📊 Supported Stock Symbol Formats

- **US**: `AAPL`, `TSLA`, `MSFT`, `NVDA`, `GOOGL`
- **A-share**: `000001`, `600519`, `300750`, `002415`
- **Hong Kong**: `0700.HK`, `9988.HK`, `3690.HK`, `1810.HK`

### 🎯 Research Depth Levels

- **Level 1 (2–4 min)**: Quick scan
- **Level 2 (4–6 min)**: Standard technical + fundamentals
- **Level 3 (6–10 min)**: Adds news sentiment (Recommended ⭐)
- **Level 4 (10–15 min)**: Multi-round agent debate
- **Level 5 (15–25 min)**: Full institutional-style research

### 💡 Usage Tips

- Refresh-safe progress persistence
- Mobile + dark mode friendly
- Enter key shortcuts
- Recent configuration retention

---

## 🔐 User & Permission System

### 🔑 Default Accounts

| Username | Password  | Role      | Description                              |
|----------|-----------|-----------|------------------------------------------|
| admin    | admin123  | Admin     | Full system privileges & user management |
| user     | user123   | Standard  | Stock analysis & report viewing          |

> ⚠️ Change default passwords after first login!

### 🛡️ Capabilities

- 🔐 Authentication (username/password)
- 👥 Roles (admin/user, extendable)
- ⏰ Session timeout & security
- 📊 Activity logging

### 🛠️ Management Tools

Command-line + cross-platform scripts under `scripts/`.

Examples:

```bash
python scripts/user_password_manager.py list
python scripts/user_password_manager.py create analyst01 --role trader
python scripts/user_password_manager.py change-password admin
```

Config file: `web/config/users.json`

Limitations (current version): no self-service signup / no web-based role editing yet (CLI only).

---

## 🎯 Key Advantages

- 🧠 AI-powered news filtering & quality scoring
- 🔧 Multi-layer pipeline: Basic → Enhanced → Integrated
- 📰 Unified news retrieval interface
- 🤖 Multi-LLM integration (4 providers / 60+ models)
- 💾 Persistent model selection via URL encoding
- 🎯 Quick-switch model buttons
- 🔄 Async progress tracking
- 💾 Session resilience across reloads
- 🔐 Permission-controlled environment
- 🇨🇳 Chinese market + domestic LLM support
- 🐳 One-command Docker deployment
- 📄 Professional investment-style report export
- 🛡️ Multi-tier fallback & reliability engineering

---

## 🔧 Technical Stack

**Core**: Python 3.10+, LangChain, Streamlit, MongoDB, Redis

**LLMs**: DeepSeek, DashScope (Qwen), Google AI (Gemini), OpenRouter (OpenAI-compatible), OpenAI native

**Data Sources**: Tushare, AkShare, FinnHub, Yahoo Finance

**Deployment**: Docker, Docker Compose, Local install

---

## 🚀 Quick Start (Local)

```bash
python -m pip install --upgrade pip
pip install -e .
python start_web.py
# Open http://localhost:8501
```

Set API keys via `.env`:

```env
DASHSCOPE_API_KEY=...
FINNHUB_API_KEY=...
TUSHARE_TOKEN=...
GOOGLE_API_KEY=...
DEEPSEEK_API_KEY=...
```

MongoDB / Redis optional for performance (fallback works without them).

---

## 📤 Report Export

Export formats:
- Markdown (.md)
- Word (.docx)
- PDF (.pdf)

Includes: Summary decision, detailed multi-angle analysis, risk disclosures, configuration metadata.

---

## 📁 Data Directory Configuration

Manage data path:

```bash
python -m cli.main data-config --show
python -m cli.main data-config --set /path/to/data
```

Priority: Programmatic > Env var > Config file > Default.

---

## 🤝 Contributing

We welcome:

- 🐛 Bug fixes
- ✨ New features
- 📚 Documentation & localization
- 🎨 Code quality improvements
- 🧪 Test enhancements

Workflow:

1. Fork
2. Branch (`feature/...`)
3. Commit
4. Push
5. Open PR

See `CONTRIBUTORS.md` for acknowledgments.

---

## 📄 License

Apache 2.0 – See `LICENSE`.

You may: Use commercially, modify, distribute, patent. Must retain copyright & license.

---

## 🙏 Credits

Special thanks to the original [TradingAgents](https://github.com/TauricResearch/TradingAgents) project and its maintainers. This enhanced Chinese edition builds upon their excellent foundation while focusing on localization, accessibility, and expanded applied tooling for Chinese markets.

Mission Goals:
- 🌉 Technology diffusion
- 🎓 Educational enablement
- 🤝 Cross-cultural collaboration
- 🚀 Accelerating AI-driven finance innovation in Chinese ecosystems

---

## ⚠️ Disclaimer

This framework is for research & educational purposes only. Not investment advice.

- Market outcomes vary
- AI outputs are probabilistic
- Investment risk is real
- Consult a licensed advisor

---

## ⭐ Support

If this project helps you, please star the repo:

`git clone https://github.com/hsliuping/TradingAgents-CN`

Issues & feedback: https://github.com/hsliuping/TradingAgents-CN/issues

---

### Translation Coverage Note

This English README is the first step of a full repository translation. Planned next phases:

1. Core usage docs (`docs/overview/*`)
2. Architecture & agent design (`docs/architecture/*`, `docs/agents/*`)
3. Configuration & data docs
4. Technical fix / upgrade reports
5. Blog & research deep dives

We will mirror translated content under a future `docs-en/` tree to preserve original Chinese materials while enabling bilingual navigation.

Feel free to open an issue if you want specific documents prioritized for translation.

---

© 2025 TradingAgents-CN Contributors. Licensed under Apache 2.0.
