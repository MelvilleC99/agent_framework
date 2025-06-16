# Agents Layer

The agents layer contains LLM agent implementations with modular, specialized components.

## 📁 Structure

```
agents/
├── README.md              # This file
├── base/                  # Base interfaces and shared components
│   ├── README.md         # Base agent documentation
│   ├── agent_interface.py # Abstract base agent
│   └── __init__.py       # Package initialization
├── chatgpt/              # ChatGPT agent implementation
│   ├── README.md         # ChatGPT agent documentation
│   ├── core_agent.py     # Main ChatGPT orchestrator
│   ├── prompt_manager.py # System prompts & date handling
│   ├── message_builder.py # OpenAI message formatting
│   ├── response_handler.py # Function call processing
│   ├── session_detector.py # Session management logic
│   ├── context_helpers.py # Context utilities
│   └── __init__.py       # Package initialization
└── deepseek/             # DeepSeek agent (future implementation)
    ├── README.md
    ├── core_agent.py
    └── __init__.py
```

## 🧠 Agent Architecture

### **Modular Design Pattern**
Each agent follows the same modular pattern established by the Industrial Engineering Agent's ChatGPT implementation:

1. **Core Agent**: Main orchestrator that coordinates components
2. **Prompt Manager**: Handles system prompts and date injection
3. **Message Builder**: Formats messages for the LLM API
4. **Response Handler**: Processes LLM responses and function calls
5. **Session Detector**: Manages session logic (goodbye detection, etc.)
6. **Context Helpers**: Provides context utilities and metadata

### **Dependency Injection**
All agents receive dependencies rather than creating them:
```python
agent = ChatGPTAgent(
    tool_registry=injected_tools,
    context_manager=injected_context,
    database=injected_db
)
```

## 🔄 Agent Interaction Flow

### **Query Processing**
```
1. Coordinator → core_agent.process_query()
2. → prompt_manager.get_system_prompt()
3. → message_builder.build_messages()
4. → OpenAI API call
5. → response_handler.format_function_result()
6. → session_detector.is_goodbye_message()
7. → Return formatted response
```

### **Function Call Handling**
```
1. OpenAI returns function call
2. → response_handler processes function call
3. → tool_executor executes the tool
4. → response_handler formats result
5. → Return to OpenAI for final response
```

## 🎯 Key Features

### **Based on Industrial Engineering Agent**
- ✅ Preserves your excellent modular ChatGPT structure
- ✅ Maintains your prompt management patterns
- ✅ Keeps your session detection logic
- ✅ Preserves your response handling

### **Enhanced for Template**
- ✅ Dependency injection throughout
- ✅ Better error handling and recovery
- ✅ Standardized interfaces
- ✅ Comprehensive documentation

## 🔗 Integration Points

### **With Orchestration Layer**
```python
# coordinator.py
self.chatgpt_agent = ChatGPTAgent(
    tool_registry=self.tool_registry,
    context_manager=self.context_manager
)
```

### **With Tools Layer**
```python
# Agents use injected tool registry
result = self.tool_executor.execute(function_name, arguments)
```

### **With Analytics Layer**
```python
# Cost tracking integration
self.usage_tracker.track_api_call(conversation_id, model, tokens)
```

## 🔧 Adding New Agents

To add a new agent (e.g., Claude):

1. **Create agent directory**: `agents/claude/`
2. **Implement base interface**: Extend `BaseAgent`
3. **Follow modular pattern**: Create specialized components
4. **Add to coordinator**: Register in `coordinator.py`

## 📊 Agent Capabilities

### **ChatGPT Agent**
- Function calling with tool registry
- System prompt management with date injection
- Session detection and management
- Context-aware responses
- Cost tracking integration

### **Future Agents**
- **DeepSeek**: Complex analysis and reasoning
- **Claude**: Enhanced conversation and analysis
- **Custom**: Domain-specific agents
