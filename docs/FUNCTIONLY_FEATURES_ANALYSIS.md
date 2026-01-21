# Functionly AI-Assisted Org Design - Complete Feature Documentation

**Document Version:** 1.0
**Date:** 2026-01-21
**Purpose:** Comprehensive analysis of Functionly's UI, features, and AI capabilities for OrgChartAI implementation

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Complete UI Structure](#complete-ui-structure)
3. [Navigation & Top Bar](#navigation--top-bar)
4. [Left Sidebar - Views Panel](#left-sidebar---views-panel)
5. [Main Canvas - Org Chart](#main-canvas---org-chart)
6. [Right Panel - Properties & Details](#right-panel---properties--details)
7. [AI Features](#ai-features)
8. [Scenario Summary Dashboard](#scenario-summary-dashboard)
9. [Role Management](#role-management)
10. [Data Model & Calculations](#data-model--calculations)
11. [Feature Gap Analysis](#feature-gap-analysis)

---

## Executive Summary

Functionly provides an AI-assisted organizational design platform with the following key capabilities:

### Core Value Propositions
- **AI Agent Integration**: Ability to add AI agents as positions in org chart (AI Agent "Eve", "Tars", "Sonny")
- **OrgPilot AI**: AI-powered conversational assistant for workforce design
- **Multiple View Modes**: Org chart, People & positions, Functional chart, Forecast sheet, Change plan
- **Scenario Planning**: Compare organizational scenarios with impact analysis
- **Real-time Analytics**: Dashboard showing key statistics, vacancies, allocations, forecasts
- **Interactive Visualization**: Drag-drop org chart with customizable layouts
- **Role-based Design**: Define roles, accountabilities, and responsibilities
- **Workforce Forecasting**: Monthly projections for headcount, FTE, compensation

---

## Complete UI Structure

### Layout Architecture
```
┌─────────────────────────────────────────────────────────────────────────┐
│ TOP NAVIGATION BAR                                                      │
│ [Title] [Add tag] [Template] [Edit] [Download] [Theme] [Share]         │
│ [Copy] [OrgPilot AI] [User Profile]                                    │
├──────────┬────────────────────────────────────────────┬────────────────┤
│          │  MAIN TOOLBAR                              │                │
│  LEFT    │  [Views] [Properties] [Filter] [Layers]   │  RIGHT PANEL   │
│ SIDEBAR  │  [Layout] [Roles] [More]                   │                │
│          ├────────────────────────────────────────────┤  - Properties  │
│ - Views  │                                            │  - Scenario    │
│ - Search │  MAIN CANVAS                               │    Summary     │
│ - Export │                                            │  - Role Details│
│          │  Interactive Org Chart Display             │  - Analytics   │
│          │                                            │                │
│          │  [Nodes with people, roles, AI agents]     │                │
│          │                                            │                │
├──────────┼────────────────────────────────────────────┼────────────────┤
│ Scenario │  [Zoom Controls] [+ -] [Fit]               │ [Ask me...]    │
│ Explorer │                                            │ [AI Chat]      │
└──────────┴────────────────────────────────────────────┴────────────────┘
```

---

## Navigation & Top Bar

### Top Navigation Elements

#### 1. Document Title
- **Element**: `"Future Org with AI Roles"` with dropdown
- **Function**: Select/switch between different org scenarios
- **UI Component**: Dropdown menu button

#### 2. Action Buttons (Left Group)
- **Add tag** button
  - Icon: Tag icon
  - Function: Add tags to organize scenarios

- **Template** button
  - Icon: Template/grid icon
  - Function: Apply org chart templates

#### 3. Utility Buttons (Right Group)
- **Edit** button
  - Icon: Pencil/edit icon
  - Function: Enter edit mode

- **Download** button
  - Icon: Download icon
  - Function: Export org chart (PDF, PNG, CSV, etc.)

- **Theme Toggle** button
  - Icon: Light bulb icon
  - Function: **Opens Scenario Summary Dashboard**
  - **CRITICAL FEATURE**: This reveals analytics and insights

- **Share** button
  - Icon: Share/link icon
  - Function: Share org chart with team members

#### 4. Primary Action Buttons
- **Copy** button
  - Style: Blue/purple button
  - Function: Duplicate current scenario

- **OrgPilot AI** button
  - Style: Blue/purple with sparkle icon
  - Function: **Launch AI assistant for workforce design**
  - **CRITICAL AI FEATURE**

#### 5. User Profile
- **Element**: Avatar with dropdown
- Function: User settings, account management

---

## Left Sidebar - Views Panel

### Sidebar Structure

#### Top Section
1. **View Selector Dropdown**
   - Current: "Org chart"
   - Icon: Bar chart icon
   - Function: Quick switch between views

2. **Search Button**
   - Icon: Magnifying glass
   - Function: Search people, roles, positions

3. **Related Link**
   - Icon: Connection icon
   - Function: Show related scenarios/connections

4. **Export Link**
   - Icon: Download icon
   - Function: Export current view data

#### Views Section

**Label**: "Views" with info icon

##### View 1: Org chart
- **Icon**: 📊 Bar chart icon (blue/yellow)
- **Badge**: "Default"
- **Description**: "Edit positions by adding people..."
- **Function**: Primary hierarchical org chart view
- **UI Elements in View**:
  - Drag-drop node positioning
  - Hierarchical tree layout
  - Person cards with photos
  - Role titles and percentages
  - AI agent indicators (purple border)

##### View 2: People & positions
- **Icon**: 👥 People/layers icon (orange/teal)
- **Description**: "View and edit people and..."
- **Function**: List/table view of all people and their positions
- **Expected Features**:
  - Sortable table
  - Filter by department, role, status
  - Bulk edit capabilities
  - Vacancy management

##### View 3: Functional chart
- **Icon**: 📋 Grid/checklist icon (red/black)
- **Description**: "Edit roles and accountabilities i..."
- **Function**: Function-based organization view
- **Expected Features**:
  - Role definitions
  - Accountabilities matrix
  - Responsibility assignments
  - RACI chart integration

##### View 4: Forecast sheet
- **Icon**: 📊 Bar chart icon (yellow/orange)
- **Description**: "View and edit the forecast sheet"
- **Function**: Workforce planning and forecasting
- **Expected Features**:
  - Monthly/quarterly projections
  - Headcount planning
  - FTE calculations
  - Budget forecasting
  - Compensation projections

##### View 5: Change plan
- **Icon**: 🔄 Comparison/layers icon (red/yellow gradient)
- **Description**: "Compare this scenario with..."
- **Function**: Scenario comparison and change planning
- **Expected Features**:
  - Before/after comparison
  - Change impact analysis
  - Side-by-side scenario view
  - Diff highlighting

#### Bottom Section
- **"+ Add a view"** button
  - Function: Create custom views
  - Expected: Custom filters, saved searches, specific team views

### Scenario Explorer (Bottom Panel)
- **Element**: Purple/blue collapsible panel
- **Label**: "Scenario explorer" with expand icon
- **Function**: Manage and compare multiple organizational scenarios
- **State**: Expandable/collapsible

---

## Main Canvas - Org Chart

### Toolbar Elements

#### Left Side
1. **View Type Dropdown**
   - Icon: Bar chart icon
   - Current: Shows active view type
   - Function: Quick view switcher

2. **Properties Tab**
   - Label: "Properties"
   - Function: Show properties panel
   - State: Active/Inactive

3. **Filter: Top item**
   - Function: Filter org chart by top-level person/role
   - UI: Search box appears with autocomplete
   - Example: "Georgeanne Gorke, Chief Executive Officer"
   - **Clear** button to reset filter
   - **CRITICAL FEATURE**: Allows focusing on specific hierarchies

4. **Layers Control**
   - Label: "Layers: 2 below"
   - Options: Control depth of hierarchy shown
   - Values: "X above", "X below", "All"

5. **Layout Selector**
   - Label: "Layout: Narrow"
   - Options: Narrow, Wide, Compact, Custom
   - Function: Adjust node spacing and arrangement

6. **Roles Dropdown**
   - Label: "Roles" with dropdown
   - Options:
     - Accountabilities
     - **Roles** (checked - active view)
     - Positions
     - Groups
   - Function: Switch between different org design paradigms
   - **CRITICAL FEATURE**: Multiple design methodologies

#### Right Side
7. **More Options Menu**
   - Icon: Three dots
   - Function: Additional chart options

### Org Chart Visualization

#### Node Structure

Each org chart node displays:

##### Standard Employee Node
```
┌──────────────────────────┐
│ 👤 Photo                 │
│                          │
│ Name (Bold)              │
│ Title/Role               │
│                          │
│ 🎯 Role Name       100%  │
└──────────────────────────┘
```

**Example**:
- **Cly Mengue**
- **CTO**
- 🎯 Chief Technology Officer | 100%

##### AI Agent Node (Special Styling)
```
┌══════════════════════════┐  ← Purple/Blue Border
║ 🤖 AI Avatar             ║
║                          ║
║ AI Agent "Name"          ║
║ AI Role Description      ║
║                          ║
║ 🎯 AI Role Name    100%  ║
└══════════════════════════┘
```

**Example AI Agents Shown**:

1. **AI Agent "Eve"**
   - Role: AI Cross-Functional Integrator
   - Description: "AI Cross-Functional..."
   - Percentage: 100%
   - Border: Purple/blue to distinguish from humans

2. **AI Agent "Tars"**
   - Role: AI Chief Strategy Advisor
   - Description: "AI Chief Strategy Adv"
   - Percentage: 100%

3. **AI Agent "Sonny"**
   - Role: AI Market Analyst
   - Description: "AI Market Analyst"
   - Percentage: 100%

#### Node Visual Properties
- **Border**: Thin border (purple for AI, standard for humans)
- **Background**: White/light background
- **Shadow**: Subtle drop shadow
- **Spacing**: Consistent padding
- **Avatar**: Circular photo or AI icon
- **Percentage**: Role allocation (100%, 50%, etc.)
- **Icon**: Role icon (🎯) before role name

#### Hierarchy Connections
- **Lines**: Solid lines connecting nodes
- **Style**: Orthogonal or curved connectors
- **Direction**: Top-down tree layout
- **Multiple Reports**: Lines fan out from manager node

#### Example Hierarchy Shown
```
CEO (Georgeanne Gorki)
├─ AI Agent "Eve" (AI Cross-Functional Integrator)
├─ Cly Mengue (CTO)
│  └─ Cohen Kavanagh (VP Engineering)
├─ Brita Lippitt (COO)
│  └─ Teodor Enriquez (Operations Director)
├─ Brett Hans (CMO)
│  ├─ Margery Thomas (Marketing Manager)
│  └─ AI Agent "Sonny" (AI Market Analyst)
└─ AI Agent "Tars" (AI Chief Strategy Advisor)
```

### Canvas Controls

#### Bottom Right
- **Grid Icon**: Toggle grid view
- **"Ask me anything..."** input field
  - Function: AI chat interface (OrgPilot AI)
  - Icon: Plus/star icon before text
  - Send button on right
  - **CRITICAL AI FEATURE**

#### Zoom Controls
- **Zoom** label
- **-** (Zoom out button)
- **+** (Zoom in button)
- **⛶** (Fit to screen button)
- **↗** (Fullscreen button)

---

## Right Panel - Properties & Details

The right panel shows context-sensitive information based on what's selected:

### Mode 1: Properties Panel (Chart Level)

#### Header
- **Icon**: Chart icon
- **Tabs**: Displayed properties, Group calculations

#### Section 1: Displayed Properties

##### Person Properties
**Category**: Person

- **Person photo**
  - Toggle: ON (green)
  - Function: Show/hide profile photos

- **Person name**
  - Toggle: ON (green)
  - Function: Show/hide names

##### Positions Properties
**Category**: Positions

- **Title**
  - Toggle: ON (green)
  - Function: Show position titles

- **Description**
  - Toggle: OFF (gray)
  - Function: Show position descriptions

- **AI status**
  - Toggle: OFF (gray)
  - Function: **Show AI vs human indicator**
  - **CRITICAL AI FEATURE**

- **Position Id**
  - Toggle: OFF (gray)
  - Function: Show position IDs

- **Full time equivalent (Effort)**
  - Toggle: OFF (gray)
  - Function: Show FTE percentage

- **Vacancy status**
  - Toggle: OFF (gray)
  - Function: Show vacant positions

- **Total compensation**
  - Toggle: OFF (gray)
  - Icon: Eye with strikethrough (hidden/private)
  - Function: Show salary information

- **+ Add a property**
  - Function: Add custom properties

##### Groups Properties
**Category**: Groups

- **Description**
  - Toggle: OFF (gray)
  - Function: Show group descriptions

##### Other Properties
**Category**: Other

- **Comments**
  - Toggle: ON (green)
  - Function: Show comments

- **Role effort %**
  - Toggle: ON (green)
  - Function: Show role allocation percentage

#### Section 2: Group Calculations

##### Vacancy Calculations
- **Vacancy FTE (sum)**
  - Toggle: OFF
  - Function: Total vacant FTE

- **Vacancy compensation (sum)**
  - Toggle: OFF
  - Icon: Eye crossed out (private)
  - Function: Total compensation for vacant positions

- **Include vacancies in all calculations**
  - Toggle: OFF
  - Function: Include/exclude vacancies from totals

##### Span of Control
**Category**: Span of control

- **Span of control (avg)**
  - Toggle: OFF
  - Function: Average direct reports

- **Span of control (max)**
  - Toggle: OFF
  - Function: Maximum direct reports

- **Span of control (min)**
  - Toggle: OFF
  - Function: Minimum direct reports

##### Role Calculations
**Category**: Roles

- **Role count (sum)**
  - Toggle: OFF
  - Function: Total number of roles

- **Role FTE (sum)**
  - Toggle: OFF
  - Function: Total FTE across all roles

- **Role compensation (sum)**
  - Toggle: OFF
  - Icon: Eye crossed out
  - Function: Total role compensation

##### AI Calculations
**Category**: AI

- **AI agent roles (count)**
  - Toggle: OFF
  - Function: **Count of AI agents in org**
  - **CRITICAL AI FEATURE**

- **AI agent roles (FTE)**
  - Toggle: OFF
  - Function: **Total FTE allocated to AI agents**
  - **CRITICAL AI FEATURE**

##### Layer Calculations
**Category**: Layers

- **Layers above (count)**
  - Toggle: OFF
  - Function: Hierarchy levels above selected node

- **Layers below (count)**
  - Toggle: OFF
  - Function: Hierarchy levels below selected node

##### Custom Calculations
**Category**: Custom

- **+ Add a custom calculation**
  - Function: Create custom metrics and calculations

---

### Mode 2: Scenario Summary Dashboard

**Trigger**: Click light bulb icon in top bar

#### Header
- **Title**: "Scenario summary"
- **Close button**: X in top right

#### Section 1: Key Statistics
- **Label**: "Key statistics" (collapsible)
- **Summary**: "10 | 103 ⭐"
  - Interpretation: 10 positions | 103 people | star (favorite/important)

##### Visual Charts (Side by Side)

**Org Chart Metric**
- **Type**: Circular/donut chart
- **Color**: Green
- **Value**: "10 Total"
- **Label**: "Org chart"

**People Metric**
- **Type**: Circular/donut chart
- **Color**: Purple/blue
- **Value**: "103 Total"
- **Label**: "People"

##### Status Indicators (Below Charts)

**Left Column (Org Chart)**
- "0 vacant po..." (vacant positions)
- "10 filled pos..." (filled positions)

**Right Column (People)**
- "93 not alloc..." (not allocated) 🔥 (fire icon - alert)
- "10 allocated"

#### Section 2: People Details
- **Header**: "People" with count "103 | 93 🔥"
  - 103 total people
  - 93 with alert/issue (fire icon)

- **Text**: "103 people in org"

**Role Distribution Chart**
- **Type**: Circular chart with legend
- **Segments**:
  - "Single role" (blue section)
  - "Multiple roles" (other section)
- **Number displayed**: "19" (partial view)
- **Number with alert**: "93 🔥"

#### Section 3: Accountabilities
- **Header**: "Accountabilities"
- **Count**: "0 | 154 🔥"
  - 0 assigned
  - 154 total/unassigned (alert)

#### Section 4: Forecast Overview
- **Header**: "Forecast overview" (expandable)
- **More options**: Three dots menu

##### Forecast Metrics

**Position count**
- Label: "Position count"
- Data selector: "Data: Position count >"

**Headcount**
- Label: "Headcount"
- Group selector: "Group: Vacancy status >"

**Effort (FTE)**
- Label: "Effort (FTE)"
- Scale selector: "Scale: Monthly >"

**Compensation**
- Label: "Compensation"
- Icon: Dollar sign

**Hours worked**
- Label: "Hours worked"
- Icon: Clock

##### Forecast Chart
- **Type**: Bar chart
- **Color**: Blue bars
- **X-axis**: Months (Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep)
- **Y-axis**: Scale from 0 upward
- **Data**: Monthly values shown as vertical bars

---

### Mode 3: Role Details Panel

**Trigger**: Click on a role/position node

#### Header
- **Back arrow**: Return to previous view
- **Icon**: Role icon (shield)
- **Label**: "Role"
- **Badge**: "Non-standard" (yellow)
  - Indicates role doesn't match standard role library
- **More options**: Three dots
- **Close**: X button

#### Role Title
- **Example**: "Chief Technology Officer"
- **Style**: Large, bold text

#### Assigned Person
- **Avatar**: Profile photo
- **Name**: "Cly Mengue"
- **Title**: "Chief Technology Officer"
- **Dropdown**: Select different person

#### Description Section
- **Label**: "Description"
- **Element**: Text area (editable)
- **Icon**: Edit pencil (top right)

#### Manager Section
- **Label**: "Manager"
- **Icon**: Person icon
- **Current**: "No position"
- **Placeholder**: "Click to assign to a position"
- **Function**: Assign reporting relationship

#### AI Usage Section
**Label**: "AI used"

- **Icon**: Robot/AI icon (crossed out if not used)
- **Dropdown**: "No AI in use"
- **Options** (expected):
  - No AI in use
  - AI assistant
  - AI augmented
  - Fully AI agent
  - **CRITICAL AI FEATURE**

#### Based on Standard Role
**Label**: "Based on standard role"

- **Icon**: Document/template icon
- **Role template**: "Chief Technology Officer"
- **Category**: "Management"

#### Responsibilities Section
- **Label**: "Responsibilities"
- **Count badge**: "5"
- **Icons**:
  - Edit icon (pencil)
  - Add icon (plus)

#### AI Agent Role Example

**Role**: "AI Cross-Functional Integrator"

**Badge**: "Non-standard"

**Manager**: "No position - Click to assign to a position"

**AI used**: "No AI in use" (dropdown)

**Based on standard role**:
- "AI Cross-Functional Integrator"
- Category: "Operations"

**Responsibilities**: 4

**Example Responsibility Text** (partial):
"Knowledge Bridging: Continuously monitor and analyze information flows across all departments (finance, marketing, sales, operations, customer..."

---

## AI Features

### 1. AI Agent Integration

#### AI Agent Nodes
- **Visual Distinction**: Purple/blue border around node
- **Naming Convention**: AI Agent "Name"
  - "Eve", "Tars", "Sonny" (personality/character names)
- **Roles Assigned**:
  - AI Cross-Functional Integrator
  - AI Chief Strategy Advisor
  - AI Market Analyst
- **Full Integration**: Treated as first-class org members
- **FTE Allocation**: Shows 100% (or other percentages)

#### AI Role Types

Based on the examples, AI agents can have specialized roles:

##### 1. AI Cross-Functional Integrator
- **Category**: Operations
- **Responsibilities**: 4
- **Function**: "Knowledge Bridging: Continuously monitor and analyze information flows across all departments..."
- **Purpose**: Connect silos, facilitate information sharing

##### 2. AI Chief Strategy Advisor
- **Category**: Strategy/Advisory
- **Function**: Strategic recommendations
- **Purpose**: High-level strategic guidance

##### 3. AI Market Analyst
- **Category**: Marketing/Analytics
- **Function**: Market analysis and insights
- **Purpose**: Data-driven market intelligence

### 2. OrgPilot AI (Conversational Assistant)

#### Access Points
- **Primary**: "OrgPilot AI" button in top navigation (blue/purple button with sparkle)
- **Secondary**: "Ask me anything..." chat input at bottom right of canvas

#### Expected Capabilities
Based on Functionly's positioning:

**Agent Mode**:
- Autonomous analysis of org structure
- Proactive recommendations
- Scenario generation
- "What if" analysis

**Advisor Mode**:
- Answer questions about the org
- Provide best practice guidance
- Explain metrics and calculations
- Help with decision-making

#### AI Prompt Examples (Expected)
- "What is the span of control for the engineering department?"
- "Show me all vacant positions"
- "Recommend an org structure for a new product team"
- "Compare this scenario with last quarter"
- "What's the total compensation budget?"
- "Identify skill gaps in the marketing team"

### 3. AI Status Tracking

#### Property: AI Status
- **Location**: Properties panel > Positions section
- **Type**: Toggle (can be shown/hidden on nodes)
- **Purpose**: Indicate if position is human, AI, or hybrid

#### Calculations: AI Agent Metrics
- **AI agent roles (count)**: Total number of AI agents
- **AI agent roles (FTE)**: FTE allocated to AI agents
- **Purpose**: Track AI adoption and capacity

### 4. AI-Powered Features (Inferred)

Based on Functionly's documentation:

#### Scenario Generation
- AI generates optimal org structures
- Considers: skills, capacity, costs, communication patterns

#### Field Matching
- Semantic matching of HRIS fields
- Auto-mapping during integration

#### Recommendation Engine
- Team formation suggestions
- Span of control optimization
- Role assignment recommendations

---

## Scenario Summary Dashboard

### Purpose
Provide at-a-glance insights into org health, gaps, and forecasts

### Access
Click light bulb icon (💡) in top navigation bar

### Layout

#### Top Section: Key Metrics
- **Visual**: Two circular charts side-by-side
- **Metrics**:
  - Total positions (org chart)
  - Total people
  - Vacancies
  - Allocations

#### Middle Section: Detailed Breakdowns
**People Analysis**:
- Total count
- Single role vs multiple roles distribution
- Allocation status (allocated vs not allocated)
- Alert indicators for issues

**Accountabilities**:
- Assigned vs unassigned count
- Gap identification (🔥 fire icon for alerts)

#### Bottom Section: Forecasts
**Chart Type**: Bar chart

**Metrics Available**:
- Position count
- Headcount (grouped by vacancy status)
- Effort/FTE (monthly scale)
- Compensation (monthly scale)
- Hours worked

**Time Dimension**: Monthly projections (Jan-Sep shown)

**Interactions**:
- Expandable sections
- Drill-down into details (> arrows)
- Selectable data sources
- Customizable groupings

---

## Role Management

### Role Types

#### Standard Roles
- Pre-defined role templates
- Industry standard roles (CTO, COO, CMO, etc.)
- Linked to role library

#### Non-Standard Roles
- Custom roles created by organization
- Marked with "Non-standard" badge
- Fully customizable

#### AI Roles
- New category: AI agent roles
- Specialized AI functions
- Can be standard or non-standard

### Role Properties

#### Core Properties
- **Role title**: Name of the role
- **Description**: Detailed role description
- **Category**: Management, Operations, Strategy, etc.
- **Assigned person**: Who fills the role (can be AI)
- **Manager**: Reporting relationship
- **FTE allocation**: Percentage of time/capacity
- **Responsibilities**: List of accountability items

#### AI-Specific Properties
- **AI used**: Dropdown to indicate AI involvement
  - No AI in use
  - AI-assisted (human + AI)
  - Fully AI agent
- **AI agent type**: If fully AI, what type of agent

### Role Views

#### Roles View (Active in Screenshots)
- Focus on role definitions
- Role-to-person assignments
- Responsibility matrices

#### Accountabilities View
- Function: Map accountabilities to roles
- Shows gaps (unassigned accountabilities)
- RACI-style assignment

#### Positions View
- Traditional position-based view
- Position hierarchy
- Position properties

#### Groups View
- Team/group organization
- Cross-functional groups
- Project teams

---

## Data Model & Calculations

### Calculated Metrics

#### Position Metrics
- Position count (total positions)
- Filled positions
- Vacant positions
- Vacancy FTE (sum)
- Vacancy compensation (sum)

#### People Metrics
- Total headcount
- People with single role
- People with multiple roles
- Allocated people
- Unallocated people

#### Role Metrics
- Role count (sum)
- Role FTE (sum)
- Role compensation (sum)

#### AI Metrics
- AI agent roles (count)
- AI agent roles (FTE)
- AI vs human ratio
- AI capacity utilization

#### Hierarchy Metrics
- Span of control (avg, min, max)
- Layers above (count)
- Layers below (count)
- Total layers
- Org depth

#### Accountability Metrics
- Total accountabilities
- Assigned accountabilities
- Unassigned accountabilities
- Accountability gaps

### Forecasting

#### Time Dimensions
- Monthly
- Quarterly
- Yearly

#### Forecast Types
- **Position count**: Planned positions over time
- **Headcount**: People count projections
- **Effort (FTE)**: FTE projections
- **Compensation**: Budget projections
- **Hours worked**: Capacity projections

#### Grouping Options
- By department
- By vacancy status
- By role type
- By location
- By AI vs human

---

## Feature Gap Analysis

### What OrgChartAI Already Has ✓

Based on the earlier codebase exploration:

#### Org Chart Visualization ✓
- Hierarchical tree rendering
- D3.js visualization
- Drag-drop positioning
- Multiple layouts (26+ options)
- Zoom controls

#### Data Management ✓
- PostgreSQL database
- Org units, positions, employees
- Hierarchical relationships
- Audit trail

#### Multiple Views ✓
- Org chart view
- Functional chart view
- People & positions view
- Change plan view

#### AI Service (Partial) ✓
- AI service exists (port 8001)
- MCP client for AI integration
- Field matching AI
- AI chart generator

#### Scenario Planning (Partial) ✓
- Scenario tables exist
- Change comparison
- Scenario explorer

#### HRIS Integration ✓
- SuccessFactors integration
- Field mapping
- Sync history

### Critical Missing Features ❌

#### 1. AI Agent as Position ❌
**What's Missing**:
- Cannot add AI agents as employees/positions
- No "AI" entity type in database
- No visual distinction for AI nodes (purple border)
- No AI status property on positions

**Required**:
- `ai_agent` table
- `ai_agent_assignment` linking AI to positions
- `ai_status` enum on positions
- Frontend: AI node styling (purple border)
- Frontend: AI avatar/icons

#### 2. AI Status Tracking ❌
**What's Missing**:
- No "AI used" property on roles/positions
- No tracking of AI vs human vs hybrid
- No AI agent counts in metrics
- No "AI agent roles (count)" calculation
- No "AI agent roles (FTE)" calculation

**Required**:
- `ai_usage_type` enum (none, assisted, augmented, full_agent)
- AI metrics calculations
- API endpoints for AI statistics
- Frontend: AI status toggle in properties panel

#### 3. OrgPilot AI Chat Interface ❌
**What's Missing**:
- No conversational AI interface
- No "Ask me anything..." chat input
- No Agent/Advisor modes
- No contextual org structure Q&A

**Required**:
- Chat UI component (bottom right)
- "OrgPilot AI" button in top nav
- LLM integration with org context
- Chat history storage
- Streaming responses

#### 4. Scenario Summary Dashboard ❌
**What's Missing**:
- No comprehensive dashboard view
- No light bulb icon trigger
- No circular metrics charts
- No vacancy/allocation statistics
- No people role distribution
- No accountability tracking

**Required**:
- Right panel dashboard mode
- Key statistics calculations
- Circular/donut chart components
- Vacancy analysis
- Role distribution analysis
- Alert system (🔥 icons for issues)

#### 5. Forecast Sheet with Bar Charts ❌
**What's Missing**:
- No monthly forecast projections
- No bar chart visualization for forecasts
- No headcount planning by month
- No compensation forecasting
- No FTE projections

**Required**:
- `forecast` table with time series data
- Monthly aggregation queries
- Bar chart component
- Forecast calculation engine
- API: `/api/v1/forecast` endpoints

#### 6. Advanced Properties Panel ❌
**What's Missing**:
- No comprehensive properties panel
- No toggle switches for display options
- No "AI status" property toggle
- No span of control calculations
- No custom calculations
- Limited group calculations

**Required**:
- Right panel component with tabs
- Display properties toggles
- Group calculations section
- Custom calculation builder
- Save display preferences

#### 7. Role Management System ❌
**What's Missing**:
- No role detail panel
- No "Non-standard" role badges
- No role template system
- No responsibilities tracking
- Limited accountability assignment

**Required**:
- Role detail panel (right side)
- Role template library
- `role_template` table
- `responsibility` table
- Role-to-template linking
- Badge system for role types

#### 8. Views Dropdown System ❌
**What's Missing**:
- No unified views dropdown
- Views are separate routes (not integrated switcher)
- No "+ Add a view" feature
- No custom views

**Required**:
- Views selector component
- View management system
- Custom view builder
- Save user view preferences

#### 9. Filter System ❌
**What's Missing**:
- No "Filter: Top item" feature
- Cannot filter hierarchy to specific person
- No "Clear" button for filters
- Limited filtering options

**Required**:
- Top item filter with autocomplete
- Filter state management
- Clear/reset filters
- Multiple filter types (department, role, status)

#### 10. Layers Control ❌
**What's Missing**:
- No "Layers: X below" control
- Cannot limit hierarchy depth displayed
- No "X above" view

**Required**:
- Layers control component
- Hierarchy depth limiting
- API: query parameter for depth
- Visual indicator of hidden layers

#### 11. Roles/Accountabilities/Positions/Groups Toggle ❌
**What's Missing**:
- No role-based view paradigm
- No toggle between paradigms
- Only traditional position hierarchy

**Required**:
- Roles dropdown menu
- Accountabilities view mode
- Groups view mode
- Mode state management

#### 12. Accountability System ❌
**What's Missing**:
- Limited accountability tracking
- No accountability gap analysis
- No unassigned accountability alerts
- Tables exist but not fully integrated

**Required**:
- Full accountability management UI
- Gap detection algorithm
- Alert system for 154 unassigned (like screenshot)
- Accountability assignment workflow

#### 13. Advanced Metrics ❌
**What's Missing**:
- No vacancy FTE calculations
- No vacancy compensation tracking
- No span of control (avg, min, max)
- No role distribution analysis
- No "single role vs multiple roles" metric

**Required**:
- Advanced SQL queries for metrics
- Aggregation functions
- API endpoints for all metrics
- Frontend: metric display components

#### 14. People Allocation Tracking ❌
**What's Missing**:
- No "allocated vs not allocated" metric
- No tracking of people without role assignments
- No alerts for unallocated people

**Required**:
- Allocation status calculation
- `allocation_status` derived field
- Alert logic (fire icon for 93 unallocated)
- People allocation dashboard

#### 15. Scenario Comparison UI ❌
**What's Missing**:
- Change plan view exists but limited
- No side-by-side scenario view
- No visual diff for scenarios

**Required**:
- Split-screen scenario comparison
- Diff highlighting
- Change impact metrics
- Comparison dashboard

---

## Implementation Priority

### Phase 1: Core AI Features (High Priority)
1. **AI Agent as Position** - Foundation for all AI features
2. **AI Status Tracking** - Track AI adoption
3. **AI Metrics** - Count and FTE calculations

### Phase 2: UI/UX Enhancements (High Priority)
4. **Properties Panel** - Comprehensive right panel
5. **Views Dropdown** - Unified view switcher
6. **Filter System** - Top item filtering
7. **Layers Control** - Depth limiting

### Phase 3: Analytics & Insights (Medium Priority)
8. **Scenario Summary Dashboard** - Key metrics
9. **Forecast Sheet** - Monthly projections
10. **Advanced Metrics** - All calculated fields

### Phase 4: Role Management (Medium Priority)
11. **Role Detail Panel** - Full role management
12. **Role Templates** - Standard role library
13. **Accountability System** - Gap tracking

### Phase 5: AI Intelligence (High Value)
14. **OrgPilot AI Chat** - Conversational interface
15. **AI Recommendations** - Proactive suggestions
16. **Scenario Generation** - AI-powered org design

---

## Technical Architecture Requirements

### Database Schema Additions

#### New Tables Needed
- `ai_agent` - AI agent definitions
- `ai_agent_assignment` - AI to position mapping
- `role_template` - Standard role library
- `responsibility` - Detailed responsibilities
- `responsibility_assignment` - Map to positions
- `forecast_data` - Time series forecasts
- `custom_view` - User-defined views
- `display_preferences` - User UI preferences
- `ai_chat_history` - OrgPilot conversations
- `ai_recommendation` - Already exists, expand

#### Schema Modifications
- `position`: Add `ai_usage_type` enum
- `position`: Add `ai_status` field
- `position`: Add `role_template_id` FK
- `employee`: Add `allocation_status` computed field
- `assignment`: Add `is_ai_agent` boolean

### API Endpoints Needed

#### AI Agent Management
- `POST /api/v1/ai-agents` - Create AI agent
- `GET /api/v1/ai-agents` - List AI agents
- `PUT /api/v1/ai-agents/{id}` - Update AI agent
- `DELETE /api/v1/ai-agents/{id}` - Remove AI agent
- `POST /api/v1/positions/{id}/assign-ai` - Assign AI to position

#### Metrics & Analytics
- `GET /api/v1/metrics/ai-adoption` - AI vs human stats
- `GET /api/v1/metrics/vacancy-analysis` - Vacancy metrics
- `GET /api/v1/metrics/span-of-control` - Hierarchy metrics
- `GET /api/v1/metrics/allocation-status` - People allocation
- `GET /api/v1/metrics/accountability-gaps` - Unassigned accountabilities

#### Forecasting
- `GET /api/v1/forecast/headcount` - Monthly headcount projections
- `GET /api/v1/forecast/fte` - FTE projections
- `GET /api/v1/forecast/compensation` - Budget projections
- `POST /api/v1/forecast` - Create forecast data

#### OrgPilot AI
- `POST /api/v1/orgpilot/chat` - Send chat message
- `GET /api/v1/orgpilot/history` - Get chat history
- `POST /api/v1/orgpilot/analyze` - Analyze org structure
- `POST /api/v1/orgpilot/recommend` - Get recommendations

#### Role Management
- `GET /api/v1/role-templates` - Get role library
- `POST /api/v1/roles/{id}/responsibilities` - Add responsibilities
- `GET /api/v1/roles/{id}/details` - Full role details

### Frontend Components Needed

#### React Components
- `AIAgentNode.tsx` - AI-styled org node (with purple border)
- `OrgPilotChat.tsx` - Chat interface
- `PropertiesPanel.tsx` - Right panel with all toggles
- `ScenarioSummaryDashboard.tsx` - Analytics dashboard
- `ForecastChart.tsx` - Bar chart component
- `RoleDetailPanel.tsx` - Role management panel
- `ViewsDropdown.tsx` - View switcher
- `TopItemFilter.tsx` - Hierarchy filter
- `LayersControl.tsx` - Depth control
- `RolesToggle.tsx` - Paradigm switcher
- `CircularMetric.tsx` - Donut chart for metrics
- `AlertBadge.tsx` - Fire icon for issues

#### State Management
- AI agent state (Zustand store)
- Properties panel state
- Chat history state
- Filter state
- View preferences state

### AI/ML Requirements

#### LLM Integration
- **Model**: GPT-4, Claude 3 Opus, or Llama 3
- **Context**: Inject full org structure into prompts
- **Capabilities**:
  - Answer questions about org
  - Recommend changes
  - Generate scenarios
  - Explain metrics
- **Streaming**: Real-time response streaming

#### Training Data
- Historical org structures
- Best practices corpus
- Industry benchmarks
- Role definitions library

#### Model Types Needed
- **Conversational**: OrgPilot chat
- **Analytical**: Metric calculations and insights
- **Generative**: Scenario generation
- **Classification**: Role categorization
- **NLP**: Field matching, semantic search

---

## Conclusion

Functionly represents a mature AI-assisted organizational design platform with comprehensive features for:

1. **AI Integration**: First-class AI agents in org structure
2. **Visual Analytics**: Rich dashboards and metrics
3. **Forecasting**: Time-based workforce planning
4. **Role Management**: Sophisticated role and accountability system
5. **AI Assistance**: Conversational interface for guidance

OrgChartAI has a strong foundation but requires significant enhancements in:
- AI agent integration
- Analytics dashboards
- Forecasting capabilities
- AI-powered chat interface
- Advanced metrics and calculations

The implementation will require database schema changes, new API endpoints, extensive frontend components, and LLM integration.

---

**Next Steps**:
1. Review and approve this documentation
2. Create detailed database schema design
3. Design API specifications
4. Build component mockups
5. Implement in phases (as prioritized above)

