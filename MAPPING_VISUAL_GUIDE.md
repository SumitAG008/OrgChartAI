# SuccessFactors Mapping Visual Guide

## 🔄 Complete Mapping Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    SuccessFactors (Source)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ OrgUnit      │  │ Position    │  │ User        │           │
│  │ Entity       │  │ Entity      │  │ Entity      │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             │ OData API (GET /odata/v2/...)
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│              HRIS Service (Port 8002)                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  SuccessFactorsClient                                     │  │
│  │  - Authenticate (Basic Auth: username@companyID:password) │  │
│  │  - Fetch OrgUnit, Position, User entities                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                    │
│                             ↓                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  DataTransformer                                         │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  Field Mapping Rules:                               │  │  │
│  │  │  orgUnitId → hris_id                                │  │  │
│  │  │  orgUnitCode → code                                 │  │  │
│  │  │  orgUnitName → name                                 │  │  │
│  │  │  orgUnitType → type                                 │  │  │
│  │  │  parentOrgUnitId → parent_hris_id                   │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             │ HTTP API (Transformed Data)
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│              Org Service (Port 8000)                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Sync Endpoint                                            │  │
│  │  - Receive transformed data                               │  │
│  │  - Resolve relationships (hris_id → UUID)                  │  │
│  │  - Store in PostgreSQL                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             │ SQL INSERT/UPDATE
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│              PostgreSQL Database (Neon)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ org_unit     │  │ position     │  │ employee     │         │
│  │ - hris_id    │  │ - hris_id    │  │ - hris_id    │         │
│  │ - code       │  │ - position_  │  │ - employee_  │         │
│  │ - name       │  │   code       │  │   number     │         │
│  │ - type       │  │ - position_  │  │ - first_name │         │
│  │ - parent_id  │  │   title      │  │ - last_name  │         │
│  └──────────────┘  │ - org_unit_id│  │ - position_id│         │
│                    │ - reports_to │  │ - email      │         │
│                    └──────────────┘  └──────────────┘         │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             │ Query via API
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│              Frontend (React)                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  ChartBuilder Service                                     │  │
│  │  - Query root positions                                   │  │
│  │  - Recursively build tree                                 │  │
│  │  - Attach employee data                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                    │
│                             ↓                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Org Chart Visualization                                  │  │
│  │  - 26+ layout types                                       │  │
│  │  - Interactive features                                   │  │
│  │  - Real-time updates                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 Field Mapping Details

### **OrgUnit Mapping**

```
SuccessFactors Field          →  OrgChartAI Field          →  Database Column
─────────────────────────────────────────────────────────────────────────────
orgUnitId                    →  hris_id                   →  org_unit.hris_id
orgUnitCode                  →  code                     →  org_unit.code
orgUnitName                  →  name                     →  org_unit.name
orgUnitType                  →  type                     →  org_unit.type
parentOrgUnitId              →  parent_hris_id            →  (resolved to UUID)
status                       →  status                   →  org_unit.status
effectiveStartDate           →  effective_start_date      →  org_unit.effective_start_date
effectiveEndDate             →  effective_end_date        →  org_unit.effective_end_date
```

### **Position Mapping**

```
SuccessFactors Field          →  OrgChartAI Field          →  Database Column
─────────────────────────────────────────────────────────────────────────────
positionId                   →  hris_id                   →  position.hris_id
positionCode                 →  position_code              →  position.position_code
positionTitle                →  position_title             →  position.position_title
reportsToPositionId          →  reports_to_hris_id         →  (resolved to UUID)
orgUnitId                    →  org_unit_hris_id          →  (resolved to UUID)
jobCode                      →  job_code                   →  (resolved to UUID)
status                       →  status                    →  position.status
fte                          →  fte                       →  position.fte
grade                        →  grade                     →  position.grade
```

### **Employee Mapping**

```
SuccessFactors Field          →  OrgChartAI Field          →  Database Column
─────────────────────────────────────────────────────────────────────────────
userId                       →  employee_number            →  employee.employee_number
firstName                    →  first_name                →  employee.first_name
lastName                     →  last_name                 →  employee.last_name
displayName                  →  preferred_name            →  employee.preferred_name
email                        →  email                     →  employee.email
positionId                   →  position_hris_id          →  (resolved to UUID)
status                       →  status                    →  employee.status
startDate                    →  hire_date                 →  employee.hire_date
```

---

## 🔗 Relationship Resolution

### **How Relationships Are Resolved**

```
Step 1: Sync Org Units
┌─────────────────────────────────────────┐
│ SuccessFactors:                         │
│ {                                        │
│   "orgUnitId": "SF_OU_001",             │
│   "parentOrgUnitId": "SF_OU_ROOT"        │
│ }                                        │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 1. Check if org_unit exists by hris_id  │
│    SELECT * FROM org_unit               │
│    WHERE hris_id = 'SF_OU_001'          │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 2. If not exists, create new:            │
│    INSERT INTO org_unit                  │
│    (hris_id, code, name, ...)            │
│    VALUES ('SF_OU_001', ...)             │
│    RETURNING id                          │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 3. Resolve parent relationship:          │
│    SELECT id FROM org_unit               │
│    WHERE hris_id = 'SF_OU_ROOT'          │
│    → Returns UUID: abc-123-def          │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 4. Update parent_org_unit_id:           │
│    UPDATE org_unit                       │
│    SET parent_org_unit_id = 'abc-123'    │
│    WHERE id = current_org_unit_id        │
└─────────────────────────────────────────┘
```

---

## 🤖 AI-Powered Automapping Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI Mapping Engine                             │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Step 1: Schema Discovery                                  │  │
│  │  - Fetch $metadata from SuccessFactors                     │  │
│  │  - Analyze entity structure                                │  │
│  │  - Extract field names and types                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                    │
│                             ↓                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Step 2: AI Field Matching (NLP)                           │  │
│  │  - Encode field names using BERT/Transformer              │  │
│  │  - Calculate semantic similarity                           │  │
│  │  - Match to target schema                                  │  │
│  │  - Generate confidence scores                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                    │
│                             ↓                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Step 3: Mapping Suggestions                               │  │
│  │  {                                                          │  │
│  │    "orgUnitName": {                                        │  │
│  │      "best_match": "name",                                 │  │
│  │      "confidence": 0.95,                                   │  │
│  │      "alternatives": [...]                                 │  │
│  │    }                                                        │  │
│  │  }                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                    │
│                             ↓                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Step 4: User Review & Confirmation                        │  │
│  │  - User accepts high-confidence mappings (>0.9)            │  │
│  │  - User corrects low-confidence mappings (<0.9)            │  │
│  │  - AI learns from corrections                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                    │
│                             ↓                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Step 5: Apply Mappings                                    │  │
│  │  - Transform data using confirmed mappings                │  │
│  │  - Validate data quality                                   │  │
│  │  - Enrich missing data with AI predictions                │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🧠 Deep Learning Models for Mapping

### **1. Field Matching Model**

```
Input: "orgUnitName" (SuccessFactors field)
    ↓
BERT Encoder
    ↓
Embedding: [0.23, -0.45, 0.67, ...] (768 dimensions)
    ↓
Compare with target fields:
    - "name" → [0.25, -0.43, 0.65, ...] → Similarity: 0.95 ✅
    - "code" → [0.12, 0.34, -0.21, ...] → Similarity: 0.32
    - "type" → [0.45, 0.12, 0.89, ...] → Similarity: 0.28
    ↓
Output: Best match = "name" (confidence: 0.95)
```

### **2. Graph Neural Network for Hierarchy**

```
Org Structure Graph:
    CEO
     ├─ VP Engineering
     │   ├─ Director Backend
     │   │   ├─ Manager Team A
     │   │   └─ Manager Team B
     │   └─ Director Frontend
     └─ VP Sales
         └─ Director Enterprise
    ↓
GNN Processes:
    - Learn node embeddings
    - Detect patterns
    - Infer missing relationships
    - Validate structure
    ↓
Output:
    - Detected circular reference: None ✅
    - Missing relationships: 2 (suggested)
    - Optimal hierarchy depth: 4 levels
```

---

## 📊 Current vs AI-Powered Mapping

### **Current (Manual Rules)**

```python
# Hardcoded mapping
def transform_org_unit(org_unit):
    return {
        "name": org_unit.orgUnitName,  # Manual rule
        "code": org_unit.orgUnitCode,  # Manual rule
        "type": org_unit.orgUnitType   # Manual rule
    }
```

**Limitations:**
- ❌ Requires manual configuration for each HRIS
- ❌ Doesn't handle custom fields
- ❌ No learning from corrections
- ❌ Static rules

### **AI-Powered (Intelligent)**

```python
# AI-based mapping
def transform_with_ai(org_unit):
    mappings = ai_matcher.discover_mappings(org_unit)
    return {
        mappings["orgUnitName"]: org_unit.orgUnitName,
        mappings["orgUnitCode"]: org_unit.orgUnitCode,
        mappings["orgUnitType"]: org_unit.orgUnitType
    }
```

**Advantages:**
- ✅ Automatic field discovery
- ✅ Handles custom fields
- ✅ Learns from user feedback
- ✅ Improves over time
- ✅ Works with multiple HRIS systems

---

## 🎯 Practical Example: AI Automapping

### **Scenario: New SuccessFactors Instance**

**Step 1: AI Discovers Schema**
```python
# AI fetches and analyzes $metadata
metadata = await ai_discoverer.fetch_metadata(api_url)

# AI identifies entities
entities = {
    "OrgUnit": {
        "orgUnitId": "string",
        "orgUnitName": "string",
        "orgUnitCode": "string",
        # ... more fields
    },
    "Position": {...},
    "User": {...}
}
```

**Step 2: AI Suggests Mappings**
```python
# AI matches fields semantically
suggestions = {
    "orgUnitName": {
        "target": "name",
        "confidence": 0.95,
        "reason": "Semantic similarity: 'name' matches 'orgUnitName'"
    },
    "orgUnitCode": {
        "target": "code",
        "confidence": 0.92,
        "reason": "Direct match: 'code' field"
    }
}
```

**Step 3: User Confirms**
```python
# User reviews and confirms
confirmed_mappings = {
    "orgUnitName": "name",      # ✅ Accepted (high confidence)
    "orgUnitCode": "code",      # ✅ Accepted (high confidence)
    "customField01": "notes"    # ✅ User corrected (AI suggested "description")
}
```

**Step 4: AI Learns**
```python
# AI stores correction for future learning
ai_matcher.learn_from_correction(
    source="customField01",
    ai_suggestion="description",
    user_correction="notes",
    context="SuccessFactors custom field"
)
```

---

## 🚀 Implementation Roadmap

### **Phase 1: Basic Mapping (✅ Current)**
- Manual field mapping rules
- Basic data transformation
- Relationship resolution

### **Phase 2: AI Field Matching (🔄 Next)**
- NLP-based semantic matching
- Confidence scoring
- Mapping suggestions UI

### **Phase 3: Schema Discovery (📋 Future)**
- Automatic schema analysis
- Custom field detection
- Mapping generation

### **Phase 4: Deep Learning (📋 Advanced)**
- Transformer models
- Graph neural networks
- Continuous learning

---

**Your connection is working! Now you can sync data and see how mapping transforms SuccessFactors data into your org chart.** 🎉
