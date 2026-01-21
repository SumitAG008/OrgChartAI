import React, { useState } from 'react';
import {
  LayoutGrid, Users, Grid3x3, BarChart3,
  GitCompare, Plus, ChevronDown, ChevronRight,
  Building2, DollarSign, Briefcase, MapPin,
  Globe, UserCircle
} from 'lucide-react';

interface LeftSidebarProps {
  selectedView: string;
  onViewChange: (view: string) => void;
}

const LeftSidebar: React.FC<LeftSidebarProps> = ({ selectedView, onViewChange }) => {
  const [expandedSections, setExpandedSections] = useState({
    views: true,
    quickAdd: true,
    notInChart: true,
    inChart: false,
    standardRoles: false,
    functions: false
  });

  const views = [
    { id: 'org-chart', label: 'Org chart', icon: LayoutGrid, description: 'Edit positions by adding people and roles in a...', default: true },
    { id: 'people-positions', label: 'People & positions', icon: Users, description: 'View and edit people and positions.' },
    { id: 'functional-chart', label: 'Functional chart', icon: Grid3x3, description: 'Edit roles and accountabilities in a functional chart.' },
    { id: 'forecast-sheet', label: 'Forecast sheet', icon: BarChart3, description: 'View and edit the forecast sheet.' },
    { id: 'change-plan', label: 'Change plan', icon: GitCompare, description: 'Compare this scenario with another to see...' },
    { id: 'hris', label: 'HRIS Connections', icon: Building2, description: 'Connect and sync data from SuccessFactors and other HRIS systems.' }
  ];

  const quickAddItems = [
    { label: 'Position', icon: UserCircle },
    { label: 'Role', icon: Briefcase },
    { label: 'Business Unit', icon: Building2 },
    { label: 'Cost Center', icon: DollarSign },
    { label: 'Department', icon: Building2 },
    { label: 'Division', icon: Building2 },
    { label: 'Region', icon: Globe }
  ];

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section as keyof typeof prev]
    }));
  };

  return (
    <div className="w-64 bg-white border-r border-gray-200 flex flex-col overflow-y-auto">
      {/* Views Section */}
      <div className="p-3 border-b border-gray-200">
        <div className="space-y-1">
          {views.map((view) => {
            const Icon = view.icon;
            const isSelected = selectedView === view.id;
            return (
              <button
                key={view.id}
                onClick={() => onViewChange(view.id)}
                className={`w-full flex items-start gap-3 p-2 rounded-lg text-left transition-colors ${
                  isSelected
                    ? 'bg-purple-50 border border-purple-200'
                    : 'hover:bg-gray-50'
                }`}
              >
                <Icon size={18} className={`mt-0.5 ${isSelected ? 'text-purple-600' : 'text-gray-500'}`} />
                <div className="flex-1 min-w-0">
                  <div className={`text-sm font-semibold ${isSelected ? 'text-purple-900' : 'text-black'}`}>
                    {view.label}
                    {view.default && <span className="ml-2 text-xs text-gray-600 font-medium">(Default)</span>}
                  </div>
                  <div className="text-xs text-gray-700 mt-0.5 line-clamp-1 font-medium">
                    {view.description}
                  </div>
                </div>
              </button>
            );
          })}
        </div>
        <button className="w-full mt-2 px-3 py-1.5 text-sm text-black hover:bg-gray-50 rounded-lg flex items-center gap-2 font-semibold">
          <Plus size={16} className="text-black" />
          Add a view
        </button>
      </div>

      {/* Scenario Explorer - Highlighted in Purple */}
      <div className="p-3 border-b border-gray-200 bg-purple-50">
        <button className="w-full flex items-center justify-between p-2 hover:bg-purple-100 rounded-lg">
          <div className="flex items-center gap-2">
            <MapPin size={18} className="text-purple-600" />
            <span className="text-sm font-semibold text-purple-900">Scenario explorer</span>
          </div>
          <ChevronDown size={16} className="text-purple-600" />
        </button>
      </div>

      {/* Quick Add Section */}
      <div className="p-3 border-b border-gray-200">
        <button
          onClick={() => toggleSection('quickAdd')}
          className="w-full flex items-center justify-between p-2 hover:bg-gray-50 rounded-lg"
        >
          <span className="text-sm font-semibold text-black">Quick add</span>
          {expandedSections.quickAdd ? (
            <ChevronDown size={16} className="text-black" />
          ) : (
            <ChevronRight size={16} className="text-black" />
          )}
        </button>
        {expandedSections.quickAdd && (
          <div className="grid grid-cols-2 gap-2 mt-2">
            {quickAddItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.label}
                  className="p-2 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-gray-300 flex flex-col items-center gap-1"
                >
                  <Icon size={20} className="text-black" />
                  <span className="text-xs text-black text-center font-semibold">{item.label}</span>
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* Not in org chart */}
      <div className="p-3 border-b border-gray-200">
        <button
          onClick={() => toggleSection('notInChart')}
          className="w-full flex items-center justify-between p-2 hover:bg-gray-50 rounded-lg"
        >
          <span className="text-sm font-semibold text-black">Not in org chart</span>
          {expandedSections.notInChart ? (
            <ChevronDown size={16} className="text-black" />
          ) : (
            <ChevronRight size={16} className="text-black" />
          )}
        </button>
        {expandedSections.notInChart && (
          <div className="mt-2">
            <button
              onClick={() => toggleSection('people')}
              className="w-full flex items-center justify-between p-2 hover:bg-gray-50 rounded-lg"
            >
              <span className="text-sm text-black font-semibold">People</span>
              <div className="flex items-center gap-2">
                <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-bold">
                  + 93
                </span>
                {expandedSections.people ? (
                  <ChevronDown size={14} className="text-black" />
                ) : (
                  <ChevronRight size={14} className="text-black" />
                )}
              </div>
            </button>
            {expandedSections.people && (
              <div className="mt-1 space-y-1 pl-4">
                {/* Sample people */}
                <div className="flex items-center gap-2 p-2 hover:bg-gray-50 rounded">
                  <div className="w-8 h-8 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center text-white text-xs font-semibold">
                    KG
                  </div>
                  <span className="text-sm text-black font-semibold">Kevan Garaghan</span>
                </div>
                <div className="flex items-center gap-2 p-2 hover:bg-gray-50 rounded">
                  <div className="w-8 h-8 bg-gradient-to-br from-green-400 to-green-600 rounded-full flex items-center justify-center text-white text-xs font-semibold">
                    GM
                  </div>
                  <span className="text-sm text-black font-semibold">Grover McGuire</span>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* In org chart */}
      <div className="p-3 border-b border-gray-200">
        <div className="flex items-center justify-between p-2">
          <span className="text-sm font-semibold text-black">In org chart</span>
          <select className="text-xs border border-gray-200 rounded px-2 py-1 text-black font-semibold bg-white">
            <option>Hierarchy</option>
          </select>
        </div>
      </div>

      {/* Standard roles */}
      <div className="p-3 border-b border-gray-200">
        <button
          onClick={() => toggleSection('standardRoles')}
          className="w-full flex items-center justify-between p-2 hover:bg-gray-50 rounded-lg"
        >
          <span className="text-sm font-semibold text-black">Standard roles</span>
          {expandedSections.standardRoles ? (
            <ChevronDown size={16} className="text-black" />
          ) : (
            <ChevronRight size={16} className="text-black" />
          )}
        </button>
      </div>

      {/* Functions & Accountabilities */}
      <div className="p-3">
        <button
          onClick={() => toggleSection('functions')}
          className="w-full flex items-center justify-between p-2 hover:bg-gray-50 rounded-lg"
        >
          <span className="text-sm font-semibold text-black">Functions & Accountabilities</span>
          {expandedSections.functions ? (
            <ChevronDown size={16} className="text-black" />
          ) : (
            <ChevronRight size={16} className="text-black" />
          )}
        </button>
      </div>
    </div>
  );
};

export default LeftSidebar;
