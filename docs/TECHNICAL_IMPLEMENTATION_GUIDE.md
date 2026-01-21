# Technical Implementation Guide
## React Org Chart Libraries and Implementation Patterns

---

## 🎯 Overview

This guide provides technical implementation details for building the org chart visualization engine, including recommended libraries, implementation patterns, and best practices.

---

## 📚 Recommended React Org Chart Libraries

### **1. react-org-chart (coreseekdev)**

**Repository:** [https://github.com/coreseekdev/react-org-chart](https://github.com/coreseekdev/react-org-chart)

**Key Features:**
- High-performance D3-based SVG rendering
- Lazy-load children with custom function
- Handle up to **1 million collapsed nodes** and **5,000 expanded nodes**
- React component-based architecture
- Customizable node rendering

**Props:**
```typescript
interface ReactOrgChartProps {
  tree: TreeNode;              // Required: Nested data model
  nodeWidth?: number;           // Optional: Default 180
  nodeHeight?: number;         // Optional: Default 100
  nodeSpacing?: number;        // Optional: Default 12
  animationDuration?: number;  // Optional: Default 350ms
  lineType?: 'angle' | 'curve'; // Optional: Line connection type
}
```

**Data Model:**
```typescript
interface TreeNode {
  id: number | string;
  person: {
    name: string;
    title?: string;
    avatar?: string;
    // ... other person properties
  };
  children?: TreeNode[];
}
```

**Usage Example:**
```tsx
import ReactOrgChart from 'react-org-chart';

const orgData = {
  id: 1,
  person: { name: "CEO", title: "Chief Executive Officer" },
  children: [
    {
      id: 2,
      person: { name: "CTO", title: "Chief Technology Officer" },
      children: []
    }
  ]
};

<ReactOrgChart
  tree={orgData}
  nodeWidth={200}
  nodeHeight={120}
  nodeSpacing={16}
  animationDuration={400}
  lineType="curve"
/>
```

**When to Use:**
- High-performance requirements
- Large organizational structures (10,000+ nodes)
- Need lazy loading for performance
- D3.js-based rendering preferred

---

### **2. @unicef/react-org-chart**

**Repository:** [https://deepwiki.com/unicef/react-org-chart](https://deepwiki.com/unicef/react-org-chart)

**Key Features:**
- React component for displaying organizational charts
- D3.js-powered visualization
- Interactive navigation
- Export functionality (PDF, Image)
- Large-scale hierarchical data rendering

**Component Architecture:**
- Core rendering engine (D3.js)
- React component integration
- Export functionality
- User interactions (zoom, pan, expand/collapse)

**Data Structure:**
```typescript
interface OrgChartNode {
  id: string;
  person: {
    name: string;
    title: string;
    avatar?: string;
    // ... other properties
  };
  hasChild: boolean;
  hasParent: boolean;
  children?: OrgChartNode[];
  isHighlight?: boolean;
}
```

**When to Use:**
- Need export functionality (PDF, PNG)
- Interactive navigation required
- UNICEF-style organizational charts
- React-first architecture

---

### **3. Custom Implementation with D3.js**

**For Maximum Flexibility:**

If you need complete control over visualization, consider building a custom solution using D3.js directly.

**Advantages:**
- Full control over rendering
- Custom layouts (radial, matrix, network)
- Custom node/edge styling
- Integration with your design system

**Implementation Pattern:**
```typescript
import * as d3 from 'd3';

class OrgChartRenderer {
  private svg: d3.Selection<SVGSVGElement, unknown, null, undefined>;
  private treeLayout: d3.TreeLayout<OrgNode>;
  
  constructor(container: HTMLElement) {
    this.svg = d3.select(container)
      .append('svg')
      .attr('width', 1200)
      .attr('height', 800);
    
    this.treeLayout = d3.tree()
      .nodeSize([200, 300])
      .separation((a, b) => (a.parent === b.parent ? 1 : 2));
  }
  
  render(data: OrgNode[]) {
    const root = d3.hierarchy(data[0]);
    this.treeLayout(root);
    // Render nodes and links
  }
}
```

**When to Use:**
- Need custom visualization types (all 26 types)
- Maximum performance requirements
- Custom interaction patterns
- Integration with specific design system

---

## 🏗️ Implementation Architecture

### **A. Component Structure**

```
src/
├── components/
│   ├── OrgChart/
│   │   ├── OrgChartContainer.tsx      # Main container
│   │   ├── OrgChartCanvas.tsx        # D3 rendering canvas
│   │   ├── OrgChartNode.tsx          # Individual node component
│   │   ├── OrgChartEdge.tsx          # Connection line component
│   │   └── OrgChartControls.tsx      # Zoom, pan, search controls
│   ├── NodeTypes/
│   │   ├── EmployeeNode.tsx          # Human employee node
│   │   ├── AINode.tsx                # AI agent node
│   │   ├── VacantNode.tsx            # Vacant position node
│   │   └── ContainerNode.tsx        # Org unit container
│   └── Views/
│       ├── HierarchicalView.tsx      # Traditional hierarchy
│       ├── MatrixView.tsx            # Matrix structure
│       ├── NetworkView.tsx           # Network structure
│       ├── RadialView.tsx            # Radial layout
│       └── FunctionalView.tsx        # Functional chart
├── hooks/
│   ├── useOrgChart.ts                # Chart data management
│   ├── useZoomPan.ts                # Zoom and pan logic
│   ├── useNodeSelection.ts          # Node selection state
│   └── useLazyLoading.ts            # Lazy loading for large orgs
├── utils/
│   ├── layoutAlgorithms.ts           # Layout algorithms
│   ├── dataTransform.ts              # Data transformation
│   └── performance.ts                # Performance optimizations
└── types/
    └── orgChart.ts                   # TypeScript types
```

### **B. Data Transformation Layer**

Transform your database model to chart library format:

```typescript
// Transform from your data model to chart format
function transformToChartData(
  positions: Position[],
  employees: Employee[],
  orgUnits: OrgUnit[]
): TreeNode {
  // Build hierarchy from positions
  const positionMap = new Map(positions.map(p => [p.id, p]));
  const employeeMap = new Map(employees.map(e => [e.id, e]));
  
  // Find root position (no reports_to)
  const rootPosition = positions.find(p => !p.reports_to_position_id);
  
  function buildNode(position: Position): TreeNode {
    const employee = position.employee_id 
      ? employeeMap.get(position.employee_id)
      : null;
    
    const children = positions
      .filter(p => p.reports_to_position_id === position.id)
      .map(buildNode);
    
    return {
      id: position.id,
      person: {
        name: employee?.preferred_name || employee?.first_name || 'Vacant',
        title: position.position_title,
        avatar: employee?.photo,
        employmentType: employee?.employment_type,
        positionType: position.position_type,
        status: position.status
      },
      children: children.length > 0 ? children : undefined
    };
  }
  
  return rootPosition ? buildNode(rootPosition) : null;
}
```

### **C. Performance Optimization**

#### **1. Lazy Loading**

```typescript
const useLazyLoading = (node: TreeNode, maxDepth: number = 3) => {
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());
  
  const shouldLoadChildren = (node: TreeNode, depth: number) => {
    return depth < maxDepth || expandedNodes.has(node.id);
  };
  
  const loadChildren = async (nodeId: string) => {
    // Fetch children from API
    const children = await fetchNodeChildren(nodeId);
    return children;
  };
  
  return { shouldLoadChildren, loadChildren, expandedNodes, setExpandedNodes };
};
```

#### **2. Virtual Rendering**

For very large orgs (10,000+ nodes):

```typescript
const useVirtualRendering = (
  nodes: TreeNode[],
  viewport: { x: number; y: number; width: number; height: number }
) => {
  // Only render nodes visible in viewport
  const visibleNodes = useMemo(() => {
    return nodes.filter(node => isInViewport(node, viewport));
  }, [nodes, viewport]);
  
  return visibleNodes;
};
```

#### **3. Memoization**

```typescript
const MemoizedOrgChartNode = React.memo(OrgChartNode, (prev, next) => {
  return (
    prev.node.id === next.node.id &&
    prev.node.person.name === next.node.person.name &&
    prev.selected === next.selected
  );
});
```

---

## 🎨 Customization Guide

### **A. Node Styling**

```typescript
// Node styling based on employment type
const getNodeStyle = (node: TreeNode) => {
  const baseStyle = {
    width: 200,
    height: 120,
    borderRadius: 8,
    padding: 12
  };
  
  switch (node.person.employmentType) {
    case 'Permanent':
      return { ...baseStyle, backgroundColor: '#0066CC', color: '#fff' };
    case 'Contract':
      return { ...baseStyle, backgroundColor: '#FF8800', color: '#fff' };
    case 'Temporary':
      return { ...baseStyle, backgroundColor: '#FF4444', color: '#fff' };
    default:
      return { ...baseStyle, backgroundColor: '#CCCCCC', color: '#000' };
  }
};
```

### **B. Edge Styling**

```typescript
// Edge styling based on relationship type
const getEdgeStyle = (edge: Edge) => {
  switch (edge.type) {
    case 'direct':
      return { stroke: '#333', strokeWidth: 2, strokeDasharray: 'none' };
    case 'dotted-line':
      return { stroke: '#666', strokeWidth: 1, strokeDasharray: '5,5' };
    case 'temporary':
      return { stroke: '#FF8800', strokeWidth: 2, strokeDasharray: '10,5' };
    default:
      return { stroke: '#999', strokeWidth: 1 };
  }
};
```

### **C. Layout Algorithms**

```typescript
// Different layout algorithms for different view types
const layoutAlgorithms = {
  hierarchical: (root: TreeNode) => {
    // Tree layout (top-down)
    return d3.tree().nodeSize([200, 300])(d3.hierarchy(root));
  },
  
  radial: (root: TreeNode) => {
    // Radial layout (circular)
    return d3.tree().nodeSize([100, 200]).separation(() => 1)(
      d3.hierarchy(root)
    );
  },
  
  matrix: (nodes: TreeNode[]) => {
    // Grid layout for matrix structures
    return arrangeInGrid(nodes, { columns: 4, spacing: 20 });
  },
  
  forceDirected: (nodes: TreeNode[], links: Edge[]) => {
    // Force-directed layout for network structures
    return d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id(d => d.id))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(600, 400));
  }
};
```

---

## 🔄 Integration with Your Platform

### **A. Data Flow**

```
HRIS / Database
    ↓
API Layer (FastAPI)
    ↓
Data Transformation
    ↓
React Component (react-org-chart or custom)
    ↓
D3.js Rendering
    ↓
SVG Canvas
```

### **B. State Management**

```typescript
// Using Zustand or Redux for global state
interface OrgChartState {
  nodes: TreeNode[];
  selectedNode: string | null;
  expandedNodes: Set<string>;
  viewType: 'hierarchical' | 'matrix' | 'network' | 'radial';
  filters: FilterState;
  zoom: number;
  pan: { x: number; y: number };
}

const useOrgChartStore = create<OrgChartState>((set) => ({
  nodes: [],
  selectedNode: null,
  expandedNodes: new Set(),
  viewType: 'hierarchical',
  filters: {},
  zoom: 1,
  pan: { x: 0, y: 0 },
  
  setSelectedNode: (nodeId: string | null) => 
    set({ selectedNode: nodeId }),
  
  toggleExpanded: (nodeId: string) => 
    set((state) => {
      const expanded = new Set(state.expandedNodes);
      if (expanded.has(nodeId)) {
        expanded.delete(nodeId);
      } else {
        expanded.add(nodeId);
      }
      return { expandedNodes: expanded };
    }),
}));
```

### **C. API Integration**

```typescript
// Fetch org chart data
const fetchOrgChart = async (
  orgUnitId?: string,
  scenarioId?: string,
  asOfDate?: Date
) => {
  const response = await api.get('/org-chart', {
    params: {
      org_unit_id: orgUnitId,
      scenario_id: scenarioId,
      as_of_date: asOfDate?.toISOString()
    }
  });
  
  return transformToChartData(response.data);
};

// Update node position (drag and drop)
const updateNodePosition = async (
  nodeId: string,
  newReportsTo: string | null
) => {
  await api.post('/org-chart/update-position', {
    position_id: nodeId,
    reports_to_position_id: newReportsTo
  });
};
```

---

## 📱 Mobile Optimization

### **A. Touch Interactions**

```typescript
const useTouchInteractions = () => {
  const [touchStart, setTouchStart] = useState<{ x: number; y: number } | null>(null);
  
  const handleTouchStart = (e: TouchEvent) => {
    const touch = e.touches[0];
    setTouchStart({ x: touch.clientX, y: touch.clientY });
  };
  
  const handleTouchEnd = (e: TouchEvent) => {
    if (!touchStart) return;
    
    const touch = e.changedTouches[0];
    const deltaX = touch.clientX - touchStart.x;
    const deltaY = touch.clientY - touchStart.y;
    
    // Detect swipe
    if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 50) {
      // Horizontal swipe - navigate between views
    } else if (Math.abs(deltaY) > Math.abs(deltaX) && Math.abs(deltaY) > 50) {
      // Vertical swipe - scroll
    }
    
    setTouchStart(null);
  };
  
  return { handleTouchStart, handleTouchEnd };
};
```

### **B. Responsive Layout**

```typescript
const useResponsiveLayout = () => {
  const [dimensions, setDimensions] = useState({ width: 1200, height: 800 });
  
  useEffect(() => {
    const updateDimensions = () => {
      setDimensions({
        width: window.innerWidth,
        height: window.innerHeight - 100 // Account for header
      });
    };
    
    window.addEventListener('resize', updateDimensions);
    updateDimensions();
    
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);
  
  return dimensions;
};
```

---

## 🧪 Testing Strategy

### **A. Unit Tests**

```typescript
describe('OrgChartNode', () => {
  it('renders employee node correctly', () => {
    const node = {
      id: '1',
      person: { name: 'John Doe', title: 'Engineer' },
      children: []
    };
    
    render(<OrgChartNode node={node} />);
    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });
  
  it('handles vacant position', () => {
    const node = {
      id: '2',
      person: { name: 'Vacant', title: 'Manager' },
      children: []
    };
    
    render(<OrgChartNode node={node} />);
    expect(screen.getByText('Vacant')).toHaveClass('vacant');
  });
});
```

### **B. Performance Tests**

```typescript
describe('Performance', () => {
  it('renders 10,000 nodes in under 3 seconds', async () => {
    const largeOrg = generateLargeOrg(10000);
    const start = performance.now();
    
    render(<OrgChart tree={largeOrg} />);
    
    await waitFor(() => {
      expect(performance.now() - start).toBeLessThan(3000);
    });
  });
});
```

---

## 🚀 Deployment Considerations

### **A. Bundle Size Optimization**

```typescript
// Lazy load org chart component
const OrgChart = lazy(() => import('./components/OrgChart/OrgChartContainer'));

// Code splitting for different view types
const HierarchicalView = lazy(() => import('./components/Views/HierarchicalView'));
const MatrixView = lazy(() => import('./components/Views/MatrixView'));
```

### **B. CDN for D3.js**

```html
<!-- Consider using CDN for D3.js to reduce bundle size -->
<script src="https://d3js.org/d3.v7.min.js"></script>
```

---

## 📚 References

- [react-org-chart (coreseekdev)](https://github.com/coreseekdev/react-org-chart) - High-performance D3-based org chart
- [@unicef/react-org-chart](https://deepwiki.com/unicef/react-org-chart) - UNICEF's React org chart component
- [D3.js Documentation](https://d3js.org/) - Data-driven documents
- [React Performance Optimization](https://react.dev/learn/render-and-commit) - React rendering optimization

---

## 🎯 Summary

This guide provides:

1. **Recommended Libraries**: react-org-chart and @unicef/react-org-chart
2. **Implementation Architecture**: Component structure and data flow
3. **Performance Optimization**: Lazy loading, virtual rendering, memoization
4. **Customization**: Node/edge styling, layout algorithms
5. **Integration**: API integration, state management
6. **Mobile Optimization**: Touch interactions, responsive layout
7. **Testing**: Unit tests, performance tests
8. **Deployment**: Bundle optimization, CDN usage

Choose the library that best fits your needs, or build custom for maximum flexibility.
