# QC Agent Template - Setup Guide

## 🚀 Quick Start

### 1. Environment Configuration

Create a `.env` file in the project root:

```bash
# Required - Database Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here

# Required - LLM API Keys  
OPENAI_API_KEY=your_openai_api_key_here

# Optional - Advanced Configuration
REDIS_URL=redis://localhost:6379
RATE_LIMIT_PER_MINUTE=60
ENVIRONMENT=development

# Optional - Disable Analytics (for template mode)
DISABLE_ANALYTICS=false
```

### 2. Database Setup Options

#### Option A: Automatic Setup (Recommended)
1. Run the agent - it will detect missing tables
2. Execute the provided SQL in your database
3. Restart the agent

#### Option B: Template Mode (No Database)
Set `DISABLE_ANALYTICS=true` to run without database persistence.

#### Option C: Manual Setup
Execute this SQL in your PostgreSQL/Supabase database:

```sql
-- Agent usage tracking table
CREATE TABLE IF NOT EXISTS agent_usage_logs (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    conversation_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255),
    query_text TEXT,
    query_type VARCHAR(100),
    tools_used TEXT[],
    processing_time_ms INTEGER,
    memory_usage_mb FLOAT,
    total_api_calls INTEGER DEFAULT 0,
    total_input_tokens INTEGER DEFAULT 0,
    total_output_tokens INTEGER DEFAULT 0,
    llm_cost DECIMAL(10,6) DEFAULT 0.00,
    estimated_compute_cost DECIMAL(10,6) DEFAULT 0.00,
    total_cost DECIMAL(10,6) DEFAULT 0.00,
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    agent_used VARCHAR(100),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Session summaries table
CREATE TABLE IF NOT EXISTS session_summaries (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255),
    total_queries INTEGER DEFAULT 0,
    successful_queries INTEGER DEFAULT 0,
    failed_queries INTEGER DEFAULT 0,
    session_duration_ms INTEGER,
    total_cost DECIMAL(10,6) DEFAULT 0.00,
    avg_cost_per_query DECIMAL(10,6) DEFAULT 0.00,
    tools_used TEXT[],
    main_topics TEXT[],
    session_type VARCHAR(100),
    conversation_summary TEXT,
    session_ended_reason VARCHAR(100),
    session_started_at TIMESTAMP WITH TIME ZONE,
    session_ended_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_agent_usage_logs_session_id ON agent_usage_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_session_summaries_session_id ON session_summaries(session_id);
```

### 3. Add Your Domain Tools

Create tools in `src/tools/` directory:

```python
# src/tools/my_analysis_tool.py

def analyze_data(input_data: str, analysis_type: str = "basic") -> dict:
    """
    Analyze input data and return results.
    
    Args:
        input_data: Data to analyze
        analysis_type: Type of analysis to perform
        
    Returns:
        Analysis results
    """
    # Your implementation here
    return {
        "success": True,
        "result": f"Analyzed {len(input_data)} characters with {analysis_type} analysis",
        "analysis_type": analysis_type,
        "data_length": len(input_data)
    }
```

### 4. Run the Agent

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API server
cd /Users/melville/Documents/qc_agent_backend
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Test the Setup

```bash
# Health check
curl http://localhost:8000/health

# List available tools
curl http://localhost:8000/admin/tools

# Chat with the agent
curl -X POST http://localhost:8000/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello, what tools do you have?", "user_id": "test_user"}'
```

## 🔧 Customization Guide

### For Different Domains

1. **Replace Tools**: Add your domain-specific tools in `src/tools/`
2. **Update Prompts**: Customize system prompts for your use case
3. **Modify Categories**: Adjust tool categories in the registry
4. **Add Endpoints**: Create domain-specific API endpoints

### Tool Development

Tools are automatically discovered if they:
- Are Python functions in `src/tools/*.py` files
- Have descriptive names (not starting with `_`)
- Have proper docstrings
- Follow naming conventions

### Categories

- `data_retrieval`: Database queries, information lookup
- `analysis`: Data analysis, reporting, calculations  
- `action`: Data modification, system actions
- `maintenance`: System maintenance, health checks
- `notification`: Alerts, messages, communications

## 🚨 Troubleshooting

### Database Connection Issues
1. Check your `SUPABASE_URL` and `SUPABASE_KEY`
2. Ensure database is accessible
3. Try template mode: `DISABLE_ANALYTICS=true`

### Tool Discovery Issues
1. Check tool function names and docstrings
2. Use `/admin/discover-tools` endpoint
3. Check logs for discovery errors

### Missing Dependencies
```bash
pip install fastapi uvicorn supabase redis python-dotenv pydantic
```

## 📊 Monitoring

### Available Endpoints

- `GET /health` - System health check
- `GET /admin/tools` - List all tools
- `GET /admin/functions` - OpenAI function definitions
- `POST /admin/tools/execute` - Execute tools (admin)
- `POST /admin/discover-tools` - Discover new tools

### Analytics

When enabled, the system tracks:
- Query-level usage and costs
- Session-level analytics
- Tool usage patterns
- Performance metrics

## 🎯 Template Benefits

✅ **Plug & Play**: No domain-specific code in core template  
✅ **Auto-Discovery**: Tools automatically registered  
✅ **Database Optional**: Works with or without persistence  
✅ **Production Ready**: Error handling, monitoring, rate limiting  
✅ **Highly Configurable**: Environment-driven configuration  
✅ **Analytics Built-in**: Cost tracking and usage monitoring  

The template preserves your excellent Industrial Engineering Agent architecture while making it reusable across any domain!