import React from 'react';
import { ArrowRight } from 'lucide-react';

interface Scenario {
  id: string;
  name: string;
}

interface ChangeItem {
  change_type: 'added' | 'removed' | 'updated' | 'moved';
  entity_type: 'position' | 'org_unit' | 'employee';
  entity_id: string;
  entity_name: string;
}

interface ChangeVisualDiffProps {
  sourceScenario: Scenario;
  targetScenario: Scenario;
  changes: ChangeItem[];
}

const ChangeVisualDiff: React.FC<ChangeVisualDiffProps> = ({
  sourceScenario,
  targetScenario,
  changes
}) => {
  // Simple visual representation
  // In a real implementation, this would render actual org chart diagrams
  
  const getNodeColor = (entityId: string) => {
    const change = changes.find(c => c.entity_id === entityId);
    if (!change) return 'bg-gray-200';
    
    switch (change.change_type) {
      case 'added':
        return 'bg-green-200 border-green-400';
      case 'removed':
        return 'bg-red-200 border-red-400';
      case 'updated':
        return 'bg-yellow-200 border-yellow-400';
      case 'moved':
        return 'bg-blue-200 border-blue-400';
      default:
        return 'bg-gray-200';
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Visual Comparison</h3>
      
      <div className="flex items-center justify-center gap-8">
        {/* Source Scenario */}
        <div className="flex-1">
          <div className="text-sm font-medium text-gray-600 mb-3 text-center">
            {sourceScenario.name}
          </div>
          <div className="space-y-2">
            {/* Simplified org chart representation */}
            <div className="flex flex-col items-center">
              <div className="w-24 h-16 bg-gray-200 border-2 border-gray-400 rounded-lg flex items-center justify-center text-xs font-medium text-gray-700 mb-2">
                Manager
              </div>
              <div className="flex gap-2">
                <div className="w-20 h-14 bg-gray-200 border-2 border-gray-400 rounded-lg flex items-center justify-center text-xs text-gray-700">
                  Team A
                </div>
                <div className="w-20 h-14 bg-purple-200 border-2 border-purple-400 rounded-lg flex items-center justify-center text-xs text-gray-700">
                  Team B
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Arrow */}
        <ArrowRight size={32} className="text-gray-400" />

        {/* Target Scenario */}
        <div className="flex-1">
          <div className="text-sm font-medium text-gray-600 mb-3 text-center">
            {targetScenario.name}
          </div>
          <div className="space-y-2">
            <div className="flex flex-col items-center">
              <div className="w-24 h-16 bg-gray-200 border-2 border-gray-400 rounded-lg flex items-center justify-center text-xs font-medium text-gray-700 mb-2">
                Manager
              </div>
              <div className="flex gap-2">
                <div className="w-20 h-14 bg-gray-200 border-2 border-gray-400 rounded-lg flex items-center justify-center text-xs text-gray-700">
                  Team A
                </div>
                <div className="w-20 h-14 bg-orange-200 border-2 border-orange-400 rounded-lg flex items-center justify-center text-xs text-gray-700">
                  Team B
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-center gap-6 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-green-200 border border-green-400 rounded"></div>
            <span className="text-gray-600">Added</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-red-200 border border-red-400 rounded"></div>
            <span className="text-gray-600">Removed</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-yellow-200 border border-yellow-400 rounded"></div>
            <span className="text-gray-600">Updated</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-blue-200 border border-blue-400 rounded"></div>
            <span className="text-gray-600">Moved</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChangeVisualDiff;
