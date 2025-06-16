# Usage Tracking Layer

The usage tracking layer provides comprehensive cost tracking, usage monitoring, and business intelligence for the agent system.

## 📁 Structure

```
analytics/
├── README.md              # This file
├── usage_tracker.py       # Real-time query tracking & database logging
├── cost_calculator.py     # LLM & compute cost calculations
├── session_summarizer.py  # Session analytics & business intelligence
├── token_tracker.py       # In-memory token usage tracking
└── __init__.py           # Package initialization
```

## 🎯 Component Overview

### **Usage Tracker** (`usage_tracker.py`)
**Purpose**: Real-time query tracking with database persistence
- Tracks individual API calls and tool usage
- Logs detailed usage data to database
- Provides cost analysis per query
- Memory usage and performance tracking

### **Cost Calculator** (`cost_calculator.py`)
**Purpose**: Comprehensive cost calculation for LLM and compute
- LLM API costs (OpenAI, DeepSeek, etc.)
- Cloud compute cost estimates
- Monthly usage projections
- Cost breakdown analysis

### **Session Summarizer** (`session_summarizer.py`)
**Purpose**: Session-level analytics and business intelligence
- Aggregates query data into session summaries
- Creates business intelligence metrics
- Conversation analysis and classification
- Usage trend analysis

### **Token Tracker** (`token_tracker.py`)
**Purpose**: Real-time session token monitoring
- In-memory token usage tracking
- Session-level token aggregation
- Real-time cost estimates
- Performance monitoring

## 🔄 Analytics Flow

### **Query Lifecycle Tracking**
```
1. usage_tracker.start_query_tracking()
2. → API calls tracked via usage_tracker.track_api_call()
3. → Tool usage tracked via usage_tracker.track_tool_usage()
4. → token_tracker.track_openai_usage() (real-time)
5. → usage_tracker.complete_query_tracking() (database)
```

### **Session Analytics**
```
1. Query data logged to agent_usage_logs table
2. → session_summarizer.create_session_summary()
3. → Aggregated data written to session_summaries table
4. → Business intelligence and reporting
```

### **Cost Calculation**
```
1. cost_calculator.calculate_llm_cost()
2. → cost_calculator.calculate_cloud_run_cost()
3. → cost_calculator.calculate_total_query_cost()
4. → Monthly projections and analysis
```

## 📊 Database Schema

### **Expected Tables**
```sql
-- Real-time usage tracking
agent_usage_logs (
    id, session_id, conversation_id, user_id,
    query_text, query_type, tools_used,
    processing_time_ms, memory_usage_mb,
    total_api_calls, total_input_tokens, total_output_tokens,
    llm_cost, estimated_compute_cost, total_cost,
    success, error_message, agent_used,
    started_at, completed_at
)

-- Session-level analytics
session_summaries (
    id, session_id, user_id,
    total_queries, successful_queries, failed_queries,
    session_duration_ms, total_cost, avg_cost_per_query,
    tools_used, main_topics, session_type,
    conversation_summary, session_ended_reason,
    session_started_at, session_ended_at
)
```

## 🔗 Integration Points

### **With Agents Layer**
```python
# ChatGPT agent integration
if self.usage_tracker:
    self.usage_tracker.track_api_call(
        conversation_id=conversation_id,
        model=self.model,
        input_tokens=input_tokens,
        output_tokens=output_tokens
    )
```

### **With Orchestration Layer**
```python
# Coordinator integration
self.usage_tracker.start_query_tracking(
    session_id=session_id,
    conversation_id=conversation_id,
    query_text=query,
    user_id=user_id
)
```

### **With API Layer**
```python
# Container initialization
usage_tracker = UsageTracker(database=database)
session_summarizer = SessionSummarizer(database=database)
```

## 💡 Key Features

### **From Industrial Engineering Agent**
- ✅ Comprehensive usage tracking (your usage_tracker.py)
- ✅ Detailed cost calculations (your cost_calculator.py)
- ✅ Session analytics (your session_summarizer.py)
- ✅ Real-time monitoring (your token_tracker.py)

### **Enhanced for Template**
- ✅ Dependency injection for database connections
- ✅ Better error handling and recovery
- ✅ Configurable cost models and pricing
- ✅ Enhanced business intelligence metrics
- ✅ Health monitoring and diagnostics

## 📈 Business Intelligence

### **Cost Analytics**
- Query-level cost breakdown
- Session-level cost aggregation
- Monthly usage projections
- Cost optimization recommendations

### **Usage Patterns**
- Peak usage times and patterns
- Tool usage frequency and effectiveness
- User behavior analysis
- Performance trend analysis

### **Quality Metrics**
- Success rate tracking
- Error pattern analysis
- Response time monitoring
- User satisfaction indicators

## 🎯 Design Principles

### **Based on Industrial Engineering Agent**
- Preserves your excellent cost tracking architecture
- Maintains your detailed analytics approach
- Keeps your session summarization logic

### **Enhanced for Template**
- Dependency injection for loose coupling
- Better error handling and recovery
- Configurable pricing and cost models
- Enhanced business intelligence capabilities
