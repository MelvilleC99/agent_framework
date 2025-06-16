# Data Access Layer (DAL)

## 🎯 Purpose
Database abstraction layer that provides a unified interface for data operations across different database systems and data sources. Enables tools to work with any database without modification.

## 📁 Components

### **`repositories/`**
Abstract interfaces that define data operations without specifying implementation.

**Examples:**
- `maintenance_repository.py` - Interface for maintenance data operations
- `quality_repository.py` - Interface for quality control data
- `production_repository.py` - Interface for production metrics and scheduling

### **`adapters/`**
Concrete implementations for specific database systems and data sources.

**Examples:**
- `supabase_adapter.py` - Supabase/PostgreSQL implementation
- `mysql_adapter.py` - MySQL database implementation
- `api_adapter.py` - REST API data source implementation

### **`queries/`**
Reusable query templates and common data operations.

**Examples:**
- `maintenance_queries.py` - Standard maintenance data queries
- `analytics_queries.py` - Common analytical queries and aggregations
- `reporting_queries.py` - Standardized reporting queries

### **`models/`**
Data models and schemas using SQLAlchemy or similar ORM.

**Examples:**
- `maintenance_models.py` - Equipment, failures, repairs, mechanics
- `quality_models.py` - Audits, defects, inspections, standards
- `production_models.py` - Lines, products, schedules, output

## 🔄 How It Works

### **Abstraction Flow:**
1. **Tools call repository methods** (abstract interface)
2. **Repository routes to appropriate adapter** (implementation)
3. **Adapter executes database-specific operations**
4. **Results returned in standardized format**
5. **Tools receive consistent data regardless of source**

### **Integration Points:**
- **Serves:** `tools/` and `workflows/` with data access
- **Uses:** `shared_service/` for connection management
- **Supports:** `knowledge/` with structured data access
- **Enables:** Easy migration between database systems

## 🏗️ Architecture Pattern

### **Repository Pattern**
Abstract interface for data operations:
```python
# repositories/maintenance_repository.py
from abc import ABC, abstractmethod

class MaintenanceRepository(ABC):
    @abstractmethod
    def get_failures_by_date_range(self, start_date, end_date):
        pass
    
    @abstractmethod
    def get_mechanic_performance(self, mechanic_id, period_days):
        pass
    
    @abstractmethod
    def create_maintenance_record(self, maintenance_data):
        pass
```

### **Tool Using DAL**
```python
# tools/maintenance_tools/analyze_downtime_tool.py
def analyze_downtime_tool(date_range, machine_id=None):
    # Tool doesn't know or care which database is used
    maintenance_repo = get_maintenance_repository()  # Injected dependency
    
    # Standard interface call
    failures = maintenance_repo.get_failures_by_date_range(
        start_date=date_range.start,
        end_date=date_range.end,
        machine_id=machine_id
    )
    
    # Tool works with standardized data format
    analysis_results = perform_downtime_analysis(failures)
    return analysis_results
```

## 🔧 Data Operations

### **CRUD Operations**
Standard Create, Read, Update, Delete operations:
```python
class BaseRepository(ABC):
    @abstractmethod
    def create(self, entity_data):
        """Create new record"""
        pass
    
    @abstractmethod
    def get_by_id(self, entity_id):
        """Retrieve by primary key"""
        pass
    
    @abstractmethod
    def update(self, entity_id, update_data):
        """Update existing record"""
        pass
    
    @abstractmethod
    def delete(self, entity_id):
        """Delete record"""
        pass
```

### **Batch Operations**
Efficient bulk data operations:
```python
class BatchRepository(ABC):
    @abstractmethod
    def bulk_insert(self, records):
        """Insert multiple records efficiently"""
        pass
    
    @abstractmethod
    def bulk_update(self, update_specs):
        """Update multiple records in batch"""
        pass
    
    @abstractmethod
    def export_data(self, query_params, format='csv'):
        """Export data in specified format"""
        pass
```

## 🛡️ Safety & Security

### **Query Safety**
- SQL injection prevention through parameterized queries
- Input validation and sanitization
- Query complexity limits to prevent resource exhaustion

### **Access Control**
- Role-based data access permissions
- Field-level security for sensitive data
- Audit trails for all data operations

### **Data Validation**
- Schema validation before database operations
- Business rule enforcement at data layer
- Consistent error handling and reporting

## 📊 Performance Optimization

### **Caching Strategy**
```python
class CachedRepository:
    def __init__(self, base_repository, cache_manager):
        self.repo = base_repository
        self.cache = cache_manager
    
    def get_failures_by_date_range(self, start_date, end_date):
        cache_key = f"failures_{start_date}_{end_date}"
        cached_result = self.cache.get(cache_key)
        
        if cached_result:
            return cached_result
        
        result = self.repo.get_failures_by_date_range(start_date, end_date)
        self.cache.set(cache_key, result, ttl=300)  # 5 minute cache
        return result
```

### **Connection Pooling**
- Efficient database connection management
- Connection reuse and pooling
- Automatic connection recovery

### **Query Optimization**
- Indexed query patterns
- Efficient join strategies
- Pagination for large result sets

## 🔄 Migration Support

### **Database Migration**
Easy switching between database systems:
```python
# Configuration change migrates entire system
OLD_CONFIG = {'type': 'mysql', 'host': 'old-server'}
NEW_CONFIG = {'type': 'supabase', 'url': 'new-endpoint'}

# Tools continue working without modification
# Only adapter implementation changes
```

### **Data Migration**
Tools for migrating data between systems:
```python
class DataMigrator:
    def migrate_data(self, source_repo, target_repo, table_name):
        # Extract from source
        data = source_repo.export_all_data(table_name)
        
        # Transform if needed
        transformed_data = self.transform_data(data, target_repo.schema)
        
        # Load into target
        target_repo.bulk_insert(transformed_data)
```

## 🔗 Dependencies

### **Required:**
- `shared_service/` - Database connection management
- SQLAlchemy or similar ORM framework
- Database drivers for target systems

### **Optional:**
- Caching system (Redis, Memcached)
- Connection pooling libraries
- Data validation frameworks

## 🎚️ Agent Type Usage

### **Simple Reactive Agent:** ⚠️ Optional (can use direct DB calls)
### **Monitoring Agent:** ✅ Recommended for data source flexibility
### **Autonomous Agent:** ✅ Essential for multi-source environments
### **Production Agent:** ✅ Critical for enterprise deployments

## 💡 Benefits

### **For Development**
- Write tools once, work with any database
- Easy testing with different data sources
- Simplified tool development and maintenance

### **For Deployment**
- Easy migration between database systems
- Support for hybrid data environments
- Simplified client customization

### **For Maintenance**
- Centralized data access logic
- Consistent error handling
- Simplified security and compliance

---

**The Data Access Layer enables true database independence, allowing your agent template to work with any client's existing data infrastructure while maintaining consistency and performance.**