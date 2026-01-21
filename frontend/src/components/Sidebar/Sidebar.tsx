import React, { useState } from 'react';
import {
  Grid, Users, BarChart3, PieChart, Plus,
  Search, Download, Menu, ChevronDown, ChevronRight,
  Briefcase, Database, Sparkles
} from 'lucide-react';

type ViewType = 'orgChart' | 'peoplePositions' | 'functionalChart' | 'forecastSheet' | 'changePlan' | 'hris' | 'aiGenerator';

interface SidebarProps {
  currentView: ViewType;
  onViewChange: (view: ViewType) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ currentView, onViewChange }) => {
  const [expandedSections, setExpandedSections] = useState({
    quickAdd: true,
    notInOrg: true,
    people: false,
    inOrg: true,
    standardRoles: true,
    functions: true
  });

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const views = [
    {
      id: 'orgChart' as ViewType,
      icon: Grid,
      name: 'Org chart',
      description: 'Edit positions by adding people...',
      isDefault: true,
      color: 'text-indigo-600'
    },
    {
      id: 'peoplePositions' as ViewType,
      icon: Users,
      name: 'People & positions',
      description: 'View and edit people and...',
      color: 'text-amber-600'
    },
    {
      id: 'functionalChart' as ViewType,
      icon: Grid,
      name: 'Functional chart',
      description: 'Edit roles and accountabilities in...',
      color: 'text-red-600'
    },
    {
      id: 'forecastSheet' as ViewType,
      icon: BarChart3,
      name: 'Forecast sheet',
      description: 'View and edit the forecast sheet',
      color: 'text-pink-600'
    },
    {
      id: 'changePlan' as ViewType,
      icon: PieChart,
      name: 'Change plan',
      description: 'Compare this scenario with...',
      color: 'text-amber-600'
    }
  ];

  return (
    <aside className="w-70 bg-white border-r border-gray-200 flex flex-col h-full mt-16">
      {/* Sidebar Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center gap-2 px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors">
          <Grid size={20} className="text-indigo-600" />
          <span className="text-sm font-medium">
            {currentView === 'orgChart' ? 'Org chart' : 
             currentView === 'peoplePositions' ? 'People & positions' :
             'Functional chart'}
          </span>
          <ChevronDown size={16} className="ml-auto text-gray-400" />
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-3 p-4 border-b border-gray-200">
        <button className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors flex-1">
          <Search size={16} />
          Related
        </button>
        <button className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors flex-1">
          <Download size={16} />
          Export
        </button>
      </div>

      {/* Views Section */}
      <div className="flex-1 overflow-y-auto">
        <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
          Views
        </div>
        
        {views.map((view) => {
          const Icon = view.icon;
          const isActive = currentView === view.id;
          
          return (
            <div
              key={view.id}
              onClick={() => onViewChange(view.id)}
              className={`mx-3 mb-1 px-3 py-2.5 rounded-lg cursor-pointer transition-colors ${
                isActive 
                  ? 'bg-indigo-50 text-indigo-600' 
                  : 'hover:bg-gray-50 text-gray-700'
              }`}
            >
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 flex items-center justify-center flex-shrink-0">
                  <Icon size={18} className={view.color} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <div className="text-sm font-medium">{view.name}</div>
                    {view.isDefault && (
                      <span className="px-2 py-0.5 bg-gray-200 text-gray-600 text-xs font-medium rounded">
                        Default
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-gray-500 truncate mt-0.5">
                    {view.description}
                  </div>
                </div>
              </div>
            </div>
          );
        })}

        <button className="mx-3 mt-2 flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 rounded-lg transition-colors">
          <Plus size={16} />
          Add a view
        </button>

        {/* Integration & AI Section */}
        <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider mt-4">
          Integration & AI
        </div>

        <div
          onClick={() => onViewChange('hris' as ViewType)}
          className={`mx-3 mb-1 px-3 py-2.5 rounded-lg cursor-pointer transition-colors ${
            currentView === 'hris'
              ? 'bg-green-50 text-green-600'
              : 'hover:bg-gray-50 text-gray-700'
          }`}
        >
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 flex items-center justify-center flex-shrink-0">
              <Database size={18} className="text-green-600" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium">HRIS Connections</div>
              <div className="text-xs text-gray-500 truncate mt-0.5">
                Connect and sync from SuccessFactors...
              </div>
            </div>
          </div>
        </div>

        <div
          onClick={() => onViewChange('aiGenerator' as ViewType)}
          className={`mx-3 mb-1 px-3 py-2.5 rounded-lg cursor-pointer transition-colors ${
            currentView === 'aiGenerator'
              ? 'bg-green-50 text-green-600'
              : 'hover:bg-gray-50 text-gray-700'
          }`}
        >
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 flex items-center justify-center flex-shrink-0">
              <Sparkles size={18} className="text-green-600" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium">AI Structure Generator</div>
              <div className="text-xs text-gray-500 truncate mt-0.5">
                Generate and recommend org structures...
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Scenario Explorer */}
      <div className="border-t border-gray-200 p-3">
        <div className="bg-indigo-600 text-white px-4 py-3 rounded-lg flex items-center gap-2 cursor-pointer hover:bg-indigo-700 transition-colors">
          <Menu size={18} />
          <span className="text-sm font-medium">Scenario explorer</span>
          <ChevronDown size={16} className="ml-auto" />
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
