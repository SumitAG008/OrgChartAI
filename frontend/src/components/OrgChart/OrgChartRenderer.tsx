import React, { useEffect, useRef, useState, useCallback } from 'react';
import { TreeNode } from '../../types';
import { OrgStructureType } from '../../types/orgStructures';
import OrgNode from './OrgNode';
import { DisplayProperties } from './PropertiesPanel';

interface OrgChartRendererProps {
  data: TreeNode | null;
  layoutType: OrgStructureType;
  onNodeClick?: (node: TreeNode) => void;
  onNodeHover?: (node: TreeNode | null) => void;
  displayProperties?: DisplayProperties;
}

const OrgChartRenderer: React.FC<OrgChartRendererProps> = ({
  data,
  layoutType,
  onNodeClick,
  onNodeHover,
  displayProperties
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLDivElement>(null);
  const [scale, setScale] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);

  // Mouse events for panning
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    // Only start dragging if clicking on canvas background (not on nodes)
    const target = e.target as HTMLElement;
    const isNode = target.closest('.org-node') || target.closest('.motion-div');
    
    if (!isNode) {
      setIsDragging(true);
      setDragStart({ 
        x: e.clientX - pan.x, 
        y: e.clientY - pan.y 
      });
      e.preventDefault();
    }
  }, [pan]);

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (isDragging) {
      setPan({ 
        x: e.clientX - dragStart.x, 
        y: e.clientY - dragStart.y 
      });
    }
  }, [isDragging, dragStart]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDragging, handleMouseMove, handleMouseUp]);

  // Render hierarchical tree with proper connections
  const renderHierarchicalNode = (node: TreeNode, level: number = 0, index: number = 0): React.ReactNode => {
    const hasChildren = node.children && node.children.length > 0;
    const isSelected = selectedNodeId === node.id;

    return (
      <div key={node.id} className="org-node-wrapper flex flex-col items-center relative">
        {/* Node */}
        <div className="relative z-10">
          <OrgNode
            node={node}
            onClick={() => {
              setSelectedNodeId(node.id);
              onNodeClick?.(node);
            }}
            onHover={(hovered) => onNodeHover?.(hovered ? node : null)}
            isSelected={isSelected}
            displayProperties={displayProperties}
          />
        </div>

        {/* Children Container */}
        {hasChildren && (
          <div className="org-children-container mt-8 flex items-start relative">
            {/* Vertical line from parent to children */}
            <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-0.5 h-8 bg-gray-300" />
            
            {/* Horizontal line connecting all children */}
            {node.children!.length > 1 && (
              <div 
                className="absolute top-8 left-0 right-0 h-0.5 bg-gray-300"
                style={{
                  left: `${100 / (node.children!.length * 2)}%`,
                  right: `${100 / (node.children!.length * 2)}%`
                }}
              />
            )}
            
            {/* Render each child */}
            {node.children!.map((child, idx) => (
              <div key={child.id} className="org-child-wrapper flex flex-col items-center relative" style={{ minWidth: '220px' }}>
                {/* Vertical line from horizontal line to child */}
                <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 w-0.5 h-8 bg-gray-300" />
                
                {/* Child node */}
                <div className="pt-8">
                  {renderHierarchicalNode(child, level + 1, idx)}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  // Render based on layout type
  const renderLayout = () => {
    if (!data) {
      return (
        <div className="flex items-center justify-center h-full">
          <div className="text-center text-gray-500">
            <p className="text-lg mb-2">No organizational data available</p>
            <p className="text-sm">Please check your connection and try again</p>
          </div>
        </div>
      );
    }

    switch (layoutType) {
      case 'classic-top-down':
      case 'bottom-up':
      case 'vertical-functional':
      case 'horizontal-functional':
      case 'multi-layered':
      case 'span-of-control':
        return (
          <div className="flex justify-center items-start pt-10 pb-20">
            {renderHierarchicalNode(data, 0)}
          </div>
        );
      case 'radial-hub-spoke':
      case 'concentric-circles':
      case 'circular-relationship':
        return <div className="flex items-center justify-center h-full text-center p-20 text-gray-500">Radial Layout - Coming Soon</div>;
      case 'matrix-2x2':
      case 'matrix-3axis':
      case 'cross-functional-matrix':
        return <div className="flex items-center justify-center h-full text-center p-20 text-gray-500">Matrix Layout - Coming Soon</div>;
      case 'network':
      case 'holacracy':
      case 'pod-based':
      case 'agile-squad':
      case 'ecosystem':
        return <div className="flex items-center justify-center h-full text-center p-20 text-gray-500">Network Layout - Coming Soon</div>;
      case 'process-flow':
      case 'value-stream':
      case 'decision-flow':
        return <div className="flex items-center justify-center h-full text-center p-20 text-gray-500">Flow Layout - Coming Soon</div>;
      default:
        return (
          <div className="flex justify-center items-start pt-10 pb-20">
            {renderHierarchicalNode(data, 0)}
          </div>
        );
    }
  };

  return (
    <div 
      ref={containerRef}
      className="w-full h-full relative bg-gradient-to-br from-gray-50 via-green-50 to-emerald-50 overflow-hidden"
    >
      <div
        ref={canvasRef}
        className="org-chart-canvas w-full h-full overflow-auto"
        onMouseDown={handleMouseDown}
        style={{ 
          cursor: isDragging ? 'grabbing' : 'default'
        }}
      >
        <div
          className="org-chart-content"
          style={{
            transform: `translate(${pan.x}px, ${pan.y}px) scale(${scale})`,
            transformOrigin: 'top left',
            minWidth: '100%',
            minHeight: '100%'
          }}
        >
          {renderLayout()}
        </div>
      </div>

      {/* Zoom Controls */}
      <div className="absolute bottom-4 right-4 flex flex-col gap-2 bg-white rounded-lg shadow-lg p-2 border border-gray-200 z-50">
        <button
          onClick={() => setScale(Math.min(2, scale + 0.1))}
          className="w-10 h-10 flex items-center justify-center hover:bg-green-50 transition-colors rounded"
          title="Zoom In"
        >
          <span className="text-xl font-light">+</span>
        </button>
        <div className="w-10 h-8 flex items-center justify-center text-xs text-gray-600 border-t border-b border-gray-200">
          {Math.round(scale * 100)}%
        </div>
        <button
          onClick={() => setScale(Math.max(0.5, scale - 0.1))}
          className="w-10 h-10 flex items-center justify-center hover:bg-green-50 transition-colors rounded"
          title="Zoom Out"
        >
          <span className="text-xl font-light">−</span>
        </button>
        <button
          onClick={() => {
            setScale(1);
            setPan({ x: 0, y: 0 });
          }}
          className="w-10 h-10 flex items-center justify-center hover:bg-green-50 transition-colors rounded"
          title="Reset View"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
          </svg>
        </button>
      </div>
    </div>
  );
};

export default OrgChartRenderer;
