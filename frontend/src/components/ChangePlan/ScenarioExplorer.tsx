import React, { useState } from 'react';
import { ChevronRight, ChevronDown, User, Users, FileText, Building, X } from 'lucide-react';

interface Scenario {
  id: string;
  name: string;
  description?: string;
  status: 'Draft' | 'Active' | 'Archived';
  created_at: string;
  statistics?: {
    org_units_count: number;
    positions_count: number;
    employees_count: number;
    vacant_positions: number;
  };
}

interface ScenarioExplorerProps {
  scenarios: Scenario[];
  selectedScenarioId?: string;
  onScenarioSelect: (scenarioId: string) => void;
  onClose?: () => void;
}

const ScenarioExplorer: React.FC<ScenarioExplorerProps> = ({
  scenarios,
  selectedScenarioId,
  onScenarioSelect,
  onClose
}) => {
  const [expandedSections, setExpandedSections] = useState({
    scenarios: true,
    notInOrg: false,
    people: false,
    inOrg: false,
    standardRoles: true,
    functions: false
  });

  const [selectedRoles, setSelectedRoles] = useState<Set<string>>(new Set());

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const toggleRole = (roleId: string) => {
    setSelectedRoles(prev => {
      const next = new Set(prev);
      if (next.has(roleId)) {
        next.delete(roleId);
      } else {
        next.add(roleId);
      }
      return next;
    });
  };

  // Mock data for demonstration
  const standardRoles = {
    Customer: [
      'Customer Operations',
      'Customer Success Manager',
      'Customer Support Manager',
      'Head of Customer',
      'Onboarding Specialist',
      'Support Officer'
    ]
  };

  const currentScenario = scenarios.find(s => s.id === selectedScenarioId);

  return (
    <aside className="w-70 bg-white border-r border-gray-200 flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 bg-purple-50">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <FileText size={20} className="text-purple-600" />
            <h2 className="text-sm font-semibold text-purple-900">Scenario explorer</h2>
          </div>
          {onClose && (
            <button
              onClick={onClose}
              className="p-1 hover:bg-purple-100 rounded transition-colors"
            >
              <X size={16} className="text-gray-500" />
            </button>
          )}
        </div>
        {currentScenario && (
          <div className="text-xs text-gray-600 mt-1">
            {currentScenario.name} / current version
          </div>
        )}
      </div>

      {/* Scenarios Section */}
      <div className="flex-1 overflow-y-auto">
        {/* Not in org chart */}
        <div className="border-b border-gray-200">
          <button
            onClick={() => toggleSection('notInOrg')}
            className="w-full flex items-center justify-between px-4 py-2 hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center gap-2">
              {expandedSections.notInOrg ? (
                <ChevronDown size={16} className="text-gray-400" />
              ) : (
                <ChevronRight size={16} className="text-gray-400" />
              )}
              <User size={16} className="text-gray-500" />
              <span className="text-sm text-gray-700">Not in org chart</span>
            </div>
            <span className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full">
              93
            </span>
          </button>
        </div>

        {/* People */}
        <div className="border-b border-gray-200">
          <button
            onClick={() => toggleSection('people')}
            className="w-full flex items-center justify-between px-4 py-2 hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center gap-2">
              {expandedSections.people ? (
                <ChevronDown size={16} className="text-gray-400" />
              ) : (
                <ChevronRight size={16} className="text-gray-400" />
              )}
              <Users size={16} className="text-gray-500" />
              <span className="text-sm text-gray-700">People</span>
            </div>
            <span className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full">
              +93
            </span>
          </button>
        </div>

        {/* In org chart */}
        <div className="border-b border-gray-200">
          <button
            onClick={() => toggleSection('inOrg')}
            className="w-full flex items-center justify-between px-4 py-2 hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center gap-2">
              {expandedSections.inOrg ? (
                <ChevronDown size={16} className="text-gray-400" />
              ) : (
                <ChevronRight size={16} className="text-gray-400" />
              )}
              <User size={16} className="text-gray-500" />
              <span className="text-sm text-gray-700">In org chart</span>
            </div>
            <span className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full">
              10
            </span>
          </button>
        </div>

        {/* Standard roles */}
        <div className="border-b border-gray-200">
          <button
            onClick={() => toggleSection('standardRoles')}
            className="w-full flex items-center justify-between px-4 py-2 hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center gap-2">
              {expandedSections.standardRoles ? (
                <ChevronDown size={16} className="text-gray-400" />
              ) : (
                <ChevronRight size={16} className="text-gray-400" />
              )}
              <FileText size={16} className="text-gray-500" />
              <span className="text-sm text-gray-700">Standard roles</span>
            </div>
          </button>
          
          {expandedSections.standardRoles && (
            <div className="bg-gray-50">
              {Object.entries(standardRoles).map(([category, roles]) => (
                <div key={category} className="px-4 py-2">
                  <div className="flex items-center gap-2 mb-2">
                    <ChevronRight size={14} className="text-gray-400" />
                    <span className="text-xs font-medium text-gray-600">{category}</span>
                  </div>
                  <div className="ml-6 space-y-1">
                    {roles.map((role, idx) => (
                      <label
                        key={idx}
                        className="flex items-center gap-2 px-2 py-1 hover:bg-white rounded cursor-pointer group"
                      >
                        <input
                          type="checkbox"
                          checked={selectedRoles.has(`${category}-${role}`)}
                          onChange={() => toggleRole(`${category}-${role}`)}
                          className="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                        />
                        <span className="text-xs text-gray-700 group-hover:text-gray-900">
                          {role}
                        </span>
                      </label>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Functions & Accountabilities */}
        <div className="border-b border-gray-200">
          <button
            onClick={() => toggleSection('functions')}
            className="w-full flex items-center justify-between px-4 py-2 hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center gap-2">
              {expandedSections.functions ? (
                <ChevronDown size={16} className="text-gray-400" />
              ) : (
                <ChevronRight size={16} className="text-gray-400" />
              )}
              <Building size={16} className="text-gray-500" />
              <span className="text-sm text-gray-700">Functions & Accountabilities</span>
            </div>
          </button>
        </div>
      </div>
    </aside>
  );
};

export default ScenarioExplorer;
