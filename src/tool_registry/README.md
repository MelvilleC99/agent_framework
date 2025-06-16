# Tools Layer

This directory contains the complete tools system for the QC Agent Template, based on the excellent Industrial Engineering Agent tool architecture.

## Architecture

The tools layer provides:
- **Tool Registry**: Centralized tool registration and management
- **Tool Executor**: Generic tool execution framework
- **Tool Discovery**: Automatic tool discovery from directories
- **Function Generator**: OpenAI function definition generation
- **Tool Interfaces**: Standardized tool interfaces

## Key Components

### `registry.py`
- Central tool registration and management
- Tool categorization and metadata
- Parameter validation and documentation
- Integration with agent function calling

### `executor.py`
- Generic tool execution framework
- Error handling and logging
- Result formatting and validation
- Replaces manual if/elif execution chains

### `discovery.py`
- Automatic tool discovery from directories
- Dynamic tool registration
- File system scanning and module loading
- Convention-based tool identification

### `function_generator.py`
- Generate OpenAI function definitions from tool metadata
- Convert tool registry to ChatGPT function calling format
- Parameter validation and type conversion
- Dynamic function definition updates
## Integration

The tools layer integrates with:
- **Agents Layer**: Provides tools for agent function calling
- **Analytics Layer**: Tracks tool usage and performance
- **API Layer**: Exposes tool management endpoints
- **Orchestration Layer**: Manages tool execution coordination

## Usage

```python
from tools.registry import tool_registry
from tools.executor import ToolExecutor
from tools.function_generator import FunctionGenerator

# Register tools
tool_registry.register_tool(
    name="example_tool",
    function=my_function,
    description="Example tool description",
    category="data_retrieval"
)

# Execute tools
executor = ToolExecutor(tool_registry)
result = executor.execute("example_tool", {"param": "value"})

# Generate function definitions
generator = FunctionGenerator(tool_registry)
functions = generator.generate_function_definitions()
```

## Tool Categories

- **data_retrieval**: Database queries, information lookup
- **analysis**: Data analysis, reporting, calculations
- **action**: Data modification, system actions
- **maintenance**: System maintenance, health checks
- **notification**: Alerts, messages, communications

## Convention

Tools follow a standard interface:
- Accept keyword arguments
- Return structured data
- Include proper error handling
- Provide comprehensive documentation
- Support parameter validation```

### **2. Intelligent Function Grouping**
```python
# ChatGPT gets tools organized by purpose:
# - Data tools for information gathering
# - Analysis tools for processing
# - Action tools for modifications
# This helps the AI choose appropriate tools
```

### **3. Auto-Categorization Reduces Setup**
```python
# User just creates:
def analyze_sales_tool(data): ...     # → "analysis" category
def query_customers_tool(filters): ... # → "data_retrieval" category
def send_alert_tool(message): ...      # → "notification" category

# No manual category assignment needed!
```

### **4. Better Admin Interface**
- Tools grouped by purpose in admin panel
- Easier to find specific types of tools
- Clear organization for debugging

### **5. Future Extensibility**
- Could limit certain categories to specific users
- Could generate different function groups for different agents
- Could apply category-specific validation rules

## 🚫 **What Users DON'T Touch**

Users should **never edit** files in `tool_registry/`:
- ✅ Users add tools to `src/tools/`
- ✅ Tools are automatically discovered
- ✅ Categories are automatically assigned
- ❌ No need to edit registry files

## 🔧 Configuration

### Environment Variables
```bash
# Tool discovery configuration
TOOLS_DIRECTORY=src/tools          # Where to find user tools
DISABLE_ANALYTICS=false            # Enable/disable analytics
```

### Settings
```python
class Settings:
    tools_directory: str = "src/tools"  # Configurable tool location
```

## 📊 Usage Statistics

The registry tracks:
- Number of tools registered
- Tools by category
- Discovery success/failure rates
- Tool execution statistics (when analytics enabled)

## 🎯 Summary

**The tool registry system provides:**

✅ **Automatic Discovery**: Drop tools in folder → automatically registered  
✅ **Strict Validation**: Clear naming rules prevent confusion  
✅ **Smart Categorization**: Tools automatically organized by purpose  
✅ **Detailed Logging**: Easy debugging when things go wrong  
✅ **Zero Configuration**: Works out of the box  
✅ **Production Ready**: Error handling, deduplication, health checks  

**Users just need to:**
1. Create functions ending with `_tool`
2. Add proper docstrings
3. Put files in `src/tools/`
4. Restart agent → tools available!
## 🛠️ Tool Discovery Rules (UPDATED - Fixed Issues)

### **STRICT REQUIREMENTS (No More Broad Matching):**
1. Function name **MUST end with `_tool`** (exact suffix required)
2. Function **MUST have a docstring**
3. Function **SHOULD return a dictionary**

### **SAFETY FEATURES (Fixed Architecture Issues):**
- ✅ **Duplicate Protection**: Prevents re-registering existing tools
- ✅ **Safe Re-scanning**: Auto-discovery can run multiple times safely
- ✅ **No Broad Matching**: Only `_tool` suffix (removed "contains tool" rule)
- ✅ **Clean Logging**: Registry logs details, executor only logs errors
- ✅ **No Registration Overlap**: Manual and auto-discovery work together safely

### **DISCOVERY LOGGING (Improved):**

When tools are discovered, you'll see clean, informative logs:

```
🔍 Starting tool discovery in: /path/to/tools
📋 Tool naming rules: Functions must end with '_tool' and have docstrings
✅ TOOL DISCOVERY SUMMARY
📁 Directory scanned: /path/to/tools
🛠️  Tools discovered: 3
📋 REGISTERED TOOLS:
   ✅ analyze_quality_tool (from analysis_tools.py)
   ✅ query_database_tool (from database_tools.py)
   ✅ send_notification_tool (from notification_tools.py)

# Duplicate protection in action:
⏭️  Tool analyze_quality_tool already registered - skipping duplicate

💡 REMINDER: Functions must end with '_tool' and have docstrings
```

### **FIXED ISSUES:**
1. ❌ **Before**: "tool" in name could register anything with "tool" 
   ✅ **After**: Only `_tool` suffix registers tools

2. ❌ **Before**: Manual + auto registration could create duplicates
   ✅ **After**: Duplicate checking prevents conflicts

3. ❌ **Before**: Both executor and registry logged same events
   ✅ **After**: Clean, non-duplicate logging

4. ❌ **Before**: No protection against re-running discovery
   ✅ **After**: Safe to run discovery multiple times
