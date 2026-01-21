# UI/UX Redesign Plan - Functionly-Inspired Layout

## 🎨 Overview

This document outlines the UI/UX redesign to match Functionly's layout and improve user experience.

---

## 📐 Layout Structure

### **Three-Panel Layout (Like Functionly)**

```
┌─────────────────────────────────────────────────────────────┐
│  Top Navigation Bar                                          │
├──────────┬──────────────────────────────┬──────────────────┤
│          │                               │                  │
│  Left    │      Center Canvas            │   Right Panel    │
│  Sidebar │      (Org Chart View)         │   (Details)      │
│          │                               │                  │
│  - Views │      - Interactive Chart      │   - Position     │
│  - Quick │      - Zoom Controls          │     Details      │
│    Add   │      - Filter/Layers           │   - AI Chat      │
│  - People│                               │   - Calculations │
│  - Roles │                               │                  │
│          │                               │                  │
└──────────┴──────────────────────────────┴──────────────────┘
```

---

## 🎯 Component Breakdown

### **1. Top Navigation Bar**

**Elements:**
- Logo + "OrgChart with AI Intelligence" (dropdown)
- "Add tag" button
- "Template" button
- Icons: Edit, Download, Share, Copy
- **"OrgPilot AI"** button (purple, prominent)
- User profile icon (dropdown)

**Implementation:**
```typescript
// frontend/src/components/Layout/TopNav.tsx
```

---

### **2. Left Sidebar**

#### **Section 1: Views**
- Org chart (Default)
- People & positions
- Functional chart
- Forecast sheet
- Change plan
- "+ Add a view"

#### **Section 2: Scenario Explorer** (Purple highlight)
- Active scenario dropdown
- Scenario list

#### **Section 3: Quick Add**
Grid of buttons:
- Position
- Role
- Business Unit
- Cost Center
- Department
- Division
- Region

#### **Section 4: Not in org chart**
- **People** (expandable)
  - List of people not assigned
  - "+ 93" count badge
  - Profile pictures + names

#### **Section 5: In org chart**
- Hierarchy dropdown
- List of people in chart

#### **Section 6: Standard roles**
- Predefined roles library

#### **Section 7: Functions & Accountabilities**
- Functions list
- Accountabilities list

**Implementation:**
```typescript
// frontend/src/components/Layout/LeftSidebar.tsx
```

---

### **3. Center Canvas (Org Chart View)**

**Features:**
- Interactive org chart visualization
- Zoom controls (bottom right)
- Filter dropdown: "Top item"
- Layers dropdown: "2 below"
- Properties button
- Building blocks icon (chart type)

**Implementation:**
```typescript
// frontend/src/components/OrgChart/InteractiveChart.tsx
```

---

### **4. Right Panel (Details)**

**When Position Selected:**

#### **Position Header**
- Position title (e.g., "AI Market Analyst")
- Download icon
- Close icon

#### **Position Details**
- Icon + title + percentage (e.g., "100%")
- **Responsibilities** (expandable)
  - List of responsibilities
  - Add/Edit buttons
- **Accountabilities** (expandable)
  - Count badge (e.g., "0")
  - "+" button to add
- **Move down in chart** dropdown
- **Calculations**
  - Circular charts for:
    - Layers
    - Span
  - Info icons

#### **AI Chat Bubble**
- "Ask me anything..." input
- Star icon (AI indicator)
- Send button
- Overlays bottom of panel

**Implementation:**
```typescript
// frontend/src/components/Layout/RightPanel.tsx
// frontend/src/components/AI/AIChatBubble.tsx
```

---

## 🎨 Design System

### **Colors**
- **Primary**: Royal Blue (#4169E1)
- **Secondary**: Purple (#9333EA) - for AI features
- **Success**: Green (#10B981)
- **Warning**: Yellow (#F59E0B)
- **Error**: Red (#EF4444)
- **Background**: Light Gray (#F9FAFB)
- **Text**: Dark Gray (#111827)

### **Typography**
- **Headings**: Inter, Bold
- **Body**: Inter, Regular
- **Code/Mono**: JetBrains Mono

### **Spacing**
- Base unit: 4px
- Padding: 16px, 24px, 32px
- Margins: 8px, 16px, 24px, 32px

### **Components**
- **Buttons**: Rounded corners (8px), padding 12px 24px
- **Cards**: White background, shadow (sm), rounded (12px)
- **Inputs**: Border 2px, rounded (8px), padding 12px

---

## 📱 Responsive Design

### **Desktop (> 1024px)**
- Full three-panel layout
- All features visible

### **Tablet (768px - 1024px)**
- Collapsible sidebars
- Center canvas remains full width

### **Mobile (< 768px)**
- Single panel at a time
- Hamburger menu for navigation
- Bottom sheet for details

---

## 🚀 Implementation Steps

### **Phase 1: Layout Structure**
1. ✅ Create three-panel layout component
2. ✅ Implement TopNav component
3. ✅ Implement LeftSidebar component
4. ✅ Implement RightPanel component
5. ✅ Add responsive breakpoints

### **Phase 2: Left Sidebar**
1. ✅ Views section
2. ✅ Scenario Explorer
3. ✅ Quick Add panel
4. ✅ People sections
5. ✅ Standard roles
6. ✅ Functions & Accountabilities

### **Phase 3: Center Canvas**
1. ✅ Interactive org chart
2. ✅ Zoom controls
3. ✅ Filter/Layers dropdowns
4. ✅ Properties panel

### **Phase 4: Right Panel**
1. ✅ Position details view
2. ✅ Responsibilities section
3. ✅ Accountabilities section
4. ✅ Calculations charts
5. ✅ AI Chat bubble

### **Phase 5: Integration**
1. ✅ Connect to backend APIs
2. ✅ Add state management
3. ✅ Implement real-time updates
4. ✅ Add error handling

---

## 🎯 Key Features to Implement

### **1. OrgPilot AI Button**
- Purple, prominent button in top nav
- Opens AI assistant panel
- Provides org design recommendations
- Answers questions about org structure

### **2. Quick Add Panel**
- Fast way to add org elements
- Drag-and-drop support
- Context-aware suggestions

### **3. Scenario Explorer**
- Manage multiple org scenarios
- Compare scenarios
- Switch between scenarios

### **4. AI Chat Bubble**
- Context-aware AI assistant
- Answers questions about selected position
- Provides recommendations
- Natural language interface

---

## 📝 Component Files to Create

```
frontend/src/
├── components/
│   ├── Layout/
│   │   ├── TopNav.tsx
│   │   ├── LeftSidebar.tsx
│   │   ├── RightPanel.tsx
│   │   └── MainLayout.tsx
│   ├── OrgChart/
│   │   ├── InteractiveChart.tsx
│   │   └── ZoomControls.tsx
│   ├── AI/
│   │   ├── AIChatBubble.tsx
│   │   └── OrgPilotButton.tsx
│   └── Scenario/
│       ├── ScenarioExplorer.tsx
│       └── QuickAddPanel.tsx
```

---

## ✅ Success Criteria

- [ ] Layout matches Functionly's three-panel design
- [ ] All sidebar sections functional
- [ ] Interactive org chart in center
- [ ] Right panel shows position details
- [ ] AI features integrated
- [ ] Responsive on all screen sizes
- [ ] Smooth animations and transitions
- [ ] Accessible (WCAG 2.1 AA)

---

**Next Steps:** Start with MainLayout component, then build out each section incrementally.
