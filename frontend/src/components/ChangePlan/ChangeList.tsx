import React, { useState } from 'react';
import { ChevronDown, ChevronRight, Plus, Minus, Edit, Move } from 'lucide-react';

interface ChangeItem {
  change_type: 'added' | 'removed' | 'updated' | 'moved';
  entity_type: 'position' | 'org_unit' | 'employee';
  entity_id: string;
  entity_name: string;
  old_value?: any;
  new_value?: any;
  changes?: Record<string, { old: any; new: any }>;
}

interface ChangeListProps {
  changes: ChangeItem[];
  filterType?: 'added' | 'removed' | 'updated' | 'moved' | 'all';
  filterEntity?: 'position' | 'org_unit' | 'employee' | 'all';
}

const ChangeList: React.FC<ChangeListProps> = ({
  changes,
  filterType = 'all',
  filterEntity = 'all'
}) => {
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());

  const toggleExpand = (itemId: string) => {
    setExpandedItems(prev => {
      const next = new Set(prev);
      if (next.has(itemId)) {
        next.delete(itemId);
      } else {
        next.add(itemId);
      }
      return next;
    });
  };

  const getChangeIcon = (type: string) => {
    switch (type) {
      case 'added':
        return <Plus size={16} className="text-green-600" />;
      case 'removed':
        return <Minus size={16} className="text-red-600" />;
      case 'updated':
        return <Edit size={16} className="text-yellow-600" />;
      case 'moved':
        return <Move size={16} className="text-blue-600" />;
      default:
        return null;
    }
  };

  const getChangeColor = (type: string) => {
    switch (type) {
      case 'added':
        return 'bg-green-50 border-green-200 text-green-800';
      case 'removed':
        return 'bg-red-50 border-red-200 text-red-800';
      case 'updated':
        return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      case 'moved':
        return 'bg-blue-50 border-blue-200 text-blue-800';
      default:
        return 'bg-gray-50 border-gray-200 text-gray-800';
    }
  };

  const filteredChanges = changes.filter(change => {
    if (filterType !== 'all' && change.change_type !== filterType) return false;
    if (filterEntity !== 'all' && change.entity_type !== filterEntity) return false;
    return true;
  });

  return (
    <div className="divide-y divide-gray-200">
      {filteredChanges.length === 0 ? (
        <div className="px-6 py-8 text-center text-gray-500">
          No changes found
        </div>
      ) : (
        filteredChanges.map((change, index) => {
          const isExpanded = expandedItems.has(change.entity_id);
          const hasDetails = change.changes && Object.keys(change.changes).length > 0;

          return (
            <div
              key={`${change.entity_id}-${index}`}
              className={`px-6 py-4 hover:bg-gray-50 transition-colors ${getChangeColor(change.change_type)}`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 flex-1">
                  {hasDetails ? (
                    <button
                      onClick={() => toggleExpand(change.entity_id)}
                      className="p-1 hover:bg-white rounded transition-colors"
                    >
                      {isExpanded ? (
                        <ChevronDown size={16} className="text-gray-600" />
                      ) : (
                        <ChevronRight size={16} className="text-gray-600" />
                      )}
                    </button>
                  ) : (
                    <div className="w-6" />
                  )}
                  
                  {getChangeIcon(change.change_type)}
                  
                  <div className="flex-1">
                    <div className="font-medium">{change.entity_name}</div>
                    <div className="text-xs opacity-75 mt-0.5">
                      {change.entity_type} • {change.change_type}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-xs px-2 py-1 bg-white rounded border border-current opacity-50">
                    {change.entity_type}
                  </span>
                </div>
              </div>

              {/* Expanded Details */}
              {isExpanded && hasDetails && (
                <div className="mt-4 ml-9 space-y-2">
                  {Object.entries(change.changes!).map(([field, values]) => (
                    <div key={field} className="bg-white rounded p-3 border border-gray-200">
                      <div className="text-xs font-medium text-gray-600 mb-1">{field}</div>
                      <div className="flex items-center gap-2 text-sm">
                        <span className="text-red-600 line-through">{String(values.old ?? 'N/A')}</span>
                        <span className="text-gray-400">→</span>
                        <span className="text-green-600 font-medium">{String(values.new ?? 'N/A')}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Moved Details */}
              {change.change_type === 'moved' && isExpanded && (
                <div className="mt-4 ml-9 space-y-2">
                  {change.old_value && (
                    <div className="bg-white rounded p-3 border border-gray-200">
                      <div className="text-xs font-medium text-gray-600 mb-1">Previous</div>
                      <div className="text-sm text-gray-700">
                        Reports to: {change.old_value.reports_to ? 'Position' : 'None'}<br />
                        Org Unit: {change.old_value.org_unit ? 'Org Unit' : 'None'}
                      </div>
                    </div>
                  )}
                  {change.new_value && (
                    <div className="bg-white rounded p-3 border border-gray-200">
                      <div className="text-xs font-medium text-gray-600 mb-1">New</div>
                      <div className="text-sm text-gray-700">
                        Reports to: {change.new_value.reports_to ? 'Position' : 'None'}<br />
                        Org Unit: {change.new_value.org_unit ? 'Org Unit' : 'None'}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })
      )}
    </div>
  );
};

export default ChangeList;
