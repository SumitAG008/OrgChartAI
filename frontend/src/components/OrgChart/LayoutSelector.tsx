import React, { useState } from 'react';
import { ORG_STRUCTURE_TYPES, OrgStructureType, STRUCTURE_CATEGORIES } from '../../types/orgStructures';
import { ChevronDown, Search, Check } from 'lucide-react';

interface LayoutSelectorProps {
  currentLayout: OrgStructureType;
  onLayoutChange: (layout: OrgStructureType) => void;
}

const LayoutSelector: React.FC<LayoutSelectorProps> = ({ currentLayout, onLayoutChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');

  const currentConfig = ORG_STRUCTURE_TYPES[currentLayout];

  const filteredStructures = Object.values(ORG_STRUCTURE_TYPES).filter(structure => {
    const matchesSearch = structure.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          structure.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'All' || structure.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const groupedByCategory = STRUCTURE_CATEGORIES.reduce((acc, category) => {
    acc[category] = filteredStructures.filter(s => s.category === category);
    return acc;
  }, {} as Record<string, typeof filteredStructures>);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg shadow-sm hover:bg-gray-50 transition-all duration-200 hover:shadow-md"
      >
        <span className="text-2xl">{currentConfig.icon}</span>
        <div className="text-left">
          <div className="text-sm font-medium text-gray-900">{currentConfig.name}</div>
          <div className="text-xs text-gray-500">{currentConfig.category}</div>
        </div>
        <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <>
          <div 
            className="fixed inset-0 z-40" 
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute top-full left-0 mt-2 w-96 bg-white rounded-xl shadow-2xl border border-gray-200 z-50 overflow-hidden">
            {/* Search and Filter */}
            <div className="p-4 border-b border-gray-200 bg-gradient-to-r from-green-50 to-emerald-50">
              <div className="relative mb-3">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search structures..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>
              <div className="flex gap-2 flex-wrap">
                <button
                  onClick={() => setSelectedCategory('All')}
                  className={`px-3 py-1 text-xs rounded-full transition-all ${
                    selectedCategory === 'All'
                      ? 'bg-gradient-to-r from-green-600 to-emerald-600 text-white shadow-md shadow-green-500/30'
                      : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
                  }`}
                >
                  All
                </button>
                {STRUCTURE_CATEGORIES.map(category => (
                  <button
                    key={category}
                    onClick={() => setSelectedCategory(category)}
                    className={`px-3 py-1 text-xs rounded-full transition-all ${
                      selectedCategory === category
                        ? 'bg-gradient-to-r from-green-600 to-emerald-600 text-white shadow-md shadow-green-500/30'
                        : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
                    }`}
                  >
                    {category}
                  </button>
                ))}
              </div>
            </div>

            {/* Structure List */}
            <div className="max-h-96 overflow-y-auto">
              {STRUCTURE_CATEGORIES.map(category => {
                const structures = groupedByCategory[category];
                if (structures.length === 0) return null;

                return (
                  <div key={category} className="border-b border-gray-100 last:border-b-0">
                    <div className="px-4 py-2 bg-gray-50 text-xs font-semibold text-gray-600 uppercase tracking-wide">
                      {category}
                    </div>
                    {structures.map(structure => (
                      <button
                        key={structure.id}
                        onClick={() => {
                          onLayoutChange(structure.id);
                          setIsOpen(false);
                        }}
                        className={`w-full px-4 py-3 flex items-start gap-3 hover:bg-green-50 transition-all duration-150 ${
                          currentLayout === structure.id ? 'bg-green-50 border-l-4 border-green-600' : ''
                        }`}
                      >
                        <span className="text-2xl mt-0.5">{structure.icon}</span>
                        <div className="flex-1 text-left">
                          <div className="flex items-center gap-2">
                            <span className="font-medium text-gray-900">{structure.name}</span>
                            {currentLayout === structure.id && (
                              <Check className="w-4 h-4 text-green-600" />
                            )}
                          </div>
                          <div className="text-xs text-gray-500 mt-0.5">{structure.description}</div>
                          <div className="flex gap-1 mt-1.5">
                            {structure.features.slice(0, 3).map((feature, idx) => (
                              <span
                                key={idx}
                                className="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded-full"
                              >
                                {feature}
                              </span>
                            ))}
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                );
              })}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default LayoutSelector;
