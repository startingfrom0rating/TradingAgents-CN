# TradingAgents Agent Architecture

## Overview

TradingAgents implements a multi-agent collaboration model inspired by real financial research & execution teams. Each agent owns a distinct responsibility domain; shared state and message passing enable coordinated decision synthesis. This document (now translated) maps directly to the existing code structure.

## 🏗️ Layered Role Hierarchy

### Layer Model

The system defines five logical layers—each focused on a functional decision stage:

```mermaid
graph TD
    subgraph "Management Layer"
        RESMGR[Research Manager]
        RISKMGR[Risk Manager]
    end
    
    subgraph "Analysis Layer"
        FA[Fundamentals Analyst]
        MA[Market Analyst]
        NA[News Analyst]
        SA[Social Sentiment Analyst]
        CA[China Market Analyst]
    end
    
    subgraph "Research Layer"
        BR[Bull Researcher]
        BEAR[Bear Researcher]
    end
    
    subgraph "Execution Layer"
        TRADER[Trader]
    end
    
    subgraph "Risk Layer"
        CONSERVATIVE[Conservative Debator]
        NEUTRAL[Neutral Debator]
        AGGRESSIVE[Aggressive Debator]
    end
    
    %% 数据流向
    Analysis Layer --> Research Layer
    Research Layer --> Execution Layer
    Execution Layer --> Risk Layer
    Risk Layer --> Management Layer
    Management Layer --> Analysis Layer
    
    %% 样式定义
    classDef analysisNode fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef researchNode fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef executionNode fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef riskNode fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef managementNode fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    
    class FA,MA,NA,SA,CA analysisNode
    class BR,BEAR researchNode
    class TRADER executionNode
    class CONSERVATIVE,NEUTRAL,AGGRESSIVE riskNode
    class RESMGR,RISKMGR managementNode
```

### Role Responsibilities

- **Analysis Layer**: Raw data ingestion & first-pass interpretations
- **Research Layer**: Structured argumentation (bull vs bear synthesis)
- **Execution Layer**: Drafts actionable trade/investment plan
- **Risk Layer**: Multi-perspective risk calibration & challenge
- **Management Layer**: Coordination + escalation + final approval

## 🔧 State Management

### AgentState Core

Derived from `tradingagents/agents/utils/agent_states.py`; this class aggregates all mutable cross-agent fields:

```python
from typing import Annotated
from langgraph.graph import MessagesState

class AgentState(MessagesState):
    """智能体状态管理类 - 继承自 LangGraph MessagesState"""
    
    # Core identifiers
    company_of_interest: Annotated[str, "Target equity symbol"]
    trade_date: Annotated[str, "Trade/analysis date"]
    sender: Annotated[str, "Originating agent name"]
    # Analyst reports
    market_report: Annotated[str, "Market/technical report"]
    sentiment_report: Annotated[str, "Social sentiment report"]
    news_report: Annotated[str, "News/event report"]
    fundamentals_report: Annotated[str, "Fundamentals report"]
    # Research & decision
    investment_debate_state: Annotated[InvestDebateState, "Investment debate state"]
    investment_plan: Annotated[str, "Consolidated investment plan"]
    trader_investment_plan: Annotated[str, "Trader-adjusted plan"]
    # Risk management
    risk_debate_state: Annotated[RiskDebateState, "Risk debate state"]
    final_trade_decision: Annotated[str, "Final trade decision"]
```

### Debate State Structures

#### Investment Debate State

```python
class InvestDebateState(TypedDict):
    """Bull/Bear research debate state"""
    bull_history: Annotated[str, "Bull side turn history"]
    bear_history: Annotated[str, "Bear side turn history"]
    history: Annotated[str, "Merged transcript"]
    current_response: Annotated[str, "Latest debate message"]
    judge_decision: Annotated[str, "Interim or final adjudication"]
    count: Annotated[int, "Debate round index"]
```

#### Risk Debate State

```python
class RiskDebateState(TypedDict):
    """Risk perspective debate state"""
    risky_history: Annotated[str, "Aggressive perspective turns"]
    safe_history: Annotated[str, "Conservative perspective turns"]
    neutral_history: Annotated[str, "Neutral perspective turns"]
    history: Annotated[str, "Merged transcript"]
    latest_speaker: Annotated[str, "Last agent to speak"]
    current_risky_response: Annotated[str, "Latest aggressive reply"]
    current_safe_response: Annotated[str, "Latest conservative reply"]
    current_neutral_response: Annotated[str, "Latest neutral reply"]
    judge_decision: Annotated[str, "Risk judge decision"]
    count: Annotated[int, "Round index"]
```

## 🤖 Implementation Structure

### Analysis Layer

#### 1. Fundamentals Analyst

**文件位置**: `tradingagents/agents/analysts/fundamentals_analyst.py`

```python
from tradingagents.utils.tool_logging import log_analyst_module
from tradingagents.utils.logging_init import get_logger

def create_fundamentals_analyst(llm, toolkit):
    @log_analyst_module("fundamentals")
    def fundamentals_analyst_node(state):
    """Fundamentals analyst node implementation"""
        logger = get_logger("default")
        
        # 获取输入参数
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        
    # Market type detection
        from tradingagents.utils.stock_utils import StockUtils
        market_info = StockUtils.get_market_info(ticker)
        
    # Select appropriate analysis tools
        if toolkit.config["online_tools"]:
            tools = [toolkit.get_stock_fundamentals_unified]
        else:
            # 离线模式工具选择
            tools = [toolkit.get_fundamentals_openai]
        
    # Execute analysis logic
        # ...
        
        return state
    
    return fundamentals_analyst_node
```

#### 2. Market Analyst

**文件位置**: `tradingagents/agents/analysts/market_analyst.py`

```python
def create_market_analyst(llm, toolkit):
    @log_analyst_module("market")
    def market_analyst_node(state):
    """Market analyst node implementation"""
    # Technical & market structure analysis
        # ...
        return state
    
    return market_analyst_node
```

#### 3. News Analyst

**文件位置**: `tradingagents/agents/analysts/news_analyst.py`

```python
def create_news_analyst(llm, toolkit):
    @log_analyst_module("news")
    def news_analyst_node(state):
    """News analyst node implementation"""
    # News sentiment & event impact assessment
        # ...
        return state
    
    return news_analyst_node
```

#### 4. Social Sentiment Analyst

**文件位置**: `tradingagents/agents/analysts/social_media_analyst.py`

```python
def create_social_media_analyst(llm, toolkit):
    @log_analyst_module("social_media")
    def social_media_analyst_node(state):
    """Social media sentiment analyst node"""
    # Social sentiment extraction & aggregation
        # ...
        return state
    
    return social_media_analyst_node
```

#### 5. China Market Analyst

**文件位置**: `tradingagents/agents/analysts/china_market_analyst.py`

```python
def create_china_market_analyst(llm, toolkit):
    @log_analyst_module("china_market")
    def china_market_analyst_node(state):
    """China A-share specialist node"""
    # A-share specific structural logic
        # ...
        return state
    
    return china_market_analyst_node
```

### Research Layer

#### 1. Bull Researcher

**文件位置**: `tradingagents/agents/researchers/bull_researcher.py`

```python
def create_bull_researcher(llm):
    def bull_researcher_node(state):
    """Bull-side research node"""
    # Synthesize pro (bullish) thesis
        # ...
        return state
    
    return bull_researcher_node
```

#### 2. Bear Researcher

**文件位置**: `tradingagents/agents/researchers/bear_researcher.py`

```python
def create_bear_researcher(llm):
    def bear_researcher_node(state):
    """Bear-side research node"""
    # Synthesize contra (bearish) thesis
        # ...
        return state
    
    return bear_researcher_node
```

### Execution Layer – Trader

**文件位置**: `tradingagents/agents/trader/trader.py`

```python
def create_trader(llm, memory):
    def trader_node(state, name):
    """Trader node implementation"""
        # 获取所有分析报告
        company_name = state["company_of_interest"]
        investment_plan = state["investment_plan"]
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]
        
    # Market type detection
        from tradingagents.utils.stock_utils import StockUtils
        market_info = StockUtils.get_market_info(company_name)
        
    # Currency selection & normalization
        currency = market_info['currency_name']
        currency_symbol = market_info['currency_symbol']
        
    # Historical memory retrieval
        if memory is not None:
            past_memories = memory.get_memories(curr_situation, n_matches=2)
        
    # Produce structured trade decision
        # ...
        
        return state
    
    return trader_node
```

### Risk Layer

#### 1. Conservative Debator

**文件位置**: `tradingagents/agents/risk_mgmt/conservative_debator.py`

```python
def create_conservative_debator(llm):
    def conservative_debator_node(state):
    """Conservative risk perspective node"""
    # Conservative risk framing
        # ...
        return state
    
    return conservative_debator_node
```

#### 2. Neutral Debator

**文件位置**: `tradingagents/agents/risk_mgmt/neutral_debator.py`

```python
def create_neutral_debator(llm):
    def neutral_debator_node(state):
    """Neutral risk perspective node"""
    # Balanced risk articulation
        # ...
        return state
    
    return neutral_debator_node
```

#### 3. Aggressive Debator

**文件位置**: `tradingagents/agents/risk_mgmt/aggresive_debator.py`

```python
def create_aggressive_debator(llm):
    def aggressive_debator_node(state):
    """Aggressive risk perspective node"""
    # Aggressive escalation focus
        # ...
        return state
    
    return aggressive_debator_node
```

### Management Layer

#### 1. Research Manager

**文件位置**: `tradingagents/agents/managers/research_manager.py`

```python
def create_research_manager(llm):
    def research_manager_node(state):
    """Research manager coordination node"""
    # Consolidate debate → investment plan
        # ...
        return state
    
    return research_manager_node
```

#### 2. Risk Manager

**文件位置**: `tradingagents/agents/managers/risk_manager.py`

```python
def create_risk_manager(llm):
    def risk_manager_node(state):
    """Risk manager arbitration node"""
    # Integrate risk debate → final decision
        # ...
        return state
    
    return risk_manager_node
```

## 🔧 Tool Integration

### Unified Toolkit

All agents interface through a shared abstraction layer:

```python
class ToolKit:
    """Unified toolkit abstraction"""
    
    def __init__(self, config):
        self.config = config
    
    # Fundamentals
    def get_stock_fundamentals_unified(self, ticker: str):
    """Unified fundamentals accessor (auto market detection)"""
        pass
    
    # Market data
    def get_market_data(self, ticker: str):
    """Fetch market data"""
        pass
    
    # News data
    def get_news_data(self, ticker: str):
    """Fetch news data"""
        pass
```

### Logging Decorator System

Execution logging standardized via decorator:

```python
from tradingagents.utils.tool_logging import log_analyst_module

@log_analyst_module("analyst_type")
def analyst_node(state):
    """Analyst node – automatic execution logging"""
    # 智能体逻辑
    pass
```

## 🔄 Collaboration Workflow

### State Progression
1. **Initialization**: Build `AgentState`
2. **Analysis**: Parallel analyst report generation
3. **Research**: Bull vs bear structured debate
4. **Execution**: Trader synthesizes actionable plan
5. **Risk**: Multi-perspective challenge & calibration
6. **Management**: Coordination + approval

### Messaging
Agents communicate via the LangGraph `MessagesState` list:

```python
# Append message
state["messages"].append({
    "role": "assistant",
    "content": "分析结果",
    "sender": "fundamentals_analyst"
})

# Retrieve history
history = state["messages"]
```

## 🛠️ Utilities

### Stock Utilities
**Location**: `tradingagents/agents/utils/agent_utils.py`

```python
from tradingagents.utils.stock_utils import StockUtils

# Market metadata
market_info = StockUtils.get_market_info(ticker)
print(f"市场类型: {market_info['market_name']}")
print(f"货币: {market_info['currency_name']}")
```

### Memory Management
**Location**: `tradingagents/agents/utils/memory.py`

```python
class Memory:
    """Agent memory manager"""
    
    def get_memories(self, query: str, n_matches: int = 2):
    """Retrieve memories"""
        pass
    
    def add_memory(self, content: str, metadata: dict):
    """Add memory record"""
        pass
```

### Google Tool Handler
**Location**: `tradingagents/agents/utils/google_tool_handler.py`

```python
class GoogleToolCallHandler:
    """Google AI tool call handler"""
    
    def handle_tool_calls(self, response, tools, state):
    """Handle tool invocations from Google AI responses"""
        pass
```

## 📊 Performance Monitoring

### Logging System
Unified logging captures execution parameters & durations:

```python
from tradingagents.utils.logging_init import get_logger

logger = get_logger("default")
logger.info(f"📊 [Fundamentals Analyst] Analyzing: {ticker}")
logger.debug(f"📊 [DEBUG] Market info: {market_info}")
```

### Execution Tracing
Per agent metrics include:
- Inputs
- Duration
- Outputs
- Errors (if any)

## 🚀 Extension Guide

### Adding a New Analyst/Agent

1. **创建智能体文件**
```python
# tradingagents/agents/analysts/custom_analyst.py
def create_custom_analyst(llm, toolkit):
    @log_analyst_module("custom")
    def custom_analyst_node(state):
    # Custom analysis logic
        return state
    
    return custom_analyst_node
```

2. **Extend State Class**
```python
# 在 AgentState 中添加新字段
custom_report: Annotated[str, "自定义分析师报告"]
```

3. **Integrate Into Workflow**
```python
# 在图构建器中添加节点
workflow.add_node("custom_analyst", create_custom_analyst(llm, toolkit))
```

### Extending Toolkit

```python
class ExtendedToolKit(ToolKit):
    def get_custom_data(self, ticker: str):
    """Custom data retrieval tool"""
        pass
```

## 🔧 Configuration Options

### Agent Config

```python
agent_config = {
    "online_tools": True,      # enable live data
    "memory_enabled": True,    # enable memory usage
    "debug_mode": False,       # verbose debug
    "max_iterations": 10,      # iteration ceiling
}
```

### Logging Config

```python
logging_config = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "handlers": ["console", "file"]
}
```

## 🛡️ Best Practices

### 1. State Discipline
- Always mutate via `AgentState`
- Avoid ad-hoc global passing
- Preserve type annotations

### 2. Error Handling
- Local try/except with meaningful logging
- Fallback pathways for external failures
- Clear escalation boundaries

### 3. Performance
- Cache external & deterministic results
- Parallelize independent analyst phases
- Monitor memory & token consumption

### 4. Code Organization
- One file per role
- Consistent naming & suffixes
- Docstrings explain intent & side effects

The TradingAgents agent architecture—through layered role separation, unified state modeling, and extensible tooling—provides a robust foundation for reproducible, explainable multi-perspective financial decision workflows.