# Data Watchers

## 🎯 Purpose
Continuously monitor live data sources for changes, updates, and significant events that may require agent attention.

## 📝 What Goes Here
- **Production monitors** - Watch live production dashboards and metrics
- **Database watchers** - Monitor database tables for new records or changes
- **API monitors** - Poll external APIs for data updates
- **File system watchers** - Monitor for new files or data uploads

## 🔧 Implementation Pattern
```python
class DataWatcher:
    def __init__(self, data_source, polling_interval=60):
        self.data_source = data_source
        self.polling_interval = polling_interval
    
    def start_monitoring(self):
        # Continuous monitoring loop
        pass
    
    def on_data_change(self, change_event):
        # Send to event detectors for analysis
        pass
```

## 🔗 Connections
- **Sends data to:** `../event_detectors/` for analysis
- **Uses:** `shared_service/` for data connections
- **Triggers:** `decisions/` layer when immediate action needed