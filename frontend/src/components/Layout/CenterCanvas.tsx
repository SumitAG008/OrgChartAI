import React, { useState } from 'react';
import { LayoutGrid, Filter, Layers, Layout, MoreVertical, ChevronDown } from 'lucide-react';
import OrgChartCanvas from '../OrgChart/OrgChartCanvas';
import ForecastSheetView from '../Forecast/ForecastSheetView';
import FunctionalChartView from '../FunctionalChart/FunctionalChartView';
import PeoplePositionsView from '../OrgChart/PeoplePositionsView';
import ChangePlanView from '../OrgChart/ChangePlanView';
import HRISConnectionManager from '../HRIS/HRISConnectionManager';
import PropertiesPanel, { DisplayProperties } from '../OrgChart/PropertiesPanel';

interface CenterCanvasProps {
  view: string;
  onPositionSelect: (position: any) => void;
}

const CenterCanvas: React.FC<CenterCanvasProps> = ({ view, onPositionSelect }) => {
  const [filter, setFilter] = useState('Top item');
  const [layers, setLayers] = useState(2);
  const [layout, setLayout] = useState('Narrow');
  const [showProperties, setShowProperties] = useState(false);
  const [displayProperties, setDisplayProperties] = useState<DisplayProperties>({
    personPhoto: true,
    personName: true,
    title: true,
    description: false,
    positionId: false,
    fte: false,
    vacancyStatus: false,
    totalCompensation: false,
    groupDescription: false,
    comments: true,
    roleEffortPercent: true,
  });

  const renderView = () => {
    switch (view) {
      case 'org-chart':
        return (
          <div className="h-full">
            <OrgChartCanvas displayProperties={displayProperties} />
          </div>
        );
      case 'people-positions':
        return <PeoplePositionsView />;
      case 'functional-chart':
        return <FunctionalChartView />;
      case 'forecast-sheet':
        return <ForecastSheetView />;
      case 'change-plan':
        return <ChangePlanView />;
      case 'hris':
        return (
          <div className="h-full overflow-y-auto">
            <HRISConnectionManager />
          </div>
        );
      default:
        return (
          <div className="h-full">
            <OrgChartCanvas />
          </div>
        );
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* View Controls Bar */}
      <div className="bg-white border-b border-gray-200 px-4 py-2 flex items-center gap-4">
        {/* View Selector */}
        <div className="flex items-center gap-2">
          <div className="relative">
            <button className="px-3 py-1.5 bg-purple-50 text-purple-700 font-medium rounded-lg flex items-center gap-2 hover:bg-purple-100">
              <LayoutGrid size={16} />
              Org chart
              <ChevronDown size={14} />
            </button>
            {/* Dropdown menu would go here */}
          </div>
          <button 
            onClick={() => setShowProperties(!showProperties)}
            className={`px-3 py-1.5 rounded-lg font-semibold ${
              showProperties 
                ? 'bg-blue-100 text-blue-700 border border-blue-300' 
                : 'text-black hover:bg-gray-100'
            }`}
          >
            Properties
          </button>
        </div>

        {/* Filters and Controls */}
        <div className="flex items-center gap-2 ml-auto">
          <div className="flex items-center gap-2">
            <Filter size={16} className="text-black" />
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="text-sm border border-gray-200 rounded px-2 py-1 text-black font-semibold bg-white"
            >
              <option>Top item</option>
              <option>All items</option>
              <option>Active only</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <Layers size={16} className="text-black" />
            <select
              value={layers}
              onChange={(e) => setLayers(Number(e.target.value))}
              className="text-sm border border-gray-200 rounded px-2 py-1 text-black font-semibold bg-white"
            >
              <option value={1}>1 below</option>
              <option value={2}>2 below</option>
              <option value={3}>3 below</option>
              <option value={4}>4 below</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <Layout size={16} className="text-black" />
            <select
              value={layout}
              onChange={(e) => setLayout(e.target.value)}
              className="text-sm border border-gray-200 rounded px-2 py-1 text-black font-semibold bg-white"
            >
              <option>Narrow</option>
              <option>Wide</option>
              <option>Compact</option>
            </select>
          </div>

          <button className="p-1.5 hover:bg-gray-100 rounded">
            <MoreVertical size={16} className="text-black" />
          </button>
        </div>
      </div>

      {/* Main Canvas Area */}
      <div className="flex-1 overflow-auto relative flex">
        <div className={`flex-1 transition-all duration-300 ${showProperties ? 'mr-80' : ''}`}>
          {renderView()}
        </div>
        
        {/* Properties Panel - Slides in from right */}
        {showProperties && view === 'org-chart' && (
          <div className="absolute right-0 top-0 bottom-0 z-20">
            <PropertiesPanel
              properties={displayProperties}
              onPropertiesChange={setDisplayProperties}
              onClose={() => setShowProperties(false)}
            />
          </div>
        )}
      </div>

      {/* Zoom Controls (Bottom Right) */}
      <div className="absolute bottom-4 right-4 flex flex-col gap-2 bg-white rounded-lg shadow-lg border border-gray-200 p-1 z-10">
        <button className="p-2 hover:bg-gray-100 rounded" title="Zoom In">
          <span className="text-lg font-bold text-black">+</span>
        </button>
        <button className="p-2 hover:bg-gray-100 rounded" title="Zoom Out">
          <span className="text-lg font-bold text-black">−</span>
        </button>
        <button className="p-2 hover:bg-gray-100 rounded" title="Fit to Screen">
          <span className="text-xs text-black font-bold">⤢</span>
        </button>
        <button className="p-2 hover:bg-gray-100 rounded" title="Full Screen">
          <span className="text-xs text-black font-bold">⛶</span>
        </button>
      </div>
    </div>
  );
};

export default CenterCanvas;
