import React, { useState, useRef, useEffect } from 'react';
import { ArrowRight, X, Plus, Check, AlertCircle } from 'lucide-react';

interface Field {
  name: string;
  type: string;
  description?: string;
  required?: boolean;
  isParentChild?: boolean;
}

interface Mapping {
  source_field: string;
  target_field: string;
  transform_function?: string;
}

interface VisualMappingViewProps {
  sourceFields: Field[];
  targetFields: Field[];
  existingMappings: Mapping[];
  onMappingChange: (sourceField: string, targetField: string, transformFunction?: string) => void;
  onRemoveMapping: (sourceField: string) => void;
}

const VisualMappingView: React.FC<VisualMappingViewProps> = ({
  sourceFields,
  targetFields,
  existingMappings,
  onMappingChange,
  onRemoveMapping
}) => {
  const [selectedSource, setSelectedSource] = useState<string | null>(null);
  const [hoveredTarget, setHoveredTarget] = useState<string | null>(null);
  const [dragging, setDragging] = useState<string | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const getMappingForSource = (sourceField: string): Mapping | undefined => {
    const mapping = existingMappings.find(m => m.source_field === sourceField);
    // If mapping uses constant transformation, don't show it as mapped (constant ignores source)
    if (mapping && mapping.transform_function?.startsWith('constant(')) {
      return undefined;
    }
    return mapping;
  };

  const getMappingForTarget = (targetField: string): Mapping | undefined => {
    const mapping = existingMappings.find(m => m.target_field === targetField);
    // If mapping uses constant transformation, still return it but mark it differently
    return mapping;
  };
  
  const isConstantMapping = (mapping: Mapping | undefined): boolean => {
    return mapping?.transform_function?.startsWith('constant(') || false;
  };

  const handleSourceClick = (sourceField: string) => {
    if (selectedSource === sourceField) {
      setSelectedSource(null);
    } else {
      setSelectedSource(sourceField);
    }
  };

  const handleTargetClick = (targetField: string) => {
    if (selectedSource) {
      onMappingChange(selectedSource, targetField);
      setSelectedSource(null);
    }
  };

  const handleTargetHover = (targetField: string) => {
    if (selectedSource) {
      setHoveredTarget(targetField);
    }
  };

  const getConnectionPath = (sourceIndex: number, targetIndex: number): string => {
    const sourceX = 200; // Left panel width
    const sourceY = 60 + sourceIndex * 50; // Header + item height
    const targetX = 600; // Right panel start
    const targetY = 60 + targetIndex * 50;
    
    const midX = (sourceX + targetX) / 2;
    return `M ${sourceX} ${sourceY} C ${midX} ${sourceY}, ${midX} ${targetY}, ${targetX} ${targetY}`;
  };

  return (
    <div className="relative w-full h-full min-h-[600px] bg-gray-50 border border-gray-200 rounded-lg overflow-hidden">
      {/* SVG for connections */}
      <svg className="absolute inset-0 pointer-events-none z-10" style={{ width: '100%', height: '100%' }}>
        {existingMappings.map((mapping, index) => {
          const sourceIndex = sourceFields.findIndex(f => f.name === mapping.source_field);
          const targetIndex = targetFields.findIndex(f => {
            const fieldName = typeof f === 'object' ? f.name : f;
            return fieldName === mapping.target_field;
          });
          
          if (sourceIndex === -1 || targetIndex === -1) return null;
          
          const path = getConnectionPath(sourceIndex, targetIndex);
          return (
            <path
              key={`${mapping.source_field}-${mapping.target_field}`}
              d={path}
              stroke="#10b981"
              strokeWidth="2"
              fill="none"
              markerEnd="url(#arrowhead)"
              className="transition-opacity"
            />
          );
        })}
        <defs>
          <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
            <polygon points="0 0, 10 3, 0 6" fill="#10b981" />
          </marker>
        </defs>
      </svg>

      <div ref={containerRef} className="relative z-20 flex h-full">
        {/* Left Panel - Source Fields */}
        <div className="w-1/2 border-r border-gray-300 bg-white">
          <div className="bg-green-600 text-white p-3 font-semibold text-sm">
            SuccessFactors Fields (Source)
          </div>
          <div className="overflow-y-auto h-[calc(100%-48px)]">
            {sourceFields.map((field, index) => {
              const mapping = getMappingForSource(field.name);
              const isSelected = selectedSource === field.name;
              
              return (
                <div
                  key={field.name}
                  onClick={() => handleSourceClick(field.name)}
                  onMouseEnter={() => setDragging(field.name)}
                  onMouseLeave={() => setDragging(null)}
                  className={`p-3 border-b border-gray-200 cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-green-100 border-green-500 border-l-4'
                      : mapping
                      ? 'bg-green-50 border-l-2 border-green-400'
                      : 'hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-sm font-semibold text-gray-900">{field.name}</span>
                        <span className="text-xs bg-gray-200 px-1.5 py-0.5 rounded text-gray-700">
                          {field.type || 'String'}
                        </span>
                        {mapping && (
                          <Check size={14} className="text-green-600" />
                        )}
                      </div>
                      {field.description && (
                        <p className="text-xs text-gray-500 mt-1">{field.description}</p>
                      )}
                      {mapping && (
                        <div className="mt-1 flex items-center gap-1">
                          <ArrowRight size={12} className="text-green-600" />
                          <span className="text-xs text-green-700 font-medium">
                            → {mapping.target_field}
                          </span>
                          {mapping.transform_function && (
                            <span className="text-xs text-blue-600 ml-2">
                              ({mapping.transform_function})
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                    {mapping && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onRemoveMapping(field.name);
                        }}
                        className="ml-2 p-1 text-red-600 hover:bg-red-50 rounded"
                        title="Remove mapping"
                      >
                        <X size={14} />
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Panel - Target Fields */}
        <div className="w-1/2 bg-white">
          <div className="bg-blue-600 text-white p-3 font-semibold text-sm">
            OrgChartAI Fields (Target)
          </div>
          <div className="overflow-y-auto h-[calc(100%-48px)]">
            {targetFields.map((field, index) => {
              const fieldName = typeof field === 'object' ? field.name : field;
              const fieldInfo = typeof field === 'object' ? field : null;
              const mapping = getMappingForTarget(fieldName);
              const isHovered = hoveredTarget === fieldName;
              const isRequired = fieldInfo?.required || false;
              const isConstant = isConstantMapping(mapping);
              
              return (
                <div
                  key={fieldName}
                  onClick={() => handleTargetClick(fieldName)}
                  onMouseEnter={() => handleTargetHover(fieldName)}
                  onMouseLeave={() => setHoveredTarget(null)}
                  className={`p-3 border-b border-gray-200 cursor-pointer transition-all ${
                    selectedSource && isHovered
                      ? 'bg-green-100 border-green-500 border-l-4'
                      : mapping && !isConstant
                      ? 'bg-green-50 border-l-2 border-green-400'
                      : isConstant
                      ? 'bg-blue-50 border-l-2 border-blue-400'
                      : isRequired
                      ? 'bg-yellow-50 border-l-2 border-yellow-400'
                      : 'hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-sm font-semibold text-gray-900">{fieldName}</span>
                        {isRequired && (
                          <span className="text-xs bg-green-100 text-green-700 px-1.5 py-0.5 rounded font-semibold">
                            * Required
                          </span>
                        )}
                        {mapping && !isConstant && (
                          <Check size={14} className="text-green-600" />
                        )}
                        {isConstant && (
                          <span className="text-xs bg-blue-200 text-blue-800 px-1.5 py-0.5 rounded font-bold">
                            Constant
                          </span>
                        )}
                      </div>
                      {fieldInfo?.description && (
                        <p className="text-xs text-gray-500 mt-1">{fieldInfo.description}</p>
                      )}
                      {mapping && !isConstant && (
                        <div className="mt-1 flex items-center gap-1">
                          <ArrowRight size={12} className="text-green-600 rotate-180" />
                          <span className="text-xs text-green-700 font-medium">
                            ← {mapping.source_field}
                          </span>
                          {mapping.transform_function && !mapping.transform_function.startsWith('constant(') && (
                            <span className="text-xs text-blue-600 ml-2">
                              ({mapping.transform_function})
                            </span>
                          )}
                        </div>
                      )}
                      {isConstant && mapping && (
                        <div className="mt-1 flex items-center gap-1">
                          <span className="text-xs text-blue-700 font-bold bg-blue-100 px-2 py-1 rounded">
                            ✓ Constant Value: {mapping.transform_function?.replace('constant(', '').replace(')', '').replace(/'/g, '') || 'N/A'}
                          </span>
                          <span className="text-xs text-gray-600 ml-2">
                            (Source field ignored)
                          </span>
                        </div>
                      )}
                      {selectedSource && !mapping && (
                        <div className="mt-1 text-xs text-green-600 font-medium">
                          Click to map from: {selectedSource}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Instructions */}
      {selectedSource && (
        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-green-600 text-white px-4 py-2 rounded-lg shadow-lg z-30">
          <p className="text-sm font-medium">
            Selected: <span className="font-mono">{selectedSource}</span> → Click a target field to map
          </p>
        </div>
      )}
    </div>
  );
};

export default VisualMappingView;
