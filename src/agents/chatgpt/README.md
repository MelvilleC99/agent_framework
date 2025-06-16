# ChatGPT Agent

Modular ChatGPT agent implementation based on the Industrial Engineering Agent's excellent architecture.

## 📁 Structure

```
chatgpt/
├── README.md              # This file
├── core_agent.py          # Main agent orchestrator
├── prompt_manager.py      # System prompts & date handling
├── message_builder.py     # OpenAI message formatting
├── response_handler.py    # Function call processing
├── session_detector.py    # Session management logic
├── context_helpers.py     # Context utilities
└── __init__.py           # Package initialization
```

## 🧠 Modular Architecture

This implementation preserves the excellent modular design from the Industrial Engineering Agent:

### **Core Agent** (`core_agent.py`)
- **Purpose**: Main orchestrator that coordinates all components
- **Responsibilities**: Query processing, component coordination, error handling
- **Enhanced**: Dependency injection, better error recovery

### **Prompt Manager** (`prompt_manager.py`)
- **Purpose**: System prompt loading and date management  
- **Responsibilities**: Prompt caching, date injection, prompt refresh
- **Enhanced**: Configurable prompt paths, better date handling

### **Message Builder** (`message_builder.py`)
- **Purpose**: OpenAI message formatting and conversation preparation
- **Responsibilities**: Message construction, history injection, token optimization
- **Enhanced**: Better token management, improved formatting

### **Response Handler** (`response_handler.py`)
- **Purpose**: Function call processing and output formatting
- **Responsibilities**: Function execution, result formatting, error handling
- **Enhanced**: Better error recovery, improved formatting

### **Session Detector** (`session_detector.py`)
- **Purpose**: Session management and conversation flow detection
- **Responsibilities**: Goodbye detection, handoff logic, session state
- **Enhanced**: More robust detection patterns

### **Context Helpers** (`context_helpers.py`)
- **Purpose**: Context utilities and metadata management
- **Responsibilities**: Query metadata, context extraction, follow-up support
- **Enhanced**: Better metadata handling

## 🔄 Component Interaction

```
core_agent.process_query()
├── prompt_manager.get_system_prompt()
├── message_builder.build_messages()
├── OpenAI API call
├── response_handler.format_function_result()
├── session_detector.is_goodbye_message()
└── Return formatted response
```

## 🎯 Key Features

### **From Industrial Engineering Agent**
- ✅ Excellent modular design preserved
- ✅ Function calling with tool registry
- ✅ System prompt management with date injection
- ✅ Session detection and management
- ✅ Context-aware responses

### **Enhanced for Template**
- ✅ Dependency injection throughout
- ✅ Better error handling and recovery
- ✅ Configurable prompt paths
- ✅ Health monitoring
- ✅ Usage tracking integration

## 🔧 Configuration

The agent can be configured through environment variables:

```bash
# System prompt path (optional)
CHATGPT_SYSTEM_PROMPT_PATH="/path/to/system_prompt.txt"

# Model configuration
OPENAI_MODEL="gpt-4o-mini"
OPENAI_MAX_TOKENS=500

# Agent behavior
MAX_CONTEXT_HISTORY=6
ENABLE_FUNCTION_CALLING=true
```

## 🔗 Usage

```python
# Initialize with dependencies
agent = ChatGPTAgent(
    tool_registry=tool_registry,
    context_manager=context_manager,
    database=database
)

# Process query
result = agent.process_query(
    query="Hello, how are you?",
    conversation_history=history,
    conversation_id="conv_123"
)

# Result format
{
    "answer": "Response text",
    "response": message_object,
    "requires_deepseek": False,
    "is_goodbye": False
}
```
