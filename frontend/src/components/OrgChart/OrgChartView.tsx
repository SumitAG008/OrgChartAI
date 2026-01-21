import React from 'react';
import OrgChartCanvas from './OrgChartCanvas';
import HRISConnectionManager from '../HRIS/HRISConnectionManager';
import AIOrgGenerator from '../AI/AIOrgGenerator';
import FunctionalChartView from '../FunctionalChart/FunctionalChartView';

type ViewType = 'orgChart' | 'peoplePositions' | 'functionalChart' | 'forecastSheet' | 'changePlan' | 'hris' | 'aiGenerator';

interface OrgChartViewProps {
  view: ViewType;
}

const OrgChartView: React.FC<OrgChartViewProps> = ({ view }) => {
  switch (view) {
    case 'orgChart':
      return <OrgChartCanvas />;
    case 'functionalChart':
      return <FunctionalChartView />;
    case 'hris':
      return (
        <div className="p-6 h-full overflow-y-auto">
          <HRISConnectionManager />
        </div>
      );
    case 'aiGenerator':
      return (
        <div className="p-6 h-full overflow-y-auto">
          <AIOrgGenerator />
        </div>
      );
    case 'peoplePositions':
    case 'forecastSheet':
    case 'changePlan':
      return (
        <div className="flex items-center justify-center h-full">
          <div className="text-center text-gray-500">
            <p className="text-lg">{view} view - Coming soon</p>
          </div>
        </div>
      );
    default:
      return <OrgChartCanvas />;
  }
};

export default OrgChartView;
