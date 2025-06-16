# Base Agent Components

This folder contains the abstract base interfaces and shared components for all agents.

## 📁 Files

- **`agent_interface.py`** - Abstract base agent interface
- **`__init__.py`** - Package initialization

## 🎯 Purpose

The base agent interface ensures consistency across all agent implementations:

### **Abstract Methods**
All agents must implement:
- `process_query()` - Main query processing
- `initialize()` - Agent initialization
- `cleanup()` - Resource cleanup

### **Common Patterns**
- Dependency injection for all external dependencies
- Consistent error handling and logging
- Standardized response format
- Health check capabilities

## 🔧 Usage

```python
from ..base.agent_interface import BaseAgent

class ChatGPTAgent(BaseAgent):
    def process_query(self, query: str, **kwargs) -> Dict[str, Any]:
        # Implementation here
        pass
        
    def initialize(self) -> bool:
        # Initialization logic
        pass
        
    def cleanup(self) -> None:
        # Cleanup logic
        pass
```

## 📊 Benefits

- **Consistency**: All agents follow same interface
- **Maintainability**: Easy to add new agents
- **Testing**: Standardized testing patterns
- **Documentation**: Clear contracts and expectations
