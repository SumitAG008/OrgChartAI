# Org Structure Visualization Guide
## Building 26 Types of Organizational Structure Visualizations

---

## 🎨 1. Visual Grammar

Every org-structure diagram, no matter the style, is built from the same primitives:

### **Core Primitives:**

- **Nodes** → people, roles, teams, departments
- **Edges** → reporting lines, collaboration lines
- **Containers** → divisions, business units
- **Layouts** → hierarchical, radial, matrix, layered
- **Color System** → use your brand palette (you already have modular palettes for InsightSheet)

You can define these once and reuse them across all 26 variations.

---

## 🏗️ 2. The 26 Org Structure Types

Below is a categorized list of the most common and visually distinct org-structure representations. You can recreate each one using your design system.

### **A. Hierarchical Structures**

1. **Classic Top-Down Hierarchy**
   - Traditional pyramid structure
   - CEO at top, cascading down
   - Most common org chart type

2. **Bottom-Up Hierarchy**
   - Inverted pyramid
   - Front-line employees at top
   - Leadership at bottom

3. **Vertical Functional Structure**
   - Organized by function (HR, Finance, Engineering)
   - Vertical columns for each function
   - Clear functional boundaries

4. **Horizontal Functional Structure**
   - Functions arranged horizontally
   - Cross-functional collaboration emphasis
   - Flat reporting structure

5. **Multi-Layered Hierarchy**
   - Multiple hierarchy levels visible
   - Expandable/collapsible layers
   - Deep organizational depth

6. **Span-of-Control Chart**
   - Focus on manager-to-direct-report ratios
   - Visual emphasis on reporting relationships
   - Highlights management efficiency

### **B. Divisional Structures**

7. **Product-Based Divisional Structure**
   - Organized by product lines
   - Each product has its own division
   - Independent product teams

8. **Geography-Based Divisional Structure**
   - Organized by geographic regions
   - Regional autonomy
   - Location-based hierarchy

9. **Market/Customer Segment Structure**
   - Organized by customer segments
   - Market-focused divisions
   - Customer-centric organization

10. **Multi-Divisional (M-Form) Structure**
    - Multiple divisions with central HQ
    - Each division operates semi-independently
    - Corporate oversight layer

### **C. Matrix Structures**

11. **2×2 Matrix (Dual Reporting)**
    - Dual reporting lines
    - Functional and project managers
    - Cross-functional collaboration

12. **3-Axis Matrix (Role × Region × Product)**
    - Three-dimensional matrix
    - Complex reporting relationships
    - Multi-dimensional organization

13. **Cross-Functional Matrix**
    - Functional departments × project teams
    - Shared resources
    - Collaborative structure

### **D. Network & Modern Structures**

14. **Network Organization**
    - Interconnected nodes
    - No strict hierarchy
    - Relationship-based structure

15. **Holacracy / Circle Structure**
    - Circular organizational units
    - Self-organizing teams
    - Distributed authority

16. **Pod-Based Structure**
    - Small autonomous teams (pods)
    - Pod-to-pod relationships
    - Agile team structure

17. **Agile Squad/Tribe Structure**
    - Squads (small teams)
    - Tribes (collections of squads)
    - Guilds (cross-cutting communities)
    - Modern tech organization pattern

18. **Ecosystem Structure**
    - Partner and vendor relationships
    - External connections
    - Extended organization view

### **E. Radial & Circular Structures**

19. **Radial Hub-and-Spoke**
    - Central hub with radiating spokes
    - Central leadership
    - Spoke teams/departments

20. **Concentric Circle Structure**
    - Multiple concentric circles
    - Inner circle = leadership
    - Outer circles = broader organization

21. **Circular Team Relationship Map**
    - Circular arrangement
    - Relationship-focused
    - Team collaboration emphasis

### **F. Flow-Based Structures**

22. **Process-Flow Org Structure**
    - Organized by business processes
    - Process-driven hierarchy
    - Workflow visualization

23. **Value-Stream Org Structure**
    - Organized by value streams
    - Value delivery focus
    - Customer value emphasis

24. **Decision-Flow Org Structure**
    - Organized by decision-making authority
    - Decision rights visualization
    - Authority flow

### **G. Hybrid & Custom Structures**

25. **Hybrid Hierarchy + Matrix**
    - Combines hierarchical and matrix elements
    - Flexible structure
    - Dual reporting where needed

26. **Hybrid Divisional + Network**
    - Divisional structure with network elements
    - Cross-divisional collaboration
    - Modern hybrid approach

---

## 🔧 3. How to Build These Visualizations (Step-by-Step)

### **Step 1 — Choose a Layout Engine**

Depending on your platform:

- **Web** → D3.js, React Flow, Cytoscape.js
- **Desktop** → Mermaid.js, Graphviz, Draw.io XML
- **Your product (InsightSheet)** → You can build a modular layout engine using:
  - Node components
  - Edge routing
  - Auto-layout algorithms

### **Step 2 — Define Node Types**

**Example:**
- Executive node
- Manager node
- Team node
- Contractor node
- External partner node

**Use your brand color system:**
- InsightSheet Lite → Blue
- InsightSheet File → Green
- InsightSheet Elite → Purple
- Meldra → Teal

### **Step 3 — Define Edge Types**

- **Solid line** → direct reporting
- **Dashed line** → dotted-line reporting
- **Curved line** → collaboration
- **Thick line** → authority

### **Step 4 — Apply Layout Algorithms**

- **Tree layout** → hierarchical
- **Radial layout** → circular
- **Force-directed** → network
- **Grid layout** → matrix

### **Step 5 — Add Interaction (Optional)**

- Expand/collapse nodes
- Hover tooltips
- Click to open profile
- Drag to rearrange

---

## 🎨 Visual Design System

You can leverage your modular color systems and branding principles:

### **Node Types:**

- 🔵 **Permanent** → Blue gradient
- 🟢 **Fixed-Term** → Green gradient
- 🟠 **Contractual** → Orange gradient
- 🔴 **Temporary** → Red gradient

### **Node Shapes:**

- **Rounded rectangles** for individuals
- **Circles** for contractors
- **Hexagons** for cross-functional roles

### **Edge Types:**

- **Solid line** → Direct reporting
- **Dashed line** → Temporary assignment
- **Curved line** → Collaboration

---

## 📊 4. Core Object Model for Org Visualization

These are your foundational entities (inspired by how serious HR/OM systems like SAP model orgs: org units, positions, jobs, persons, relationships).

### **1. OrganizationUnit**

**Key fields:**
- `id` - Unique identifier
- `code` - e.g. "FIN-UK-001"
- `name` - Display name
- `type` - Division, Department, Team, Region, LegalEntity, CostCenterOwner
- `parent_org_unit_id` - For hierarchy (nullable)
- `cost_center_id` - Associated cost center
- `location_id` - Physical location
- `effective_start_date` - When this unit becomes active
- `effective_end_date` - When this unit becomes inactive (nullable)
- `status` - Active, Inactive, Planned

### **2. Position**

**Key idea:** Position is the "seat"; employee is who sits in it. One position can be vacant, filled, or temporarily filled.

**Key fields:**
- `id` - Unique identifier
- `org_unit_id` - Which org unit this position belongs to
- `job_id` - Generic job profile
- `position_code` - Unique position code
- `position_title` - Display title
- `position_type` - Permanent, FixedTerm, Contract, Temporary, Intern
- `fte` - Full-time equivalent (0–1)
- `grade` / `level` - Job grade/level
- `reports_to_position_id` - Direct reporting position (nullable)
- `is_managerial` - Boolean flag
- `is_mass_position_template` - Boolean flag for mass positions
- `effective_start_date` - When position becomes active
- `effective_end_date` - When position becomes inactive (nullable)
- `status` - Active, Planned, Frozen, Closed

### **3. Job**

**Key fields:**
- `id` - Unique identifier
- `job_code` - Standard job code
- `job_title` - Standard job title
- `job_family` - Job family category
- `job_sub_family` - Sub-family category
- `default_grade` - Default grade for this job
- `default_position_type` - Default position type
- `description` - Job description

### **4. Employee (Person)**

**Key fields:**
- `id` - Unique identifier
- `employee_number` - HRIS employee number
- `first_name` - First name
- `last_name` - Last name
- `preferred_name` - Preferred display name
- `email` - Email address
- `employment_type` - Permanent, FixedTerm, Contractor, Temporary
- `legal_entity_id` - Legal entity association
- `primary_position_id` - Primary position assignment
- `hire_date` - Employment start date
- `termination_date` - Employment end date (nullable)
- `status` - Active, OnLeave, Terminated

### **5. Assignment**

For temporary moves, dual reporting, projects, etc.

**Key fields:**
- `id` - Unique identifier
- `employee_id` - Employee reference
- `position_id` - Position reference
- `assignment_type` - Primary, Secondary, Temporary, Project
- `reports_to_position_id` - For dotted-line reporting (nullable)
- `start_date` - Assignment start date
- `end_date` - Assignment end date (nullable)
- `status` - Active, Completed, Planned

### **6. Location / CostCenter / LegalEntity**

Keep them as separate master tables:

**Location:**
- `id`, `code`, `name`, `country`, `city`, `timezone`

**CostCenter:**
- `id`, `code`, `name`, `region`

**LegalEntity:**
- `id`, `code`, `name`, `country`

---

## 🏭 5. Mass Position Creation

You can model this as:

### **MassPositionTemplate**

**Fields:**
- `id` - Unique identifier
- `org_unit_id` - Target org unit
- `job_id` - Job profile to use
- `position_title` - Position title template
- `position_type` - Position type
- `grade` - Job grade
- `fte` - Full-time equivalent
- `count` - e.g. 40 (number of positions to create)
- `default_reports_to_position_id` - Default manager
- `location_id` - Location assignment
- `cost_center_id` - Cost center assignment

### **Logic:**

1. User fills one form → creates `MassPositionTemplate`.
2. System generates `count` rows in `Position`:
   - `position_code` auto-generated (e.g. "FIN-ANL-001" … "FIN-ANL-040").
   - All positions are linked to same `org_unit_id`, `job_id`, etc.
3. Vacancies are simply `Position` rows with no active `Assignment` or `primary_position_id` mapping.

---

## 🔧 6. Flexible Data Model for Org Objects

To keep it extensible without schema changes every time:

### **OrgAttributeDefinition**

**Fields:**
- `id` - Unique identifier
- `object_type` - OrganizationUnit, Position, Employee
- `code` - e.g. "BAND", "SUCCESSION_RISK"
- `label` - Display label
- `data_type` - String, Number, Boolean, Date, Enum
- `allowed_values` - JSON for enums (nullable)

### **OrgAttributeValue**

**Fields:**
- `id` - Unique identifier
- `object_type` - OrganizationUnit, Position, Employee
- `object_id` - Reference to the object
- `attribute_definition_id` - Reference to attribute definition
- `value` - Stringified, interpreted by `data_type`

This gives you a flexible, metadata-driven model similar to modern HR platforms where corporate data models define org and job structures.

---

## 📈 7. Data Needed for Org Intelligence, Headcount, Vacancies

To power analytics like headcount, vacancy rate, span of control, etc., you'll want:

### **For Headcount:**

**From Employee / Assignment:**
- `employment_type`
- `fte`
- `primary_position_id`
- `legal_entity_id`
- `location_id`
- `status`

**From Position:**
- `org_unit_id`
- `position_type`
- `is_managerial`
- `status`

### **For Vacancies:**

A position is vacant if:
- `status` = Active
- AND no active `Assignment` with `assignment_type` = Primary
- AND no `Employee.primary_position_id` pointing to it.

### **For Org Intelligence:**

**Relationships:**
- `reports_to_position_id` (tree)
- `org_unit.parent_org_unit_id` (org hierarchy)

**Metrics:**
- Headcount by `org_unit`, `location`, `employment_type`
- Vacancy count and rate by `org_unit`
- Span of control (direct reports per manager)
- Temporary vs permanent ratio

**Time dimension:**
- All core objects should be effective-dated so you can reconstruct org at any point in time.

---

## 🎯 8. How This Maps to Your Visualization Product

### **Nodes:**
- Can represent `Position` or `Employee` depending on mode.
- Node color/shape driven by `employment_type` and `position_type`.

### **Edges:**
- `reports_to_position_id` → reporting lines.
- `Assignment` with `assignment_type` = Temporary → temporary movement lines.

### **Mass positions:**
- Show as multiple vacant seats under same manager/org unit.

### **Workflows:**
- On temporary assignment start → create `Assignment` row, move node visually.
- On completion → close `Assignment`, revert node to original position.

---

## 🔄 9. Visualization Workflow Integration

### **Temporary Assignments:**
- When a temporary assignment is created:
  1. Create `Assignment` record with `assignment_type = Temporary`
  2. Visually move the node to the new position
  3. Show temporary assignment indicator (dashed border, different color)
  4. Store original position reference for restoration

- When assignment completes:
  1. Close `Assignment` record (`status = Completed`)
  2. Visually revert node to original position
  3. Remove temporary assignment indicators

### **Interactive Chart Features:**
- Users/admins can drag nodes to new positions (with RBAC validation)
- System creates/updates `Assignment` records accordingly
- Visual feedback for temporary vs permanent assignments
- Undo/redo support for position changes

---

## 📋 10. Next Steps

If you want, next step we can:
- Design the API schema (FastAPI models) for these entities, or
- Sketch how the graph query would look (e.g. "give me org tree for org_unit X as of date Y").

---

## 🎨 Design System Integration

### **Brand Color Mapping:**

- **InsightSheet Lite** → Blue palette
- **InsightSheet File** → Green palette
- **InsightSheet Elite** → Purple palette
- **Meldra** → Teal palette

### **Visual Consistency:**

All 26 visualization types should:
- Use consistent node shapes and colors
- Follow the same edge styling rules
- Support the same interaction patterns
- Maintain brand identity across all views

---

## 📚 Summary

This guide provides:
1. ✅ **Visual grammar** for building org structures
2. ✅ **26 distinct visualization types** categorized by structure pattern
3. ✅ **Step-by-step building instructions** for each type
4. ✅ **Core object model** inspired by enterprise HR systems
5. ✅ **Mass position creation** workflow
6. ✅ **Flexible attribute system** for extensibility
7. ✅ **Data requirements** for org intelligence
8. ✅ **Visualization mapping** from data model to visual representation

**All 26 types can be built using the same foundational primitives and design system!**
