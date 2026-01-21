# Change Plan & Scenario Comparison Feature

## 🎯 Overview

The Change Plan feature allows users to create, compare, and manage different organizational scenarios. This enables planning for reorganizations, M&A activities, and future-state org structures.

## ✨ Key Features

### **1. Scenario Management**
- Create new scenarios from current org state
- Clone existing scenarios
- Manage scenario status (Draft, Active, Archived)
- Track scenario metadata (name, description, tree_id)

### **2. Scenario Explorer**
- View all scenarios in a sidebar
- Filter by status
- See scenario statistics (org units, positions, employees)
- Quick access to scenario details

### **3. Scenario Comparison**
- Compare any two scenarios side-by-side
- Visual diff showing changes
- Detailed change list:
  - **Added**: New positions/org units
  - **Removed**: Deleted positions/org units
  - **Updated**: Modified fields
  - **Moved**: Changed reporting lines or org unit assignments

### **4. Change Document Export**
- Export comparison results
- Generate change documents for each position
- Multiple formats (JSON, PDF, DOCX)

### **5. AI Assistant Integration**
- Ask questions about changes
- Get recommendations for transitions
- Understand impact of changes

## 🏗️ Architecture

### **Backend**

```
backend/org-service/
├── app/
│   ├── models.py              # Pydantic models (Scenario, ChangeItem, etc.)
│   ├── models_db.py           # SQLAlchemy models (Scenario table)
│   ├── routers/
│   │   └── change_plan.py     # API endpoints
│   └── services/
│       └── scenario_service.py # Business logic
```

### **Frontend**

```
frontend/src/components/
├── ChangePlan/
│   ├── ChangePlanView.tsx      # Main view
│   ├── ScenarioExplorer.tsx   # Sidebar explorer
│   ├── ComparisonView.tsx      # Comparison UI
│   ├── ChangeList.tsx          # Change items list
│   └── ChangeVisualDiff.tsx   # Visual diff component
```

## 📊 Database Schema

### **Scenario Table**

```sql
CREATE TABLE scenario (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    tree_id TEXT NOT NULL UNIQUE,
    base_scenario_id UUID REFERENCES scenario(id),
    status TEXT CHECK (status IN ('Draft', 'Active', 'Archived')),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    created_by UUID
);
```

### **How Scenarios Work**

1. Each scenario has a unique `tree_id`
2. Org units and positions are linked to scenarios via `tree_id`
3. Multiple scenarios can share the same base structure
4. Changes are tracked by comparing scenarios

## 🔄 API Endpoints

### **Scenarios**

```http
GET    /api/v1/change-plan/scenarios           # List all scenarios
GET    /api/v1/change-plan/scenarios/{id}      # Get scenario details
POST   /api/v1/change-plan/scenarios           # Create new scenario
GET    /api/v1/change-plan/scenarios/{id}/statistics  # Get stats
```

### **Comparison**

```http
GET    /api/v1/change-plan/compare?source_id=X&target_id=Y  # Compare scenarios
GET    /api/v1/change-plan/compare/{source}/{target}/changes  # Get filtered changes
GET    /api/v1/change-plan/compare/{source}/{target}/export  # Export document
```

## 🎨 UI Components

### **Scenario Explorer Sidebar**

- **Categories:**
  - Not in org chart (people without positions)
  - In org chart (people with positions)
  - Standard roles (role library)
  - Functions & Accountabilities

- **Features:**
  - Expandable/collapsible sections
  - Count badges
  - Checkbox selection
  - Quick filters

### **Comparison View**

- **Header:**
  - "Compare:" dropdown to select source scenario
  - "with this scenario:" shows current scenario
  - Version/date information

- **Visual Diff:**
  - Side-by-side org chart diagrams
  - Color-coded changes:
    - 🟢 Green: Added
    - 🔴 Red: Removed
    - 🟡 Yellow: Updated
    - 🔵 Blue: Moved

- **Change List:**
  - Detailed list of all changes
  - Filterable by type and entity
  - Expandable details

## 🚀 Usage Flow

### **1. Create Scenario**

```typescript
// Create a new scenario from current state
const scenario = await createScenario({
  name: "Future Org with AI Roles",
  description: "Reorganization plan for Q2 2024",
  tree_id: "future-org-2024-q2",
  base_scenario_id: currentScenarioId,
  created_by: userId
});
```

### **2. Make Changes**

- Edit positions in the scenario
- Add/remove org units
- Change reporting lines
- Update position details

### **3. Compare Scenarios**

```typescript
// Compare two scenarios
const comparison = await compareScenarios(
  sourceScenarioId,
  targetScenarioId
);

// Get changes
console.log(comparison.summary);
// { added: 5, removed: 3, updated: 10, moved: 2 }

// View detailed changes
comparison.changes.forEach(change => {
  console.log(`${change.change_type}: ${change.entity_name}`);
});
```

### **4. Export Change Document**

```typescript
// Export comparison
const document = await exportChangeDocument(
  sourceScenarioId,
  targetScenarioId,
  "pdf"
);
```

## 🎯 Use Cases

### **1. Reorganization Planning**
- Create "Future State" scenario
- Compare with current state
- Identify all changes needed
- Export change documents for HR

### **2. M&A Integration**
- Create "Post-Merger" scenario
- Map org units from both companies
- Compare structures
- Plan integration

### **3. Budget Planning**
- Create "Budget 2024" scenario
- Compare with current
- Calculate headcount changes
- Estimate costs

### **4. What-If Analysis**
- Create multiple scenarios
- Compare different options
- Choose best option
- Implement selected scenario

## 🤖 AI Integration

### **AI Assistant for Change Plan**

Users can ask:
- "What positions were added in this scenario?"
- "Show me all reporting line changes"
- "What's the impact of removing this department?"
- "Generate a transition plan for these changes"

### **AI Recommendations**

- Suggest optimal org structure
- Recommend positions to add/remove
- Identify potential issues
- Propose transition timelines

## 📝 Next Steps

1. ✅ Backend API implemented
2. 🔄 Frontend components (in progress)
3. 📋 Visual diff rendering
4. 📋 Export functionality
5. 📋 AI assistant integration

---

**This feature enables powerful org planning and change management capabilities!** 🚀
