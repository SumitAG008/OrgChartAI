# UI/UX Requirements Documentation
## Functionly-Style Org Intelligence Platform Interface

---

## 🎯 Overview

This document defines the exact UI/UX requirements to achieve the features shown in the Functionly-style interface. The platform must support multiple view types, scenario planning, AI-powered recommendations, and interactive org chart manipulation.

---

## 🖼️ 1. Main Application Layout

### **A. Top Navigation Bar**

**Components:**
- **Left Side:**
  - Application title/logo (e.g., "Future Org with AI Roles")
  - Tag management: "Add tag" button
  - Template selector button
  - Current scenario name (if in scenario mode)

- **Right Side:**
  - Share icon/button
  - Download/Export icon/button
  - Theme toggle (light/dark mode)
  - Copy button
  - **"OrgPilot AI" button** (prominent, purple, with sparkle icon) - Opens AI assistant
  - User profile icon/dropdown

**Requirements:**
- Sticky header (always visible)
- Responsive design for mobile
- Clear visual hierarchy

### **B. Left Sidebar**

**Structure:**
```
┌─────────────────────────────┐
│  Org chart                  │
│  ─────────────────────────  │
│  Views                      │
│  ─────────────────────────  │
│  • Org chart (Default)      │
│  • People & positions       │
│  • Functional chart         │
│  • Forecast sheet           │
│  • Change plan              │
│  ─────────────────────────  │
│  [+ Add a view]             │
│  ─────────────────────────  │
│  [Scenario explorer]        │
└─────────────────────────────┘
```

**View Types:**

1. **Org chart (Default)**
   - Icon: Stacked blocks (yellow/blue)
   - Description: "Edit positions by adding people and roles in a traditional chart"
   - Features:
     - Hierarchical tree view
     - Drag-and-drop positioning
     - Add/edit/delete nodes
     - Expand/collapse branches

2. **People & positions**
   - Icon: Overlapping rectangles
   - Description: "View and edit people and positions"
   - Features:
     - List/grid view of people
     - Position management
     - Assignment management
     - Filter and search

3. **Functional chart**
   - Icon: Horizontal bars (red/black)
   - Description: "Edit roles and accountabilities in a functional chart"
   - Features:
     - Functional grouping view
     - Role-based visualization
     - Accountability mapping
     - Cross-functional relationships

4. **Forecast sheet**
   - Icon: Bar chart with upward arrow
   - Description: "View and edit the forecast sheet"
   - Features:
     - Headcount forecasting
     - Budget projections
     - Timeline view
     - Scenario comparison

5. **Change plan**
   - Icon: Overlapping colored blocks
   - Description: "Compare this scenario with another to see changes"
   - Features:
     - Side-by-side comparison
     - Change highlighting
     - Impact analysis
     - Approval workflow

**Requirements:**
- Collapsible sidebar
- Active view highlighted
- Smooth transitions between views
- Mobile: Drawer menu

### **C. Main Canvas Area**

**Components:**
- **Control Bar** (above chart):
  - Properties dropdown
  - Filter: "Filter: Top item" dropdown
  - Layers indicator: "Layers: 2 below"
  - Layout selector: "Layout: Narrow" dropdown
  - Roles toggle

- **Org Chart Visualization:**
  - Interactive D3.js-based chart
  - Zoom and pan controls
  - Node selection
  - Connection lines (reporting relationships)

- **AI Chat Assistant** (bottom right):
  - Chat bubble: "Ask me anything..."
  - Paper airplane icon
  - Opens conversational AI interface

**Requirements:**
- Responsive canvas (fills available space)
- Smooth zoom/pan interactions
- Touch-optimized for mobile
- Keyboard shortcuts support

---

## 🎨 2. Node Design and Styling

### **A. Node Types**

1. **Human Employee Node**
   - Shape: Rounded rectangle
   - Color: Light blue background
   - Content:
     - Person icon/avatar
     - Name (e.g., "Cly Mengue")
     - Title (e.g., "CTO")
     - Full title (e.g., "Chief Technology Officer")
     - FTE indicator (e.g., "100%")
   - Border: Standard (blue when selected)

2. **AI Agent Node**
   - Shape: Rounded rectangle
   - Color: Purple background
   - Content:
     - AI icon (distinctive)
     - Agent name (e.g., "AI Agent 'Eve'")
     - Role title (e.g., "AI Cross-Functional Integrator")
     - Full description
     - Status indicator
   - Border: Standard (purple when selected)

3. **Vacant Position Node**
   - Shape: Rounded rectangle
   - Color: Gray/light background
   - Content:
     - Vacant icon
     - Position title
     - "Vacant" label
   - Border: Dashed

4. **Container Node** (Org Unit)
   - Shape: Larger rounded rectangle or container
   - Color: Subtle background with border
   - Content:
     - Org unit name
     - Headcount
     - Cost center (if applicable)

### **B. Node States**

- **Default**: Standard styling
- **Selected**: Highlighted border, shadow
- **Hover**: Slight elevation, tooltip
- **Temporary Assignment**: Dashed border, different color
- **Vacant**: Grayed out, "Vacant" indicator

### **C. Node Interactions**

- **Click**: Select node, show details panel
- **Double-click**: Edit node
- **Long-press** (mobile): Context menu
- **Drag**: Move node (with validation)
- **Hover**: Show tooltip with quick info

---

## 🔗 3. Edge (Connection) Design

### **A. Edge Types**

1. **Direct Reporting Line**
   - Style: Solid line
   - Color: Gray/dark gray
   - Arrow: Points upward (to manager)
   - Thickness: Standard

2. **Dotted-Line Reporting**
   - Style: Dashed line
   - Color: Lighter gray
   - Arrow: Points upward
   - Thickness: Standard

3. **Temporary Assignment**
   - Style: Dashed, curved
   - Color: Orange/yellow
   - Arrow: Bidirectional or curved
   - Thickness: Slightly thicker

4. **Collaboration Line**
   - Style: Curved, dotted
   - Color: Light blue
   - Arrow: None or bidirectional
   - Thickness: Thin

### **B. Edge Interactions**

- **Hover**: Highlight connection
- **Click**: Show relationship details
- **Animated**: When temporary assignment starts/ends

---

## 📊 4. Scenario Explorer Panel

### **A. Panel Structure**

**Left Panel (Scenario Explorer):**
```
┌─────────────────────────────┐
│  Org chart [dropdown]       │
│  Related | Export           │
│  ─────────────────────────  │
│  [Scenario explorer]        │ ← Active (purple background)
│  ─────────────────────────  │
│  Quick add                  │
│  [Position] [Role] [Bus...] │ ← Horizontal scrollable
│  [Cost ce...] [Depart...]   │
│  [Division] [Region]        │
│  ─────────────────────────  │
│  Not in org chart           │
│  • People (+ 93)            │
│  • In org chart (10)        │
│  ─────────────────────────  │
│  Standard roles             │
│  • Customer                 │
│  • Engineering              │
│  • Finance and Governance   │
│  • Management               │
│  ─────────────────────────  │
│  Functions & Accountabilities│
└─────────────────────────────┘
```

### **B. Quick Add Section**

**Components:**
- Horizontal scrollable button row
- Icons for each entity type:
  - Position
  - Role
  - Business Unit
  - Cost Center
  - Department
  - Division
  - Region

**Interaction:**
- Click icon → Opens creation form
- Drag-and-drop from list to canvas

### **C. Filtering and Grouping**

- **"Not in org chart"**: Shows people/positions not yet assigned
- **"Standard roles"**: Pre-defined role templates
- **"Functions & Accountabilities"**: Functional groupings

---

## ⚙️ 5. Properties and Filter Panel

### **A. Middle Panel Structure**

```
┌─────────────────────────────┐
│  [Properties] [Filter: ...] │ ← Tabs
│  ─────────────────────────  │
│  Displayed properties       │
│  [Dropdown]                 │
│  ─────────────────────────  │
│  Group calculations         │
│  [Dropdown]                 │
│  ─────────────────────────  │
│  [Search icon] [Refresh]    │
└─────────────────────────────┘
```

### **B. Properties Tab**

**Features:**
- Select which properties to display on nodes
- Group calculations (sum, avg, count)
- Custom property definitions

### **C. Filter Tab**

**Features:**
- Filter by top-level item
- Multi-select filters
- Save filter presets

---

## 📈 6. Metrics and Calculations Panel

### **A. Right Panel Structure**

```
┌─────────────────────────────┐
│  Vacancies                  │
│  ☑ Vacancy (count)          │
│  ☑ Vacancy FTE (sum)        │
│  ☑ Vacancy compensation     │
│    (sum) [link icon]         │
│  ☑ Include vacancies in     │
│    all calculations         │
│  ─────────────────────────  │
│  Span of control            │
│  ☑ Span of control (avg)    │
│  ☑ Span of control (max)    │
│  ☑ Span of control (min)    │
│  ─────────────────────────  │
│  Roles                      │
│  ☑ Role count (sum)         │
│  ☑ Role FTE (sum)           │
│  ☑ Role compensation (sum) │
│    [link icon]              │
│  ─────────────────────────  │
│  Layers                     │
│  ☑ Layers above (count)     │
│  ☑ Layers below (count)     │
│  ─────────────────────────  │
│  Custom                     │
│  [+ Add a custom calculation]│
└─────────────────────────────┘
```

### **B. Toggle Controls**

- Each metric has a toggle switch
- When enabled, metric appears on nodes/chart
- Link icon indicates drill-down capability
- Real-time calculation updates

### **C. Metric Categories**

1. **Vacancies**
   - Count, FTE sum, compensation sum
   - Include in calculations toggle

2. **Span of Control**
   - Average, max, min
   - Per manager calculation

3. **Roles**
   - Count, FTE sum, compensation sum

4. **Layers**
   - Layers above (to CEO)
   - Layers below (to front-line)

5. **Custom Calculations**
   - User-defined formulas
   - Aggregate functions

---

## 🤖 7. AI Assistant (OrgPilot AI)

### **A. Chat Interface**

**Trigger:**
- Click "OrgPilot AI" button (top right)
- Or click chat bubble (bottom right of canvas)

**Interface:**
```
┌─────────────────────────────┐
│  OrgPilot AI        [×]     │
│  ─────────────────────────  │
│  👋 Hi! How can I help?     │
│                              │
│  [Ask me anything...]        │
│  [Send icon]                 │
└─────────────────────────────┘
```

### **B. AI Capabilities**

**Use Cases:**
1. **"Suggest best team for Project X"**
   - AI analyzes required skills
   - Recommends team composition
   - Shows reasoning

2. **"Propose future-state org for Region Y"**
   - AI analyzes current structure
   - Generates design alternatives
   - Shows impact analysis

3. **"What are the skill gaps in Engineering?"**
   - AI identifies gaps
   - Recommends solutions
   - Shows cost/timeline

4. **"Who should report to the new CTO?"**
   - AI analyzes org structure
   - Recommends reporting lines
   - Considers span of control

### **C. AI Response Format**

- **Text responses** with markdown formatting
- **Visual recommendations** (charts, diagrams)
- **Action buttons** (Apply, Reject, Modify)
- **Confidence scores** for recommendations

---

## 🎯 8. Interactive Features

### **A. Drag and Drop**

**Supported Actions:**
- Move nodes to new positions
- Change reporting relationships
- Assign people to positions
- Create new connections

**Validation:**
- Check for circular references
- Validate business rules
- Show warnings for invalid moves
- Require approval for significant changes

### **B. Zoom and Pan**

**Controls:**
- Mouse wheel: Zoom in/out
- Drag: Pan canvas
- Zoom buttons: Zoom in, zoom out, fit to screen
- Touch gestures (mobile): Pinch to zoom, swipe to pan

**Requirements:**
- Smooth animations
- Maintain node readability
- Performance optimization for large orgs

### **C. Search and Filter**

**Search:**
- Global search bar (top)
- Search by name, title, department
- Real-time filtering
- Highlight matches

**Filter:**
- By department/org unit
- By location
- By employment type
- By status (active, vacant, etc.)
- Save filter presets

### **D. Expand/Collapse**

- Click node to expand/collapse children
- "Expand all" / "Collapse all" buttons
- Remember user preferences
- Lazy loading for large orgs

---

## 📱 9. Mobile Optimization

### **A. Touch Interactions**

- **Tap**: Select node
- **Double-tap**: Edit
- **Long-press**: Context menu
- **Pinch**: Zoom
- **Swipe**: Pan
- **Swipe left/right**: Navigate between views

### **B. Mobile Layout**

- **Collapsible sidebars**: Drawer menus
- **Bottom navigation**: Quick access to main views
- **Floating action button**: Quick add
- **Responsive charts**: Adapt to screen size

### **C. Performance**

- Lazy loading for large orgs
- Virtual scrolling for lists
- Optimized rendering for mobile devices

---

## 🎨 10. Visual Design System

### **A. Color Palette**

**Brand Colors:**
- **InsightSheet Lite**: Blue (#0066CC)
- **InsightSheet File**: Green (#00AA44)
- **InsightSheet Elite**: Purple (#6633CC)
- **Meldra**: Teal (#00AAAA)

**Node Colors:**
- **Permanent Employee**: Blue gradient
- **Fixed-Term**: Green gradient
- **Contractual**: Orange gradient
- **Temporary**: Red gradient
- **AI Agent**: Purple gradient
- **Vacant**: Gray

### **B. Typography**

- **Headings**: Bold, 16-24px
- **Body**: Regular, 14-16px
- **Labels**: Medium, 12-14px
- **Font Family**: System fonts (San Francisco, Segoe UI, Roboto)

### **C. Spacing and Layout**

- **Grid System**: 8px base unit
- **Padding**: 16px standard, 24px for panels
- **Border Radius**: 8px for cards, 4px for buttons
- **Shadows**: Subtle elevation for selected items

---

## 🔄 11. Workflow Features

### **A. Temporary Assignments**

**Visual Behavior:**
- Node moves to new position
- Dashed border and connection
- Original position indicator remains
- Auto-revert on assignment end

**User Actions:**
- Create temporary assignment
- Set start/end dates
- Extend assignment
- End assignment early

### **B. Mass Position Creation**

**Workflow:**
1. Click "Quick add" → Position
2. Fill form with:
   - Job profile
   - Count (e.g., 40)
   - Org unit
   - Default manager
3. System generates positions
4. Positions appear as vacant nodes

**Visual:**
- Grouped vacant positions
- Collapsible group view
- Individual position codes

### **C. Scenario Planning**

**Workflow:**
1. Create new scenario
2. Make changes (drag, add, remove)
3. Compare with current state
4. Generate change package
5. Submit for approval

**Visual:**
- Side-by-side comparison view
- Change highlighting (added/removed/modified)
- Impact metrics display

---

## 📤 12. Export and Sharing

### **A. Export Options**

- **PDF**: High-quality org chart
- **PNG/JPEG**: Image export
- **Excel**: Data export with structure
- **CSV**: Flat data export

### **B. Sharing**

- **Link sharing**: Generate shareable link
- **Permissions**: View-only, edit, admin
- **Embed**: Iframe embed code
- **Email**: Send to stakeholders

---

## ✅ 13. Accessibility Requirements

### **A. Keyboard Navigation**

- Tab: Navigate between elements
- Enter/Space: Activate buttons
- Arrow keys: Navigate chart
- Escape: Close modals

### **B. Screen Reader Support**

- ARIA labels on all interactive elements
- Alt text for icons
- Semantic HTML structure
- Focus indicators

### **C. Color Contrast**

- WCAG AA compliance
- High contrast mode support
- Color-blind friendly palette

---

## 🚀 14. Performance Requirements

### **A. Rendering Performance**

- **Large Orgs**: Support 10,000+ nodes
- **Initial Load**: < 3 seconds
- **Interaction Response**: < 100ms
- **Smooth Animations**: 60 FPS

### **B. Data Loading**

- **Lazy Loading**: Load children on expand
- **Pagination**: For large lists
- **Caching**: Cache frequently accessed data
- **Optimistic Updates**: Immediate UI feedback

---

## 📋 15. Feature Checklist

### **Core Features**
- [ ] Multi-view support (5 view types)
- [ ] Interactive org chart (D3.js)
- [ ] Drag-and-drop node manipulation
- [ ] Zoom and pan controls
- [ ] Search and filter
- [ ] Expand/collapse nodes
- [ ] Node selection and editing
- [ ] Connection line rendering
- [ ] Scenario explorer panel
- [ ] Properties and filter panel
- [ ] Metrics and calculations panel
- [ ] AI assistant (OrgPilot AI)
- [ ] Temporary assignment workflow
- [ ] Mass position creation
- [ ] Scenario planning and comparison
- [ ] Export (PDF, PNG, Excel)
- [ ] Sharing and permissions
- [ ] Mobile responsive design
- [ ] Touch-optimized interactions
- [ ] Real-time collaboration (future)

---

## 🎯 Summary

This UI/UX specification defines the exact requirements to achieve the Functionly-style interface, including:

1. **Multi-panel layout** with sidebar, canvas, and control panels
2. **Five distinct view types** for different use cases
3. **Interactive org chart** with D3.js visualization
4. **AI-powered assistant** for recommendations
5. **Scenario planning** with comparison views
6. **Mobile optimization** for touch interactions
7. **Comprehensive metrics** and calculations
8. **Workflow support** for temporary assignments and mass creation

All features must be implemented with attention to:
- **Performance** (large org support)
- **Accessibility** (WCAG compliance)
- **User experience** (intuitive, responsive)
- **Visual design** (consistent, branded)
