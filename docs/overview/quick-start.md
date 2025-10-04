# Quick Start Guide

## Overview
This guide helps you install and run TradingAgents from scratch and produce your first structured equity analysis in minutes.

## Feature Snapshot (v0.1.7 context)

### Dockerized Deployment
- ✅ One-command environment (docker-compose)
- ✅ Service bundle: Web + MongoDB + Redis
- ✅ Dev volumes for live code iteration

### Professional Report Export
- ✅ Multi-format: Markdown / Word / PDF
- ✅ Structured institutional layout
- ✅ One-click export via web UI

### DeepSeek V3 Integration
- ✅ Cost efficiency (significantly lower than GPT-4 tier)
- ✅ Tool call readiness for data-rich tasks
- ✅ Chinese financial task optimization (source heritage)
- ✅ UI feedback aligned with data origin & provider

### Recommended LLM Environment (example)
```bash
# Cost-optimized pairing
DASHSCOPE_API_KEY=your_dashscope_key
DEEPSEEK_API_KEY=your_deepseek_key
TUSHARE_TOKEN=your_tushare_token
```

## Prerequisites
| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| OS | Win 10 / macOS 10.15 / Linux | Latest stable |
| Python | 3.10 | 3.11 |
| Memory | 4 GB | 8+ GB |
| Disk | 2 GB free | 5+ GB with caches |

### API Keys (examples)
1. DashScope (Qwen) – domestic LLM provider
2. FinnHub – equity & fundamentals data
3. Google AI (Gemini) – optional alternative
4. Optional: DeepSeek / OpenAI / Anthropic / Tushare

## Installation

### 1. Clone
```bash

cd TradingAgents-CN
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate      # macOS/Linux
# venv\Scripts\activate      # Windows
```
(Or use conda: `conda create -n tradingagents python=3.11`)

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
# edit .env and add keys:
DASHSCOPE_API_KEY=...
FINNHUB_API_KEY=...
GOOGLE_API_KEY=...
MONGODB_ENABLED=false
REDIS_ENABLED=false
```

## First Run

### Web Interface (Recommended)
```bash
python start_web.py
```
Then open: http://localhost:8501

Web UI provides:
1. Interactive stock analysis launcher
2. API key & model configuration
3. Real-time progress tracking
4. Token / usage tracking
5. Report export actions

### CLI Mode
```bash
python -m cli.main
```

### Python API Example
```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

config = DEFAULT_CONFIG.copy()
config["deep_think_llm"] = "gpt-4o-mini"
config["quick_think_llm"] = "gpt-4o-mini"
config["max_debate_rounds"] = 1
config["online_tools"] = True

ta = TradingAgentsGraph(debug=True, config=config)
print("Analyzing AAPL...")
state, decision = ta.propagate("AAPL", "2024-01-15")

print("\n=== RESULT ===")
print("Action:", decision.get("action", "hold"))
print("Confidence:", f"{decision.get('confidence', 0.5):.2f}")
print("Risk Score:", f"{decision.get('risk_score', 0.5):.2f}")
print("Reasoning:", decision.get("reasoning", "N/A"))
```

## Configuration Options
```python
config = {
    "llm_provider": "openai",            # or dashscope, google, anthropic
    "deep_think_llm": "gpt-4o-mini",
    "quick_think_llm": "gpt-4o-mini",
    "max_debate_rounds": 1,              # 1–5
    "max_risk_discuss_rounds": 1,
    "online_tools": True,
}
```

### Selecting Analysts
```python
selected_analysts = [
    "market",       # technical
    "fundamentals", # fundamentals
    "news",         # news & events
    "social"        # sentiment / social
]

ta = TradingAgentsGraph(
    selected_analysts=selected_analysts,
    debug=True,
    config=config
)
```

## Full Analysis Example
```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

def analyze(symbol: str, date: str):
    cfg = DEFAULT_CONFIG.copy()
    cfg["deep_think_llm"] = "gpt-4o-mini"
    cfg["quick_think_llm"] = "gpt-4o-mini"
    cfg["max_debate_rounds"] = 2
    cfg["online_tools"] = True

    ta = TradingAgentsGraph(
        selected_analysts=["market", "fundamentals", "news", "social"],
        debug=True,
        config=cfg
    )

    print(f"Analyzing {symbol} ({date})...")
    try:
        state, decision = ta.propagate(symbol, date)
        print("\n" + "=" * 48)
        print(f"Symbol: {symbol}")
        print(f"Date:   {date}")
        print("=" * 48)
        print("\nDecision:")
        print("  Action:", decision.get("action", "hold").upper())
        print("  Quantity:", decision.get("quantity", 0))
        print("  Confidence:", f"{decision.get('confidence', 0.5):.1%}")
        print("  Risk Score:", f"{decision.get('risk_score', 0.5):.1%}")
        print("\nReasoning:")
        print("  ", decision.get("reasoning", "N/A"))
        if hasattr(state, 'analyst_reports'):
            print("\nAnalyst Scores:")
            for name, report in state.analyst_reports.items():
                score = report.get('overall_score', report.get('score', 0.5))
                print(f"  {name}: {score:.1%}")
        return decision
    except Exception as e:
        print("❌ Analysis failed:", e)
        return None

if __name__ == "__main__":
    result = analyze("AAPL", "2024-01-15")
    print("\n✅ Done" if result else "\n❌ Failed")
```

## Troubleshooting
| Issue | Message Example | Resolution |
|-------|-----------------|------------|
| Missing API Key | OpenAI API key not found | Set OPENAI_API_KEY or provider key in .env |
| Network Timeout | Connection timeout | Retry / proxy / stabilize network |
| Memory Error | Out of memory | Reduce debate rounds or use lighter model |
| Data Fetch Fail | Failed to fetch data | Verify FINNHUB_API_KEY or throttle calls |

## Cost Control
```python
config["deep_think_llm"] = "gpt-4o-mini"      # cheaper tier
config["quick_think_llm"] = "gpt-4o-mini"
config["max_debate_rounds"] = 1               # reduce reasoning cycles
config["online_tools"] = False                # prefer cached datasets
selected_analysts = ["market", "fundamentals"] # fewer agents
```

## Next Steps
1. Explore configuration (config guide under translation)
2. Extend agents (custom strategy injection)
3. Review architecture docs
4. Add caching & DB for performance

## Getting Help
- GitHub Issues (bug reports / feature ideas)
- Existing troubleshooting & FAQ documents (being translated)
- Community discussion (refer to upstream links)

Enjoy exploring! 🚀
    config = DEFAULT_CONFIG.copy()
