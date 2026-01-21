import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { X, Move, ChevronDown } from 'lucide-react';

interface MoveModalProps {
  isOpen: boolean;
  onClose: () => void;
  onMove: (targetId: string) => void;
  itemType: 'accountability' | 'function';
  itemName: string;
  categories: Array<{
    id: string;
    name: string;
    functions?: Array<{
      id: string;
      name: string;
    }>;
  }>;
  currentCategoryId?: string;
  currentFunctionId?: string;
}

const MoveModal: React.FC<MoveModalProps> = ({
  isOpen,
  onClose,
  onMove,
  itemType,
  itemName,
  categories,
  currentCategoryId,
  currentFunctionId
}) => {
  const [selectedCategoryId, setSelectedCategoryId] = useState<string>('');
  const [selectedFunctionId, setSelectedFunctionId] = useState<string>('');
  const [expandedCategory, setExpandedCategory] = useState<string>('');

  if (!isOpen) return null;

  const handleMove = () => {
    if (itemType === 'accountability') {
      if (selectedFunctionId) {
        onMove(selectedFunctionId);
      }
    } else {
      if (selectedCategoryId) {
        onMove(selectedCategoryId);
      }
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        onClick={(e) => e.stopPropagation()}
        className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
      >
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Move size={20} className="text-green-600" />
              <div>
                <h3 className="text-xl font-bold text-gray-900">Move {itemType === 'accountability' ? 'Accountability' : 'Function'}</h3>
                <p className="text-sm text-gray-600 mt-1">{itemName}</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X size={20} className="text-gray-500" />
            </button>
          </div>
        </div>

        <div className="p-6 space-y-4">
          {itemType === 'accountability' ? (
            <>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Move to Function
              </label>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {categories.map((category) => (
                  <div key={category.id} className="border border-gray-200 rounded-lg">
                    <button
                      onClick={() => setExpandedCategory(expandedCategory === category.id ? '' : category.id)}
                      className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
                    >
                      <span className="font-medium text-gray-900">{category.name}</span>
                      <ChevronDown
                        size={18}
                        className={`text-gray-500 transition-transform ${
                          expandedCategory === category.id ? 'rotate-180' : ''
                        }`}
                      />
                    </button>
                    {expandedCategory === category.id && category.functions && (
                      <div className="border-t border-gray-200 bg-gray-50">
                        {category.functions
                          .filter(func => func.id !== currentFunctionId)
                          .map((func) => (
                            <button
                              key={func.id}
                              onClick={() => setSelectedFunctionId(func.id)}
                              className={`w-full px-6 py-3 text-left hover:bg-green-50 transition-colors ${
                                selectedFunctionId === func.id ? 'bg-green-100 border-l-4 border-green-500' : ''
                              }`}
                            >
                              <span className="text-sm text-gray-700">{func.name}</span>
                            </button>
                          ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </>
          ) : (
            <>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Move to Category
              </label>
              <div className="space-y-2">
                {categories
                  .filter(cat => cat.id !== currentCategoryId)
                  .map((category) => (
                    <button
                      key={category.id}
                      onClick={() => setSelectedCategoryId(category.id)}
                      className={`w-full px-4 py-3 text-left border border-gray-200 rounded-lg hover:bg-green-50 transition-colors ${
                        selectedCategoryId === category.id ? 'bg-green-100 border-green-500' : ''
                      }`}
                    >
                      <span className="font-medium text-gray-900">{category.name}</span>
                    </button>
                  ))}
              </div>
            </>
          )}
        </div>

        <div className="p-6 border-t border-gray-200 flex items-center justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
          >
            Cancel
          </button>
          <button
            onClick={handleMove}
            disabled={
              (itemType === 'accountability' && !selectedFunctionId) ||
              (itemType === 'function' && !selectedCategoryId)
            }
            className="px-4 py-2 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Move
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default MoveModal;
