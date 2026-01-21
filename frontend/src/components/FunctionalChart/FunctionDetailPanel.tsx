import React, { useState } from 'react';
import { X, MoreVertical, Briefcase, Plus, Sparkles } from 'lucide-react';

interface Accountability {
  id: string;
  accountability_code?: string;
  objective: string;
  display_order: number;
}

interface Function {
  id: string;
  name: string;
  description?: string;
  accountabilities: Accountability[];
}

interface FunctionDetailPanelProps {
  functionItem: Function | null;
  onClose: () => void;
  onAddAccountability?: (functionId: string) => void;
  onEditAccountability?: (accountability: Accountability) => void;
  onDeleteAccountability?: (accountabilityId: string) => void;
}

const FunctionDetailPanel: React.FC<FunctionDetailPanelProps> = ({
  functionItem,
  onClose,
  onAddAccountability,
  onEditAccountability,
  onDeleteAccountability
}) => {
  const [contextMenu, setContextMenu] = useState<{id: string; x: number; y: number} | null>(null);

  if (!functionItem) return null;

  return (
    <div className="w-80 bg-white border-l border-gray-200 flex flex-col h-full shadow-lg">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h2 className="text-lg font-bold text-black">Function</h2>
        </div>
        <div className="flex items-center gap-2">
          <button className="p-1 hover:bg-gray-100 rounded">
            <MoreVertical size={18} className="text-black" />
          </button>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded">
            <X size={18} className="text-black" />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {/* Function Title */}
        <h3 className="text-xl font-bold text-black mb-4">{functionItem.name}</h3>

        {/* Accountabilities Section */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <span className="text-sm font-bold text-black">Accountabilities</span>
              <span className="text-xs bg-gray-100 text-black px-2 py-0.5 rounded-full font-bold">
                {functionItem.accountabilities?.length || 0}
              </span>
            </div>
            <button
              onClick={() => onAddAccountability?.(functionItem.id)}
              className="p-1.5 hover:bg-gray-100 rounded-lg"
            >
              <Plus size={16} className="text-black" />
            </button>
          </div>

          {/* Accountabilities List */}
          <div className="space-y-2">
            {(functionItem.accountabilities || []).map((accountability) => (
              <div
                key={accountability.id}
                className="flex items-center justify-between p-2 hover:bg-gray-50 rounded-lg group"
              >
                <div className="flex items-center gap-2 flex-1 min-w-0">
                  <Briefcase size={16} className="text-black flex-shrink-0" />
                  <span className="text-sm text-black font-semibold truncate">
                    {accountability.objective}
                  </span>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setContextMenu({
                      id: accountability.id,
                      x: e.clientX,
                      y: e.clientY
                    });
                  }}
                  className="opacity-0 group-hover:opacity-100 p-1 hover:bg-gray-100 rounded transition-opacity"
                >
                  <MoreVertical size={14} className="text-black" />
                </button>

                {/* Context Menu */}
                {contextMenu?.id === accountability.id && (
                  <div
                    className="fixed bg-white border border-gray-200 rounded-lg shadow-xl z-50 min-w-[150px]"
                    style={{ left: contextMenu.x, top: contextMenu.y }}
                    onClick={(e) => e.stopPropagation()}
                  >
                    <button
                      onClick={() => {
                        onEditAccountability?.(accountability);
                        setContextMenu(null);
                      }}
                      className="w-full px-4 py-2 text-left text-sm text-black hover:bg-gray-100 font-semibold"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => {
                        onDeleteAccountability?.(accountability.id);
                        setContextMenu(null);
                      }}
                      className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 font-semibold"
                    >
                      Delete
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* AI Chat Input - Fixed at Bottom */}
      <div className="p-4 border-t border-gray-200 bg-white">
        <div className="relative">
          <input
            type="text"
            placeholder="Ask me anything..."
            className="w-full pl-10 pr-20 py-2.5 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-purple-500 text-sm text-black font-semibold placeholder-gray-500"
          />
          <Sparkles size={18} className="absolute left-3 top-3 text-purple-500" />
          <button className="absolute right-2 top-2 p-1.5 bg-purple-600 text-white rounded hover:bg-purple-700">
            <span className="text-xs">→</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default FunctionDetailPanel;
