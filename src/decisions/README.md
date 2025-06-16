# Decisions Layer

## 🎯 Purpose
Centralized decision-making framework that determines when and how agents should respond to detected conditions. Provides consistent, configurable decision logic across all agent operations.

## 📁 Components

### **`thresholds/`**
Define acceptable operating ranges and trigger points for various metrics.

**Examples:**
- `maintenance_thresholds.py` - "Downtime > 4 hours = critical"
- `quality_thresholds.py` - "Defect rate > 5% = immediate review"
- `production_thresholds.py` - "Efficiency < 85% = performance concern"

### **`matrices/`**
Multi-criteria decision frameworks for complex evaluations.

**Examples:**
- `priority_matrix.py` - Determines urgency based on multiple factors
- `resource_allocation_matrix.py` - Optimizes mechanic/resource assignment
- `escalation_matrix.py` - When to involve humans vs autonomous action

### **`escalation_rules/`**
Define when and how to escalate issues to different stakeholders.

**Examples:**
- `maintenance_escalation.py` - Supervisor → Manager → Director escalation
- `quality_escalation.py` - Inspector → QC Manager → Production Manager
- `emergency_escalation.py` - Immediate escalation for safety concerns

## 🔄 How It Works

### **Decision Flow:**
1. **Monitoring layer** detects condition
2. **Thresholds** determine if condition is significant
3. **Matrices** evaluate complexity and priority
4. **Escalation rules** determine appropriate response level
5. **Actions layer** receives decision for execution

### **Integration Points:**
- **Receives from:** `monitoring/` layer (detected conditions)
- **Sends to:** `actions/` layer (execution decisions)
- **Uses:** `knowledge/` for historical context
- **Updates:** `learning/` with decision outcomes

## 🧠 Decision Framework Types

### **Threshold-Based Decisions**
Simple binary decisions based on single metrics:
```
IF downtime > 4_hours THEN severity = "critical"
IF defect_rate > 5% THEN action = "immediate_review"
```

### **Matrix-Based Decisions**
Multi-factor analysis for complex situations:
```
Priority = (Impact × Urgency × Frequency) / Resource_Availability
```

### **Rule-Based Decisions**
Business logic and domain expertise:
```
IF (machine_type == "critical" AND failure_count > 2) THEN 
    escalate_to = "maintenance_manager"
```

### **Adaptive Decisions**
Learning-based thresholds that adjust over time:
```
Dynamic threshold = base_threshold + seasonal_adjustment + learned_offset
```

## 🛠️ Implementation Examples

### **Maintenance Thresholds**
```python
# thresholds/maintenance_thresholds.py
MAINTENANCE_THRESHOLDS = {
    'critical_downtime': 4,  # hours
    'excessive_response_time': 20,  # minutes
    'repeat_failure_window': 30,  # minutes
    'mechanic_efficiency_threshold': 0.85  # percentage
}

def evaluate_downtime_severity(downtime_hours):
    if downtime_hours > MAINTENANCE_THRESHOLDS['critical_downtime']:
        return "critical"
    elif downtime_hours > MAINTENANCE_THRESHOLDS['critical_downtime'] * 0.75:
        return "high"
    else:
        return "normal"
```

### **Priority Matrix**
```python
# matrices/priority_matrix.py
def calculate_priority(impact, urgency, frequency, resources_available):
    base_score = (impact * urgency * frequency)
    resource_factor = 1.0 if resources_available else 0.5
    return base_score * resource_factor

def get_priority_level(score):
    if score >= 80: return "immediate"
    elif score >= 60: return "high"
    elif score >= 40: return "medium"
    else: return "low"
```

### **Escalation Rules**
```python
# escalation_rules/maintenance_escalation.py
def determine_escalation_path(severity, duration, attempts):
    if severity == "critical" and duration > 2:
        return "director"
    elif severity in ["critical", "high"] and attempts > 2:
        return "manager"
    elif severity != "low":
        return "supervisor"
    else:
        return "team_lead"
```

## ⚙️ Configuration Management

### **Threshold Configuration**
```python
# Easy adjustment of decision parameters
THRESHOLDS = {
    'factory_a': {'downtime': 4, 'efficiency': 0.85},
    'factory_b': {'downtime': 6, 'efficiency': 0.80},  # Different standards
}
```

### **Environment-Specific Rules**
- Development: Lower thresholds for testing
- Staging: Production-like thresholds
- Production: Strict operational thresholds

### **Dynamic Adjustments**
- Seasonal variations (summer vs winter)
- Product-specific tolerances
- Learning-based improvements

## 🎯 Decision Quality Metrics

### **Accuracy Tracking**
- True positives: Correct escalations
- False positives: Unnecessary alerts
- False negatives: Missed critical issues

### **Response Time**
- Decision latency
- Escalation speed
- Resolution time

### **Effectiveness**
- Issue resolution rate
- Stakeholder satisfaction
- Cost of decisions

## 🔗 Dependencies

### **Required:**
- `monitoring/` - Input conditions for evaluation
- `actions/` - Execution of decisions

### **Optional:**
- `knowledge/` - Historical patterns and context
- `learning/` - Decision outcome feedback
- `data_access/` - Additional data for complex decisions

## 🎚️ Agent Type Usage

### **Simple Reactive Agent:** ❌ Not needed (decisions embedded in tools)
### **Monitoring Agent:** ✅ Essential for consistent alert logic
### **Autonomous Agent:** ✅ Critical for intelligent decision-making
### **Production Agent:** ✅ Required for enterprise governance

## 🔧 Best Practices

### **Decision Transparency**
- Log all decision inputs and outputs
- Provide clear reasoning for decisions
- Enable decision audit trails

### **Consistency**
- Standardize decision criteria across agents
- Avoid conflicting or contradictory rules
- Regular review and validation of decision logic

### **Adaptability**
- Design for easy threshold adjustments
- Support A/B testing of decision rules
- Enable learning-based improvements

---

**The decisions layer ensures that autonomous agents make consistent, logical, and auditable decisions based on clearly defined business rules and operational requirements.**