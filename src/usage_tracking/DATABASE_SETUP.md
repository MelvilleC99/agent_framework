# Usage Tracking Database Setup

The usage tracking system requires two database tables to store analytics data.

## 📊 Required Tables

### 1. `agent_usage_logs` - Query-level tracking
Stores detailed information about each query processed by the agent.

### 2. `session_summaries` - Session-level analytics  
Stores aggregated session information and summaries.

## 🗄️ **Complete Database Setup SQL**

Execute this SQL in your PostgreSQL/Supabase database:

```sql
-- ============================================================================
-- USAGE TRACKING TABLES
-- ============================================================================

-- Table 1: Query-level usage tracking
CREATE TABLE IF NOT EXISTS agent_usage_logs (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    conversation_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255),
    query_text TEXT,
    query_type VARCHAR(100),
    tools_used TEXT[], -- Array of tool names
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

-- Table 2: Session-level analytics
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
    tools_used TEXT[], -- Array of tool names
    main_topics TEXT[], -- Array of main topics discussed
    session_type VARCHAR(100),
    conversation_summary TEXT,
    session_ended_reason VARCHAR(100),
    session_started_at TIMESTAMP WITH TIME ZONE,
    session_ended_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- PERFORMANCE INDEXES
-- ============================================================================

-- Indexes for agent_usage_logs
CREATE INDEX IF NOT EXISTS idx_agent_usage_logs_session_id ON agent_usage_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_agent_usage_logs_user_id ON agent_usage_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_agent_usage_logs_created_at ON agent_usage_logs(created_at);

-- Indexes for session_summaries  
CREATE INDEX IF NOT EXISTS idx_session_summaries_session_id ON session_summaries(session_id);
CREATE INDEX IF NOT EXISTS idx_session_summaries_user_id ON session_summaries(user_id);
CREATE INDEX IF NOT EXISTS idx_session_summaries_created_at ON session_summaries(created_at);
```

## 🔧 Setup Options

### Option 1: Manual Setup (Recommended)
1. Copy the SQL above
2. Execute in your PostgreSQL/Supabase SQL editor
3. Verify tables exist

### Option 2: Automatic Detection
The agent will detect missing tables on startup and provide the SQL to run:

```bash
# Start the agent - it will check for tables
python -m uvicorn src.api.main:app --reload

# If tables are missing, you'll see:
# ⚠️  Database setup required - analytics will be disabled
# [SQL provided in logs]
```

### Option 3: Template Mode (No Database)
```bash
# In .env file
DISABLE_ANALYTICS=true

# Usage tracking runs in memory only (no persistence)
```

## 📋 **Table Purposes**

| Table | Purpose | When Written |
|-------|---------|--------------|
| `agent_usage_logs` | Track every query | During chat processing |
| `session_summaries` | Session analytics | When session ends |

## 🔍 **Data Flow**

```
User Query → chat.py → orchestrator → usage_tracker → agent_usage_logs
Session End → orchestrator → session_summarizer → session_summaries
```

## 🛠️ **Testing Tables**

After setup, verify tables exist:

```sql
-- Check tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('agent_usage_logs', 'session_summaries');

-- Check table structure
\d agent_usage_logs
\d session_summaries
```
