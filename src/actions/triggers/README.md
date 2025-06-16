# Triggers

## 🎯 Purpose
Execute tools and workflows based on specific conditions detected by monitoring and decision layers.

## 📝 What Goes Here
- **Condition triggers** - "If downtime > threshold, execute analysis tool"
- **Event triggers** - "If new failure record, run pattern analysis"
- **Compound triggers** - "If multiple conditions met, execute workflow"
- **Recovery triggers** - "If system recovery detected, update status"

## 🔧 Implementation Pattern
```python
class ConditionTrigger:
    def __init__(self, orchestrator, condition_spec):
        self.orchestrator = orchestrator
        self.condition = condition_spec
    
    def evaluate_condition(self, event_data):
        # Check if trigger condition is met
        pass
    
    def execute_action(self, trigger_context):
        # Call appropriate tool or workflow
        self.orchestrator.execute_tool(self.condition.tool_name, trigger_context)
```

## 🔗 Connections
- **Receives from:** `decisions/` layer (action decisions)
- **Executes:** `tools/` and `workflows/` via `orchestration/`
- **Reports to:** `learning/` for outcome tracking