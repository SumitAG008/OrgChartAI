import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ChevronDown, ChevronRight, Plus, MoreVertical, 
  Edit, UserPlus, Move, Settings, Trash2, Archive,
  FileText, Sparkles, X, Briefcase, Grid3x3, List, Search
} from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import MoveModal from './MoveModal';
import FunctionDetailPanel from './FunctionDetailPanel';

interface FunctionCategory {
  id: string;
  name: string;
  description?: string;
  icon?: string;
  display_order: number;
  functions: Function[];
}

interface Function {
  id: string;
  name: string;
  description?: string;
  icon?: string;
  display_order: number;
  accountabilities: Accountability[];
}

interface Accountability {
  id: string;
  accountability_code?: string;
  objective: string;
  display_order: number;
  assignment_count?: number;
}

const FunctionalChartView: React.FC = () => {
  const [expandedCategories, setExpandedCategories] = useState<string[]>([]);
  const [showAddAccountabilityModal, setShowAddAccountabilityModal] = useState(false);
  const [showEditAccountabilityModal, setShowEditAccountabilityModal] = useState(false);
  const [showMoveModal, setShowMoveModal] = useState(false);
  const [selectedFunction, setSelectedFunction] = useState<Function | null>(null);
  const [selectedAccountability, setSelectedAccountability] = useState<Accountability | null>(null);
  const [contextMenu, setContextMenu] = useState<{id: string; x: number; y: number} | null>(null);
  const [categoryContextMenu, setCategoryContextMenu] = useState<{id: string; x: number; y: number} | null>(null);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [showFunctionPanel, setShowFunctionPanel] = useState(false);
  const [newAccountability, setNewAccountability] = useState({
    objective: '',
    accountability_code: ''
  });

  const queryClient = useQueryClient();

  // Fetch functional chart data
  const { data: chartData, isLoading } = useQuery({
    queryKey: ['functionalChart'],
    queryFn: async () => {
      const response = await fetch('http://localhost:8000/api/v1/functional-chart/chart');
      if (!response.ok) throw new Error('Failed to fetch functional chart');
      return response.json();
    }
  });

  // Create accountability mutation
  const createAccountabilityMutation = useMutation({
    mutationFn: async (data: { function_id: string; objective: string; accountability_code?: string }) => {
      const response = await fetch('http://localhost:8000/api/v1/functional-chart/accountabilities', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...data,
          created_by: '00000000-0000-0000-0000-000000000000' // TODO: Get from auth
        })
      });
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to create accountability' }));
        throw new Error(errorData.detail || 'Failed to create accountability');
      }
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['functionalChart'] });
      setShowAddAccountabilityModal(false);
      setNewAccountability({ objective: '', accountability_code: '' });
    },
    onError: (error: Error) => {
      alert(`Error: ${error.message}\n\nPlease run the database schema: database/functional_chart_schema.sql`);
    }
  });

  // Update accountability mutation
  const updateAccountabilityMutation = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: any }) => {
      const response = await fetch(`http://localhost:8000/api/v1/functional-chart/accountabilities/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...data,
          updated_by: '00000000-0000-0000-0000-000000000000' // TODO: Get from auth
        })
      });
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to update accountability' }));
        throw new Error(errorData.detail || 'Failed to update accountability');
      }
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['functionalChart'] });
      setShowEditAccountabilityModal(false);
      setSelectedAccountability(null);
    },
    onError: (error: Error) => {
      alert(`Error: ${error.message}\n\nPlease run the database schema: database/functional_chart_schema.sql`);
    }
  });

  // Delete accountability mutation
  const deleteAccountabilityMutation = useMutation({
    mutationFn: async (id: string) => {
      const response = await fetch(`http://localhost:8000/api/v1/functional-chart/accountabilities/${id}`, {
        method: 'DELETE'
      });
      if (!response.ok) throw new Error('Failed to delete accountability');
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['functionalChart'] });
      setContextMenu(null);
    }
  });

  // Move accountability mutation
  const moveAccountabilityMutation = useMutation({
    mutationFn: async ({ id, newFunctionId }: { id: string; newFunctionId: string }) => {
      const response = await fetch(`http://localhost:8000/api/v1/functional-chart/accountabilities/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          function_id: newFunctionId,
          updated_by: '00000000-0000-0000-0000-000000000000' // TODO: Get from auth
        })
      });
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to move accountability' }));
        throw new Error(errorData.detail || 'Failed to move accountability');
      }
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['functionalChart'] });
      setShowMoveModal(false);
      setSelectedAccountability(null);
      setSelectedFunction(null);
    },
    onError: (error: Error) => {
      alert(`Error: ${error.message}\n\nPlease run the database schema: database/functional_chart_schema.sql`);
    }
  });

  // Move function mutation
  const moveFunctionMutation = useMutation({
    mutationFn: async ({ id, newCategoryId }: { id: string; newCategoryId: string }) => {
      const response = await fetch(`http://localhost:8000/api/v1/functional-chart/functions/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          category_id: newCategoryId,
          updated_by: '00000000-0000-0000-0000-000000000000' // TODO: Get from auth
        })
      });
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to move function' }));
        throw new Error(errorData.detail || 'Failed to move function');
      }
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['functionalChart'] });
      setShowMoveModal(false);
      setSelectedFunction(null);
    },
    onError: (error: Error) => {
      alert(`Error: ${error.message}\n\nPlease run the database schema: database/functional_chart_schema.sql`);
    }
  });

  const toggleCategory = (categoryName: string) => {
    setExpandedCategories(prev => 
      prev.includes(categoryName)
        ? prev.filter(name => name !== categoryName)
        : [...prev, categoryName]
    );
  };

  const handleAddAccountability = () => {
    if (!selectedFunction || !newAccountability.objective.trim()) {
      alert('Please enter an objective');
      return;
    }

    createAccountabilityMutation.mutate({
      function_id: selectedFunction.id,
      objective: newAccountability.objective,
      accountability_code: newAccountability.accountability_code || undefined
    });
  };

  const handleEditAccountability = () => {
    if (!selectedAccountability || !newAccountability.objective.trim()) {
      return;
    }

    updateAccountabilityMutation.mutate({
      id: selectedAccountability.id,
      data: {
        objective: newAccountability.objective,
        accountability_code: newAccountability.accountability_code || undefined
      }
    });
  };

  const handleDeleteAccountability = (accountabilityId: string) => {
    if (confirm('Are you sure you want to delete this accountability?')) {
      deleteAccountabilityMutation.mutate(accountabilityId);
    }
  };

  const handleMoveAccountability = (targetFunctionId: string) => {
    if (!selectedAccountability) return;
    moveAccountabilityMutation.mutate({
      id: selectedAccountability.id,
      newFunctionId: targetFunctionId
    });
  };

  const handleMoveFunction = (targetCategoryId: string) => {
    if (!selectedFunction) return;
    moveFunctionMutation.mutate({
      id: selectedFunction.id,
      newCategoryId: targetCategoryId
    });
  };

  const handleEditAccountabilityClick = (accountability: Accountability, functionItem: Function) => {
    setSelectedAccountability(accountability);
    setSelectedFunction(functionItem);
    setNewAccountability({
      objective: accountability.objective,
      accountability_code: accountability.accountability_code || ''
    });
    setShowEditAccountabilityModal(true);
    setContextMenu(null);
  };

  const handleMoveAccountabilityClick = (accountability: Accountability, functionItem: Function) => {
    setSelectedAccountability(accountability);
    setSelectedFunction(functionItem);
    setShowMoveModal(true);
    setContextMenu(null);
  };

  // Close context menus when clicking outside
  useEffect(() => {
    const handleClickOutside = () => {
      setContextMenu(null);
      setCategoryContextMenu(null);
    };
    if (contextMenu || categoryContextMenu) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [contextMenu, categoryContextMenu]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-green-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading functional chart...</p>
        </div>
      </div>
    );
  }

  const categories: FunctionCategory[] = chartData?.categories || [];

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Toolbar */}
      <div className="bg-white border-b border-gray-200 px-6 py-3">
        <div className="flex items-center gap-4">
          {/* View Selector */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded-lg ${
                viewMode === 'grid' 
                  ? 'bg-blue-100 text-blue-700' 
                  : 'text-black hover:bg-gray-100'
              }`}
            >
              <Grid3x3 size={18} />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded-lg ${
                viewMode === 'list' 
                  ? 'bg-blue-100 text-blue-700' 
                  : 'text-black hover:bg-gray-100'
              }`}
            >
              <List size={18} />
            </button>
          </div>

          <button className="flex items-center gap-2 px-3 py-2 text-sm text-black bg-white border border-gray-300 rounded-lg hover:bg-gray-50 font-semibold">
            <Settings size={16} className="text-black" />
            Properties
          </button>
          <button className="flex items-center gap-2 px-3 py-2 text-sm text-black bg-white border border-gray-300 rounded-lg hover:bg-gray-50 font-semibold">
            Filter
          </button>

          {/* Search */}
          <div className="relative flex-1 max-w-xs">
            <Search size={16} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search functions..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-black font-semibold"
            />
          </div>

          {/* Add New Button */}
          <button className="flex items-center gap-2 px-4 py-2 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700 font-semibold">
            <Plus size={16} />
            Add new
            <ChevronDown size={14} />
          </button>
        </div>
      </div>

      {/* Functions Container */}
      <div className="flex-1 overflow-y-auto p-6 flex relative">
        <div className={`flex-1 transition-all duration-300 ${showFunctionPanel ? 'mr-80' : ''}`}>
          {categories.map((category) => {
            // Filter functions based on search query
            const filteredFunctions = (category.functions || []).filter(func =>
              func.name.toLowerCase().includes(searchQuery.toLowerCase())
            );

            if (searchQuery && filteredFunctions.length === 0) return null;

            return (
              <div key={category.id} className="mb-6">
                {/* Category Header */}
                <div className="flex items-center justify-between px-4 py-3 bg-gray-50 rounded-lg mb-3 group">
                  <div
                    className="flex items-center gap-2 flex-1 cursor-pointer"
                    onClick={() => toggleCategory(category.name)}
                  >
                    {expandedCategories.includes(category.name) ? (
                      <ChevronDown size={18} className="text-black" />
                    ) : (
                      <ChevronRight size={18} className="text-black" />
                    )}
                    <span className="font-bold text-black">{category.name}</span>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setCategoryContextMenu({
                        id: category.id,
                        x: e.clientX,
                        y: e.clientY
                      });
                    }}
                    className="opacity-0 group-hover:opacity-100 p-1 hover:bg-gray-100 rounded transition-opacity"
                  >
                    <MoreVertical size={18} className="text-black" />
                  </button>

                  {/* Category Context Menu */}
                  {categoryContextMenu?.id === category.id && (
                    <div
                      className="fixed bg-white border border-gray-200 rounded-lg shadow-xl z-50 min-w-[150px]"
                      style={{ left: categoryContextMenu.x, top: categoryContextMenu.y }}
                      onClick={(e) => e.stopPropagation()}
                    >
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setCategoryContextMenu(null);
                        }}
                        className="w-full px-4 py-2 text-left text-sm text-black hover:bg-gray-100 font-semibold"
                      >
                        Edit
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setCategoryContextMenu(null);
                        }}
                        className="w-full px-4 py-2 text-left text-sm text-black hover:bg-gray-100 font-semibold"
                      >
                        Disable
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setCategoryContextMenu(null);
                        }}
                        className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 font-semibold"
                      >
                        Delete
                      </button>
                    </div>
                  )}
                </div>

                {/* Functions Grid/List */}
                {expandedCategories.includes(category.name) && (
                  <>
                    {viewMode === 'grid' ? (
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
                        {filteredFunctions.map((func) => (
                          <div
                            key={func.id}
                            onClick={() => {
                              setSelectedFunction(func);
                              setShowFunctionPanel(true);
                            }}
                            className="bg-white border border-gray-200 rounded-xl p-4 hover:border-green-300 hover:shadow-md transition-all relative group cursor-pointer"
                          >
                            <div className="flex items-start justify-between mb-2">
                              <div className="flex items-start gap-3 flex-1">
                                <span className="text-2xl">{func.icon || '📋'}</span>
                                <span className="text-sm font-bold text-black leading-tight">{func.name}</span>
                              </div>
                              <button
                                className="opacity-0 group-hover:opacity-100 p-1 hover:bg-gray-100 rounded transition-opacity"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setContextMenu({
                                    id: func.id,
                                    x: e.clientX,
                                    y: e.clientY
                                  });
                                }}
                              >
                                <MoreVertical size={14} className="text-black" />
                              </button>
                            </div>

                            {/* Yellow Dot Indicator */}
                            <div className="absolute bottom-2 right-2 w-2 h-2 bg-yellow-400 rounded-full" />

                            {/* Accountabilities Count */}
                            <div className="text-xs text-black mt-2 font-semibold">
                              {func.accountabilities?.length || 0} accountability{func.accountabilities?.length !== 1 ? 'ies' : ''}
                            </div>

                            {/* Context Menu for Function */}
                            {contextMenu?.id === func.id && (
                              <div
                                className="fixed bg-white border border-gray-200 rounded-lg shadow-xl z-50 min-w-[180px]"
                                style={{ left: contextMenu.x, top: contextMenu.y }}
                                onClick={(e) => e.stopPropagation()}
                              >
                                <div className="px-3 py-2 text-xs font-bold text-black uppercase border-b border-gray-100">
                                  Function
                                </div>
                                <button
                                  className="w-full px-4 py-2 text-sm text-left hover:bg-gray-50 flex items-center gap-2 text-black font-semibold"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setSelectedFunction(func);
                                    setShowAddAccountabilityModal(true);
                                    setContextMenu(null);
                                  }}
                                >
                                  <Plus size={14} className="text-black" />
                                  Add Accountability
                                </button>
                                <button
                                  className="w-full px-4 py-2 text-sm text-left hover:bg-gray-50 flex items-center gap-2 text-black font-semibold"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setContextMenu(null);
                                  }}
                                >
                                  <Edit size={14} className="text-black" />
                                  Edit Function
                                </button>
                                <button
                                  className="w-full px-4 py-2 text-sm text-left hover:bg-gray-50 flex items-center gap-2 text-black font-semibold"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setSelectedFunction(func);
                                    setShowMoveModal(true);
                                    setContextMenu(null);
                                  }}
                                >
                                  <Move size={14} className="text-black" />
                                  Move Function
                                </button>
                                <button
                                  className="w-full px-4 py-2 text-sm text-left hover:bg-red-50 flex items-center gap-2 text-red-600 font-semibold"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setContextMenu(null);
                                  }}
                                >
                                  <Trash2 size={14} className="text-red-600" />
                                  Delete Function
                                </button>
                              </div>
                            )}

                            {/* Context Menu for Accountability */}
                            {contextMenu?.id?.startsWith('acc-') && selectedAccountability && (
                              <div
                                className="fixed bg-white border border-gray-200 rounded-lg shadow-xl z-50 min-w-[180px]"
                                style={{ left: contextMenu.x, top: contextMenu.y }}
                                onClick={(e) => e.stopPropagation()}
                              >
                                <div className="px-3 py-2 text-xs font-bold text-black uppercase border-b border-gray-100">
                                  Accountability
                                </div>
                                <button
                                  className="w-full px-4 py-2 text-sm text-left hover:bg-gray-50 flex items-center gap-2 text-black font-semibold"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleEditAccountabilityClick(selectedAccountability, func);
                                    setContextMenu(null);
                                  }}
                                >
                                  <Edit size={14} className="text-black" />
                                  Edit
                                </button>
                                <button
                                  className="w-full px-4 py-2 text-sm text-left hover:bg-gray-50 flex items-center gap-2 text-black font-semibold"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleMoveAccountabilityClick(selectedAccountability, func);
                                    setContextMenu(null);
                                  }}
                                >
                                  <Move size={14} className="text-black" />
                                  Move
                                </button>
                                <button
                                  className="w-full px-4 py-2 text-sm text-left hover:bg-red-50 flex items-center gap-2 text-red-600 font-semibold"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleDeleteAccountability(selectedAccountability.id);
                                    setContextMenu(null);
                                  }}
                                >
                                  <Trash2 size={14} className="text-red-600" />
                                  Delete
                                </button>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="space-y-2">
                        {filteredFunctions.map((func) => (
                          <div
                            key={func.id}
                            onClick={() => {
                              setSelectedFunction(func);
                              setShowFunctionPanel(true);
                            }}
                            className="bg-white border border-gray-200 rounded-lg p-3 hover:border-green-300 hover:shadow-md transition-all relative group cursor-pointer flex items-center justify-between"
                          >
                            <div className="flex items-center gap-3 flex-1">
                              <span className="text-xl">{func.icon || '📋'}</span>
                              <span className="text-sm font-bold text-black">{func.name}</span>
                              <div className="w-2 h-2 bg-yellow-400 rounded-full" />
                            </div>
                            <div className="text-xs text-black font-semibold">
                              {func.accountabilities?.length || 0}
                            </div>

                            {/* Context Menu for Function (List View) */}
                            {contextMenu?.id === func.id && (
                              <div
                                className="fixed bg-white border border-gray-200 rounded-lg shadow-xl z-50 min-w-[180px]"
                                style={{ left: contextMenu.x, top: contextMenu.y }}
                                onClick={(e) => e.stopPropagation()}
                              >
                                <div className="px-3 py-2 text-xs font-bold text-black uppercase border-b border-gray-100">
                                  Function
                                </div>
                                <button
                                  className="w-full px-4 py-2 text-sm text-left hover:bg-gray-50 flex items-center gap-2 text-black font-semibold"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setSelectedFunction(func);
                                    setShowAddAccountabilityModal(true);
                                    setContextMenu(null);
                                  }}
                                >
                                  <Plus size={14} className="text-black" />
                                  Add Accountability
                                </button>
                                <button
                                  className="w-full px-4 py-2 text-sm text-left hover:bg-gray-50 flex items-center gap-2 text-black font-semibold"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setContextMenu(null);
                                  }}
                                >
                                  <Edit size={14} className="text-black" />
                                  Edit Function
                                </button>
                                <button
                                  className="w-full px-4 py-2 text-sm text-left hover:bg-gray-50 flex items-center gap-2 text-black font-semibold"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setSelectedFunction(func);
                                    setShowMoveModal(true);
                                    setContextMenu(null);
                                  }}
                                >
                                  <Move size={14} className="text-black" />
                                  Move Function
                                </button>
                                <button
                                  className="w-full px-4 py-2 text-sm text-left hover:bg-red-50 flex items-center gap-2 text-red-600 font-semibold"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setContextMenu(null);
                                  }}
                                >
                                  <Trash2 size={14} className="text-red-600" />
                                  Delete Function
                                </button>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Add Accountability Button */}
                    <div className="mt-4 p-3 bg-gray-50 rounded-lg border border-gray-200">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => {
                            // Find first function in category to add accountability to
                            const firstFunc = filteredFunctions[0];
                            if (firstFunc) {
                              setSelectedFunction(firstFunc);
                              setShowAddAccountabilityModal(true);
                            }
                          }}
                          className="flex items-center gap-2 px-3 py-1.5 text-sm text-black hover:bg-gray-100 rounded-lg font-semibold"
                        >
                          <Plus size={14} className="text-black" />
                          Add accountability
                        </button>
                        <button className="flex items-center gap-2 px-3 py-1.5 text-sm text-purple-600 hover:bg-purple-50 rounded-lg font-semibold">
                          <Sparkles size={14} className="text-purple-600" />
                          Suggest
                        </button>
                      </div>
                    </div>
                  </>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Function Detail Panel - Slides in from right */}
      {showFunctionPanel && selectedFunction && (
        <div className="absolute right-0 top-0 bottom-0 z-20">
          <FunctionDetailPanel
            functionItem={selectedFunction}
            onClose={() => {
              setShowFunctionPanel(false);
              setSelectedFunction(null);
            }}
            onAddAccountability={(functionId) => {
              const func = categories
                .flatMap(cat => cat.functions || [])
                .find(f => f.id === functionId);
              if (func) {
                setSelectedFunction(func);
                setShowAddAccountabilityModal(true);
              }
            }}
            onEditAccountability={(accountability) => {
              setSelectedAccountability(accountability);
              setNewAccountability({
                objective: accountability.objective,
                accountability_code: accountability.accountability_code || ''
              });
              setShowEditAccountabilityModal(true);
            }}
            onDeleteAccountability={(accountabilityId) => {
              handleDeleteAccountability(accountabilityId);
            }}
          />
        </div>
      )}

      {/* Add Accountability Modal */}
      <AnimatePresence>
        {showAddAccountabilityModal && selectedFunction && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
            onClick={() => setShowAddAccountabilityModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            >
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center gap-3">
                  <Briefcase size={20} className="text-green-600" />
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">Add Accountability</h3>
                    <p className="text-sm text-gray-600 mt-1">Function: {selectedFunction.name}</p>
                  </div>
                </div>
              </div>

              <div className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Accountability ID (Optional)
                  </label>
                  <input
                    type="text"
                    value={newAccountability.accountability_code}
                    onChange={(e) => setNewAccountability({...newAccountability, accountability_code: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                    placeholder="Enter accountability ID"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Objective *
                  </label>
                  <textarea
                    value={newAccountability.objective}
                    onChange={(e) => setNewAccountability({...newAccountability, objective: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 min-h-[120px]"
                    placeholder="Describe the accountability objective..."
                  />
                </div>
              </div>

              <div className="p-6 border-t border-gray-200 flex items-center justify-end gap-3">
                <button
                  onClick={() => {
                    setShowAddAccountabilityModal(false);
                    setNewAccountability({ objective: '', accountability_code: '' });
                  }}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                >
                  Cancel
                </button>
                <button
                  onClick={handleAddAccountability}
                  disabled={createAccountabilityMutation.isPending || !newAccountability.objective.trim()}
                  className="px-4 py-2 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {createAccountabilityMutation.isPending ? 'Saving...' : 'Save Accountability'}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Edit Accountability Modal */}
      <AnimatePresence>
        {showEditAccountabilityModal && selectedAccountability && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
            onClick={() => setShowEditAccountabilityModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            >
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center gap-3">
                  <Briefcase size={20} className="text-green-600" />
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">Edit Accountability</h3>
                    <p className="text-sm text-gray-600 mt-1">Accountability</p>
                  </div>
                </div>
              </div>

              <div className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Accountability ID
                  </label>
                  <input
                    type="text"
                    value={newAccountability.accountability_code || ''}
                    onChange={(e) => setNewAccountability({...newAccountability, accountability_code: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                    placeholder="Enter accountability ID"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Objective *
                  </label>
                  <textarea
                    value={newAccountability.objective}
                    onChange={(e) => setNewAccountability({...newAccountability, objective: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 min-h-[120px]"
                    placeholder="Describe the accountability objective..."
                  />
                </div>
              </div>

              <div className="p-6 border-t border-gray-200 flex items-center justify-end gap-3">
                <button
                  onClick={() => {
                    setShowEditAccountabilityModal(false);
                    setSelectedAccountability(null);
                    setNewAccountability({ objective: '', accountability_code: '' });
                  }}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                >
                  Cancel
                </button>
                <button
                  onClick={handleEditAccountability}
                  disabled={updateAccountabilityMutation.isPending || !newAccountability.objective.trim()}
                  className="px-4 py-2 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {updateAccountabilityMutation.isPending ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Move Modal */}
      <MoveModal
        isOpen={showMoveModal}
        onClose={() => {
          setShowMoveModal(false);
          setSelectedAccountability(null);
          setSelectedFunction(null);
        }}
        onMove={(targetId) => {
          if (selectedAccountability) {
            handleMoveAccountability(targetId);
          } else if (selectedFunction) {
            handleMoveFunction(targetId);
          }
        }}
        itemType={selectedAccountability ? 'accountability' : 'function'}
        itemName={selectedAccountability?.objective || selectedFunction?.name || ''}
        categories={categories.map(cat => ({
          id: cat.id,
          name: cat.name,
          functions: (cat.functions || []).map(f => ({ id: f.id, name: f.name }))
        }))}
        currentCategoryId={selectedFunction ? categories.find(c => (c.functions || []).some(f => f.id === selectedFunction.id))?.id : undefined}
        currentFunctionId={selectedAccountability ? selectedFunction?.id : undefined}
      />
    </div>
  );
};

export default FunctionalChartView;
