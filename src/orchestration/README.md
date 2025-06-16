# Orchestration Layer

The orchestration layer coordinates agent interactions, manages conversation context, and handles session lifecycles.

## 📁 Structure

```
orchestration/
├── README.md              # This file
├── coordinator.py         # Main orchestrator (enhanced two-tier)
├── context_manager.py     # Conversation history & metadata
├── session_manager.py     # Session lifecycle management
└── __init__.py           # Package initialization
```

## 🧠 How It Works

### **1. Request Flow**
```
API Request → Coordinator → Context Manager → Agent → Response
```

### **2. Components**

#### **Context Manager**
- Stores conversation history
- Manages query metadata for follow-ups
- Provides context for agent handoffs
- Handles conversation summarization

#### **Session Manager** 
- Tracks session lifecycle
- Handles timeouts and expiration
- Manages session persistence
- Coordinates session cleanup

#### **Coordinator (Main Orchestrator)**
- Routes queries between ChatGPT and DeepSeek
- Manages agent handoffs
- Integrates cost tracking
- Handles error fallbacks

## 🔄 Agent Handoff Logic

### **ChatGPT → DeepSeek Handoff**
1. ChatGPT processes query
2. Checks if response indicates need for DeepSeek
3. If yes, passes context to DeepSeek
4. DeepSeek provides enhanced analysis
5. Result returned to user

### **Context Preservation**
- Conversation history maintained across handoffs
- Query metadata preserved for follow-up questions
- Session state consistent across agents

## 🎯 Key Features

### **Dependency Injection**
All components receive dependencies instead of creating them:
```python
coordinator = Coordinator(
    database=injected_db,
    redis=injected_redis,
    tool_registry=injected_tools
)
```

### **Enhanced Error Handling**
- Graceful fallbacks when agents fail
- Structured error responses
- Recovery mechanisms for partial failures

### **Cost Tracking Integration**
- Real-time token usage tracking
- Session-level cost aggregation
- Usage analytics and reporting

## 🔗 Integration Points

### **With API Layer**
```python
# In routes/chat.py
orchestrator = request.app.state.orchestrator
result = await orchestrator.process_query(query, user_id)
```

### **With Agents Layer**
```python
# Coordinator manages agent instances
self.chatgpt_agent = ChatGPTAgent(database=database)
self.deepseek_agent = DeepSeekAgent(database=database)
```

### **With Analytics Layer**
```python
# Cost tracking integration
self.usage_tracker = UsageTracker(database=database)
self.session_summarizer = SessionSummarizer(database=database)
```

## 📊 Session Lifecycle

### **1. Session Creation**
- New session ID generated
- Context manager initialized
- Session tracking started

### **2. Active Session**
- Queries processed through coordinator
- Context updated with each interaction
- Activity timestamps maintained

### **3. Session End**
- Triggered by timeout or explicit goodbye
- Session summary created
- Resources cleaned up
- Analytics written to database

## 🎯 Design Principles

### **Based on Industrial Engineering Agent**
- Preserves your excellent two-tier architecture
- Maintains your session management patterns
- Keeps your cost tracking integration

### **Enhanced for Template**
- Dependency injection for loose coupling
- Better error handling and recovery
- Cleaner interfaces for extensibility
- Comprehensive documentation
