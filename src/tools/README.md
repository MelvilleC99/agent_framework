# Tools Directory - User Guide

This directory is where you add your domain-specific tools. Tools placed here are **automatically discovered** and registered with the agent system.

## 🛠️ Tool Creation Rules

### **REQUIRED: Strict Naming Convention**
- Function names **MUST end with `_tool`** (strict requirement)
- Function **MUST have a docstring**  
- Function **should return a dictionary**

### ✅ **Valid Tool Examples:**

```python
# tools/analysis_tools.py

def analyze_quality_tool(product_id: str, metric_type: str = "defect_rate") -> dict:
    """
    Analyze quality metrics for a specific product.
    
    Args:
        product_id: ID of the product to analyze
        metric_type: Type of metric (defect_rate, compliance, etc.)
        
    Returns:
        Quality analysis results
    """
    # Your implementation here
    analysis_result = {
        "product_id": product_id,
        "metric_type": metric_type,
        "defect_rate": 0.02,
        "compliance_score": 98.5,
        "recommendations": ["Continue current processes"]
    }
    
    return {
        "success": True,
        "data": analysis_result
    }


def query_database_tool(table: str, filters: dict = None) -> dict:
    """
    Query database for specific data.
    
    Args:
        table: Database table to query
        filters: Optional filter conditions
        
    Returns:
        Query results
    """
    # Your database query logic here
    return {
        "success": True,
        "data": [{"id": 1, "name": "Product A"}],
        "total_records": 1
    }


def send_notification_tool(message: str, recipient: str = "admin") -> dict:
    """
    Send notification message to specified recipient.
    
    Args:
        message: Notification message
        recipient: Who to send to
        
    Returns:
        Send status
    """
    # Your notification logic here
    return {
        "success": True,
        "message_sent": True,
        "recipient": recipient
    }
```

### ❌ **What Gets Skipped:**

```python
# These functions will NOT be registered as tools:

def helper_function(data):          # ❌ Doesn't end with '_tool'
    return data

def _private_tool(data):            # ❌ Starts with underscore  
    return data

def process_data_tool(data):        # ❌ Missing docstring
    return {"result": data}

def main():                         # ❌ Reserved function name
    pass

def analyze_data(data):             # ❌ Doesn't end with '_tool'
    return data
```

## 🔍 **Discovery Rules (Updated)**

**STRICT REQUIREMENTS:**
1. ✅ Function name ends with `_tool` 
2. ✅ Function has docstring
3. ✅ Function is not private (no `_` prefix)
4. ✅ Function is not reserved name (`main`, `test`, `setup`, `init`)

**AUTOMATIC FEATURES:**
- 🚫 **Duplicate Protection**: Won't register the same tool twice
- 🔄 **Safe Re-scanning**: Can run discovery multiple times safely  
- 📂 **Auto-categorization**: Tools categorized by name/description
- 📝 **Clear Logging**: See exactly what was found/skipped

## 📁 **Recommended File Organization**

```
tools/
├── analysis_tools.py       # Data analysis, reporting, calculations
├── database_tools.py       # Database queries, data retrieval  
├── integration_tools.py    # External API calls, integrations
├── utility_tools.py        # Helper functions, utilities
└── notification_tools.py   # Alerts, messages, communications
```

## 🔄 **Auto-Categorization**

Tools are automatically categorized based on their names and descriptions:

- **data_retrieval**: `query_*`, `get_*`, `fetch_*`, `search_*`
- **analysis**: `analyze_*`, `calculate_*`, `report_*`
- **action**: `update_*`, `create_*`, `delete_*`, `save_*`
- **maintenance**: `health_*`, `check_*`, `status_*`
- **notification**: `notify_*`, `alert_*`, `send_*`

## 🚀 **Getting Started**

1. **Create a tool file:**
   ```bash
   touch tools/my_domain_tools.py
   ```

2. **Add your first tool:**
   ```python
   def hello_world_tool() -> dict:
       """A simple hello world tool for testing."""
       return {"message": "Hello from my tool!"}
   ```

3. **Restart the agent** - your tool will be automatically discovered

4. **Test it:**
   ```bash
   # Check if tool was registered
   curl http://localhost:8000/admin/tools
   
   # Use the tool via chat
   curl -X POST http://localhost:8000/api/agent/chat \
     -H "Content-Type: application/json" \
     -d '{"query": "Use the hello world tool", "user_id": "test"}'
   ```

## 🔍 **Debugging Tool Discovery**

### **Check Discovery Logs**
When the agent starts, look for:
```
🔍 Starting tool discovery in: /path/to/tools
📋 Tool naming rules: Functions must end with '_tool' and have docstrings
✅ TOOL DISCOVERY SUMMARY
📁 Directory scanned: /path/to/tools
🛠️  Tools discovered: 3
📋 REGISTERED TOOLS:
   ✅ analyze_quality_tool (from analysis_tools.py)
   ✅ query_database_tool (from database_tools.py)
```

### **Manual Re-Discovery**
```bash
# Force re-scan for new tools
curl -X POST http://localhost:8000/admin/discover-tools
```

### **Common Issues**

| Issue | Solution |
|-------|----------|
| "Tool not found" | Check function name ends with `_tool` |
| "Missing docstring" | Add docstring to your function |
| "Function skipped" | Ensure function is not private (`_name`) |
| "Import error" | Check Python syntax in your tool file |

## 💡 **Best Practices**

1. **Clear Naming**: Use descriptive names that indicate purpose
   ```python
   # Good
   def analyze_sales_data_tool(...)
   def query_customer_database_tool(...)
   
   # Avoid  
   def tool1(...)
   def process_tool(...)
   ```

2. **Good Docstrings**: Include purpose, parameters, and return format
   ```python
   def my_tool(param1: str, param2: int = 10) -> dict:
       """
       Brief description of what the tool does.
       
       Args:
           param1: Description of first parameter
           param2: Description of second parameter (default: 10)
           
       Returns:
           Dictionary with 'success' boolean and 'data' containing results
       """
   ```

3. **Consistent Return Format**: Always return dictionaries with status
   ```python
   # Successful result
   return {
       "success": True,
       "data": your_result_data
   }
   
   # Error result  
   return {
       "success": False,
       "error": "Description of what went wrong"
   }
   ```

4. **Error Handling**: Include try/catch blocks
   ```python
   def risky_operation_tool(data: str) -> dict:
       """Process data that might fail."""
       try:
           result = dangerous_operation(data)
           return {"success": True, "data": result}
       except Exception as e:
           return {"success": False, "error": str(e)}
   ```

## 📊 **Categories Explained**

| Category | Purpose | Examples |
|----------|---------|----------|
| **data_retrieval** | Getting data from sources | Database queries, API calls, file reading |
| **analysis** | Processing and analyzing data | Calculations, reports, metrics |
| **action** | Modifying or creating data | Updates, inserts, file writes |
| **maintenance** | System health and diagnostics | Health checks, cleanup, status |
| **notification** | Communications and alerts | Emails, messages, notifications |

Tools are automatically categorized, but you can also check categories via:
```bash
curl http://localhost:8000/admin/tools/category/analysis
```

---

**Need help?** Check the agent logs for detailed discovery information, or use the admin endpoints to inspect registered tools.
