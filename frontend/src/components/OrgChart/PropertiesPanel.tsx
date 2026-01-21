import React, { useState } from 'react';
import { ChevronRight, User, Briefcase, Users, DollarSign, Calendar, Hash, Percent, MessageSquare } from 'lucide-react';

export interface DisplayProperties {
  // Person properties
  personPhoto: boolean;
  personName: boolean;
  
  // Position properties
  title: boolean;
  description: boolean;
  positionId: boolean;
  fte: boolean;
  vacancyStatus: boolean;
  totalCompensation: boolean;
  
  // Group properties
  groupDescription: boolean;
  
  // Other properties
  comments: boolean;
  roleEffortPercent: boolean;
}

interface PropertiesPanelProps {
  properties: DisplayProperties;
  onPropertiesChange: (properties: DisplayProperties) => void;
  onClose?: () => void;
}

const PropertiesPanel: React.FC<PropertiesPanelProps> = ({ properties, onPropertiesChange, onClose }) => {
  const [expandedSections, setExpandedSections] = useState({
    displayed: true,
    calculations: false
  });

  const toggleProperty = (key: keyof DisplayProperties) => {
    onPropertiesChange({
      ...properties,
      [key]: !properties[key]
    });
  };

  const toggleSection = (section: 'displayed' | 'calculations') => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  return (
    <div className="w-80 bg-white border-l border-gray-200 flex flex-col h-full shadow-lg">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 flex items-center justify-between">
        <h2 className="text-lg font-bold text-black">Properties</h2>
        {onClose && (
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded">
            <span className="text-black font-bold">×</span>
          </button>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {/* Displayed properties */}
        <div className="mb-6">
          <button
            onClick={() => toggleSection('displayed')}
            className="w-full flex items-center justify-between p-2 hover:bg-gray-50 rounded-lg mb-2"
          >
            <span className="text-sm font-bold text-black">Displayed properties</span>
            <ChevronRight 
              size={16} 
              className={`text-black transition-transform ${expandedSections.displayed ? 'rotate-90' : ''}`} 
            />
          </button>

          {expandedSections.displayed && (
            <div className="space-y-4 pl-2">
              {/* Person Section */}
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <User size={16} className="text-black" />
                  <span className="text-xs font-bold text-black uppercase">Person</span>
                </div>
                <div className="space-y-2">
                  <PropertyToggle
                    label="Person photo"
                    checked={properties.personPhoto}
                    onChange={() => toggleProperty('personPhoto')}
                  />
                  <PropertyToggle
                    label="Person name"
                    checked={properties.personName}
                    onChange={() => toggleProperty('personName')}
                  />
                </div>
              </div>

              {/* Positions Section */}
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Briefcase size={16} className="text-black" />
                  <span className="text-xs font-bold text-black uppercase">Positions</span>
                </div>
                <div className="space-y-2">
                  <PropertyToggle
                    label="Title"
                    checked={properties.title}
                    onChange={() => toggleProperty('title')}
                  />
                  <PropertyToggle
                    label="Description"
                    checked={properties.description}
                    onChange={() => toggleProperty('description')}
                  />
                  <PropertyToggle
                    label="# Position Id"
                    checked={properties.positionId}
                    onChange={() => toggleProperty('positionId')}
                    icon={<Hash size={14} className="text-black" />}
                  />
                  <PropertyToggle
                    label="Full time equivalent (Effort)"
                    checked={properties.fte}
                    onChange={() => toggleProperty('fte')}
                    icon={<Percent size={14} className="text-black" />}
                  />
                  <PropertyToggle
                    label="Vacancy status"
                    checked={properties.vacancyStatus}
                    onChange={() => toggleProperty('vacancyStatus')}
                  />
                  <PropertyToggle
                    label="$ Total compensation"
                    checked={properties.totalCompensation}
                    onChange={() => toggleProperty('totalCompensation')}
                    icon={<DollarSign size={14} className="text-black" />}
                  />
                  <button className="w-full text-left px-3 py-2 text-sm text-blue-600 hover:bg-blue-50 rounded-lg font-semibold">
                    + Add a property
                  </button>
                </div>
              </div>

              {/* Groups Section */}
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Users size={16} className="text-black" />
                  <span className="text-xs font-bold text-black uppercase">Groups</span>
                </div>
                <div className="space-y-2">
                  <PropertyToggle
                    label="Description"
                    checked={properties.groupDescription}
                    onChange={() => toggleProperty('groupDescription')}
                  />
                </div>
              </div>

              {/* Other Section */}
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <MessageSquare size={16} className="text-black" />
                  <span className="text-xs font-bold text-black uppercase">Other</span>
                </div>
                <div className="space-y-2">
                  <PropertyToggle
                    label="Comments"
                    checked={properties.comments}
                    onChange={() => toggleProperty('comments')}
                  />
                  <PropertyToggle
                    label="Role effort %"
                    checked={properties.roleEffortPercent}
                    onChange={() => toggleProperty('roleEffortPercent')}
                    icon={<Percent size={14} className="text-black" />}
                  />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Group calculations */}
        <div>
          <button
            onClick={() => toggleSection('calculations')}
            className="w-full flex items-center justify-between p-2 hover:bg-gray-50 rounded-lg mb-2"
          >
            <span className="text-sm font-bold text-black">Group calculations</span>
            <ChevronRight 
              size={16} 
              className={`text-black transition-transform ${expandedSections.calculations ? 'rotate-90' : ''}`} 
            />
          </button>

          {expandedSections.calculations && (
            <div className="pl-2 space-y-2">
              <div className="text-xs text-gray-600 font-semibold">
                Calculation options will appear here
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

interface PropertyToggleProps {
  label: string;
  checked: boolean;
  onChange: () => void;
  icon?: React.ReactNode;
}

const PropertyToggle: React.FC<PropertyToggleProps> = ({ label, checked, onChange, icon }) => {
  return (
    <div className="flex items-center justify-between p-2 hover:bg-gray-50 rounded-lg">
      <div className="flex items-center gap-2 flex-1">
        {icon && <span className="text-gray-500">{icon}</span>}
        <span className="text-sm text-black font-semibold">{label}</span>
      </div>
      <button
        onClick={onChange}
        className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${
          checked ? 'bg-green-500' : 'bg-gray-300'
        }`}
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
            checked ? 'translate-x-5' : 'translate-x-1'
          }`}
        />
      </button>
    </div>
  );
};

export default PropertiesPanel;
